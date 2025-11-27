from fastapi.responses import JSONResponse

import os
from typing import Optional, List, Dict, Any
from uuid import UUID
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Header, HTTPException, status, Request
from pydantic import BaseModel, Field
import httpx
from datetime import datetime

load_dotenv()


SUPABASE_URL = os.getenv("SUPABASE_URL", "") 
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "") 
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") 
TABLE = os.getenv("TABLE_NEWS", "news")


POSTGREST_URL = f"{SUPABASE_URL}/rest/v1"
AUTH_USER_ENDPOINT = f"{SUPABASE_URL}/auth/v1/user"



if not SUPABASE_SERVICE_ROLE_KEY:
   
    print("Warning: SUPABASE_SERVICE_ROLE_KEY não configurado. Recomenda-se configurar para operações server-side seguras.")

app = FastAPI(title="News API (FastAPI + Supabase)")

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security

security = HTTPBearer()



class NewsCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=160)
    content: str
    
    author_id: Optional[UUID] = None

class NewsUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=160)
    content: Optional[str] = None

class NewsOut(BaseModel):
    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: Optional[str]
    updated_at: Optional[str]


def service_headers() -> Dict[str, str]:
    """Headers usando service role (server-side)."""
    key = SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Prefer": "return=representation",
    }

def anon_headers_with_token(user_token: str) -> Dict[str, str]:
    if user_token.lower().startswith("bearer "):
        token_only = user_token.split(" ", 1)[1]
    else:
        token_only = user_token
        
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {token_only}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }



async def verify_token_and_get_user(
    auth: HTTPAuthorizationCredentials = Security(security),
) -> Dict[str, Any]:

    # Token puro, só o JWT
    token = auth.credentials
    authorization = f"Bearer {token}"  

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(
                AUTH_USER_ENDPOINT,
                headers=anon_headers_with_token(authorization)
            )
        except httpx.RequestError:
            raise HTTPException(status_code=500, detail="Failed to contact auth server")

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user = resp.json()

    if not user or not user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user data from auth server"
        )

    return user



@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
   
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/news", response_model=List[NewsOut])
async def list_news(
    user=Depends(verify_token_and_get_user),
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
):
    
    params = {
        "select": "*",
        "limit": str(min(limit, 100)),
        "offset": str(max(offset, 0)),
        "order": "created_at.desc",
        "author_id": f"eq.{user['id']}"
    }
    if search:
       
        params["title"] = f"ilike.*{search}*"
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{POSTGREST_URL}/{TABLE}", headers=service_headers(), params=params)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()

@app.get("/news/{news_id}", response_model=NewsOut)
async def get_news(news_id: UUID, user=Depends(verify_token_and_get_user)):
    params = {"select": "*", "id": f"eq.{news_id}"}
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{POSTGREST_URL}/{TABLE}", headers=service_headers(), params=params)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    data = r.json()
    if not data:
        raise HTTPException(status_code=404, detail="News not found")
    item = data[0] if isinstance(data, list) else data
    if str(item.get("author_id")) != str(user["id"]):
        raise HTTPException(status_code=403, detail="Not allowed")
    return item

@app.post("/news", response_model=NewsOut, status_code=201)
async def create_news(payload: NewsCreate, user=Depends(verify_token_and_get_user)):
    
    payload_data = payload.model_dump()
    payload_data["author_id"] = str(user["id"])
    payload_data["created_at"] = datetime.utcnow().isoformat()
    payload_data["updated_at"] = datetime.utcnow().isoformat()
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{POSTGREST_URL}/{TABLE}", headers=service_headers(), json=payload_data)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    created = r.json()
    
    return created[0] if isinstance(created, list) else created

@app.put("/news/{news_id}", response_model=NewsOut)
async def update_news(news_id: UUID, payload: NewsUpdate, user=Depends(verify_token_and_get_user)):
    
    async with httpx.AsyncClient(timeout=10) as client:
        fetch = await client.get(f"{POSTGREST_URL}/{TABLE}", headers=service_headers(), params={"select": "author_id", "id": f"eq.{news_id}"})
    if fetch.status_code >= 400:
        raise HTTPException(status_code=fetch.status_code, detail=fetch.text)
    fdata = fetch.json()
    if not fdata:
        raise HTTPException(status_code=404, detail="News not found")
    if str(fdata[0].get("author_id")) != str(user["id"]):
        raise HTTPException(status_code=403, detail="Not allowed")
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    data["updated_at"] = datetime.utcnow().isoformat()
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.patch(f"{POSTGREST_URL}/{TABLE}", headers=service_headers(), params={"id": f"eq.{news_id}"}, json=data)
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    updated = r.json()
    return updated[0] if isinstance(updated, list) else updated

@app.delete("/news/{news_id}", status_code=204)
async def delete_news(news_id: UUID, user=Depends(verify_token_and_get_user)):
    
    async with httpx.AsyncClient(timeout=10) as client:
        fetch = await client.get(f"{POSTGREST_URL}/{TABLE}", headers=service_headers(), params={"select": "author_id", "id": f"eq.{news_id}"})
    if fetch.status_code >= 400:
        raise HTTPException(status_code=fetch.status_code, detail=fetch.text)
    fdata = fetch.json()
    if not fdata:
        raise HTTPException(status_code=404, detail="News not found")
    if str(fdata[0].get("author_id")) != str(user["id"]):
        raise HTTPException(status_code=403, detail="Not allowed")
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.delete(f"{POSTGREST_URL}/{TABLE}", headers=service_headers(), params={"id": f"eq.{news_id}"})
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return {}
@app.post("/login")
async def login(data: dict):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers={"apikey": SUPABASE_ANON_KEY, "Content-Type": "application/json"},
            json={
                "email": data["email"],
                "password": data["password"]
            }
        )
    return r.json()