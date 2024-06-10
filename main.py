import redis.asyncio as redis
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware


from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0,
                                     password=config.REDIS_PASSWORD, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)
    app.state.redis_client = redis_client
    yield
    await redis_client.close()

app = FastAPI(lifespan=lifespan)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")


@app.get("/")
def index():
    return {"message": "Contact Application"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        # Make request
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")







