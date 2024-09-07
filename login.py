from fastapi import FastAPI, Depends, HTTPException, Form, HTTPException
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm import Session
from database import engine, get_db
from models import User     
from schemas import LoginDetails, UserCreate
from sqladmin.models import Base
from sqlalchemy import select
from pydantic import EmailStr

app = FastAPI()

# Define a login route
@app.post("/admin/products/")
# @app.post('/login' ,response_model=schemas.TokenSchema)
def login(request: LoginDetails, session: Session = Depends(get_db)):
    user = session.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email")
    user_id = user.id
    if request.username != user.username:
        raise HTTPException(status_code=404, detail="Incorrect password")

    return user_id