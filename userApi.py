
from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import Base, engine, get_db     
from schemas import UserCreate
from models import User , create_tables, get_user_table
from starlette.middleware.sessions import SessionMiddleware
from sqladmin import Admin, ModelView


create_tables(["users"])
app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key="qwerty")  

# class UserAdmin(ModelView, model=User):
#     column_list = [User.id, User.username, User.email, User.role] 

# admin = Admin(app, engine)
# admin.add_view(UserAdmin)  

@app.get("/")
def root():
    return {"message": "Welcome to the Admin Panel"}

@app.post("/admin/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_db)):  

    userdb = User(username=user.username, email=user.email, role=user.role)
    session.add(userdb)
    session.commit()

    session.refresh(userdb)
    id = userdb.id  
    product_table = get_user_table(id)
    # product_table.__table__.create(bind=engine)
    # Base.metadata.create_all(bind=engine, tables=[product_table])

    session.close()
    return {"message": f"Created user with id {id}"}

@app.get("/admin/users/", response_model=List[UserCreate])
def read_user_list(session: Session = Depends(get_db)):
    
    user_list = session.query(User).all()
    session.close()
    user_list_pydantic = [UserCreate.from_orm(user) for user in user_list]
    return user_list_pydantic

@app.put("/admin/users/{user_id}")
def update_user(user_id: int, user: UserCreate, session: Session = Depends(get_db)):    
    user_data = session.query(User).get(user_id)
    
    if user_data:
        user_data.username = user.username
        user_data.email = user.email
        user_data.role = user.role
        session.commit()
        return {"message": f"Updated user with id {user_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, session : Session = Depends(get_db)):
    
    user_data = session.query(User).get(user_id)

    if user_data:
        session.delete(user_data)
        session.commit()
        session.close()
        return {"message": f"Deleted user with id {user_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"user with id {id} not found")

    




