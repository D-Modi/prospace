
from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import MetaData, Table
from typing import List
from database import engine, get_db     
from schemas import ProductCreate, UserCreate, LoginDetails
from models import User , Product, create_tables, create_user_table

create_tables(["users"])
app = FastAPI()
token = None
produts_table_name = None

@app.get("/")
def root():
    return {"message": "Welcome to the Admin Panel"}

@app.post("/admin/products/")
# @app.post('/login' ,response_model=schemas.TokenSchema)
def login(request: LoginDetails, session: Session = Depends(get_db)):
    user = session.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect email")
    user_id = user.id
    if request.username != user.username:
        raise HTTPException(status_code=404, detail="Incorrect username")
    token = user_id 
    products_table_name = f'products_{user_id}'
    return {"message": f"Login Successful, token: {token}"}


@app.post("/admin/products/", status_code=status.HTTP_201_CREATED)
def create_products(user_id: int, product: ProductCreate, session: Session = Depends(get_db)):  

    metadata = MetaData(bind=engine)
    table_name = f'products_{user_id}'
    product_table = Table(table_name, metadata, autoload_with=engine)

    # add it to the session and commit it
    session.add(userdb)
    session.commit()

    # grab the id given to the object from the database
    session.refresh(userdb)
    id = userdb.id
    session.close()
    return {"message": f"Created user with id {id}"}

@app.get("/admin/products/", response_model=List[ProductCreate])
def read_product_list(user_id: int, session: Session = Depends(get_db)):

    metadata = MetaData(bind=engine)
    table_name = f'products_{user_id}'
    product_table = Table(table_name, metadata, autoload_with=engine)
    query = session.query(product_table).all()
    product_list_pydantic = [ProductCreate.from_orm(product) for product in query]

    session.close()
    
    # Return the queried products
    return product_list_pydantic


@app.get("/")
def root():
    return {"message": "Welcome to the Admin Panel"}

@app.post("/admin/users/", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_db)):  

    # create an instance of the User database model
    userdb = User(username=user.username, email=user.email, role=user.role)

    # add it to the session and commit it
    session.add(userdb)
    session.commit()

    # grab the id given to the object from the database
    session.refresh(userdb)
    id = userdb.id  
    create_user_table(id)
    session.close()
    return {"message": f"Created user with id {id}"}

@app.get("/admin/users/", response_model=List[UserCreate])
def read_user_list(session: Session = Depends(get_db)):
    # Get the user list
    user_list = session.query(User).all()
    session.close()
    
    # Convert SQLAlchemy objects to Pydantic models
    user_list_pydantic = [UserCreate.from_orm(user) for user in user_list]
    
    # Return the list of users
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
        # Raise a 404 error if the user is not found
        raise HTTPException(status_code=404, detail=f"User with id {id} not found")

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, session : Session = Depends(get_db)):
    # get user with the given id
    user_data = session.query(User).get(user_id)

    # if user with given id exists, delete it from the database. Otherwise raise 404 error
    if user_data:
        session.delete(user_data)
        session.commit()
        session.close()
        return {"message": f"Deleted user with id {user_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"user with id {id} not found")

    




