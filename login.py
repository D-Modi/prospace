from fastapi import FastAPI, Depends, HTTPException
from sqladmin import Admin, ModelView
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from database import Base, engine, get_db
from sqlalchemy.orm import Session
from models import User
from fastapi.responses import RedirectResponse

app = FastAPI()
admin = Admin(app, engine)

class IntegerInput(BaseModel):
    input_id: int

# Endpoint to handle integer input
@app.post("/admin/products")
def handle_integer_input(integer_input: IntegerInput, session: Session = Depends(get_db)):
    id = integer_input.input_id
    user = session.query(User).filter(User.id == id).first()
    
    if user:
        return {"message": f"{id} present"}
        # return RedirectResponse(url=f"/admin/products/{id}", status_code=302)

    else:
        raise HTTPException(status_code=404, detail="User not found")