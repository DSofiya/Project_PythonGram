from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes import images, auth, users, comments, transform

app = FastAPI()

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
app.include_router(images.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(transform.router, prefix="/api")


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Endpoint to check the health of the FastAPI application and the database.

    :param db: The active AsyncSession to perform the database health check.
    :type db: AsyncSession
    :return: A dictionary containing a welcome message if the database is configured correctly.
    :rtype: dict
    :raises HTTPException 500: If there is an error connecting to the database
        or if the database is not configured correctly.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
