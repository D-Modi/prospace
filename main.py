
from fastapi import FastAPI, status, Depends, HTTPException, Cookie, Response
from sqlalchemy.orm import Session, sessionmaker
from typing import List
from sqlalchemy import MetaData, Table, insert, update, delete
from sqladmin import Admin, ModelView
from starlette.middleware.sessions import SessionMiddleware
from database import engine, get_db     
from schemas import UserCreate, IntegerInput, ProductCreate
from models import User, get_user_table, create_tables, Product

create_tables(["users"])
app = FastAPI()

#gets the product table for a given user_id
def get_product_table(user_id: int):
    metadata = MetaData()
    table_name = f'products_{user_id}'
    
    table_user_id = Table(
        table_name, 
        metadata, 
        autoload_with=engine,  
    )
    
    return table_user_id

# app.add_middleware(SessionMiddleware, secret_key="qwerty")  

# class UserAdmin(ModelView, model=User):
#     column_list = [User.id, User.username, User.email, User.role] 

# admin = Admin(app, engine)
# admin.add_view(UserAdmin) 

# admin = Admin(app, engine, sessionmaker(bind=engine))

# # Define the admin views
# class UserAdmin(ModelView, model=User):
#     column_list = ['id', 'username', 'email', 'role']
#     form_columns = ['username', 'email', 'role']

# class ProductAdmin(ModelView, model=Product):
#     column_list = ['id', 'name', 'description', 'price', 'stock']
#     form_columns = ['name', 'description', 'price', 'stock']

# # Add views to admin
# admin.add_view(UserAdmin, category="Users")
# admin.add_view(ProductAdmin, category="Products")

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
    product_table_create = get_user_table(id)
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
        session.close()
        return {"message": f"Updated user with id {user_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, session : Session = Depends(get_db)):
    
    user_data = session.query(User).get(user_id)

    if user_data:
        session.delete(user_data)
        session.commit()
        session.close()
        return {"message": f"Deleted user with id {user_id}"}
    else:
        raise HTTPException(status_code=404, detail=f"user with id {user_id} not found")

@app.post("/admin/products")
def login(integer_input: IntegerInput, response: Response, session: Session = Depends(get_db)):
    id = integer_input.input_id
    user = session.query(User).filter(User.id == id).first()
    
    if user:
        response.set_cookie(key="user_id", value=str(id))
        return {"message": f"{id} present"}
        # return RedirectResponse(url=f"/admin/products/{id}", status_code=302)

    else:
        raise HTTPException(status_code=404, detail="User not found")


# Create Product for a specific user
@app.post("/admin/products/")
def create_product(product: ProductCreate, user_id: str = Cookie(None), session: Session = Depends(get_db)):
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not logged in")

    product_table = get_product_table(int(user_id))

    product_data = {
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock
    }

    insert_statement = insert(product_table).values(product_data)
    session.execute(insert_statement)
    session.commit()
    session.close()

    return {"message": f"Product created for user with id {user_id}"}

# Read all Products for a specific user
@app.get("/admin/products/", response_model=List[ProductCreate])
def read_products(user_id: str = Cookie(None), session: Session = Depends(get_db)):
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not logged in")
    
    product_table = get_product_table(int(user_id))
    
    query = session.query(product_table).all()
    session.close()
    product_list_pydantic = [ProductCreate.from_orm(product) for product in query]
    
    return product_list_pydantic

# Update a Product for a specific user
@app.put("/admin/products/{product_id}")
def update_product(product_id: int, product: ProductCreate, user_id: str = Cookie(None), session: Session = Depends(get_db)):
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not logged in")
    
    product_table = get_product_table(int(user_id))
    
    product_query = select(product_table).where(product_table.c.id == product_id)
    result = session.execute(product_query).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found for user {user_id}")

    update_statement = (
        update(product_table)
        .where(product_table.c.id == product_id)  
        .values(
            name=product.name,
            description=product.description,
            price=product.price,
            stock=product.stock
        )
    )
    session.execute(update_statement)
    session.commit()
    session.close()

    return {"message": f"Product with id {product_id} updated for user with id {user_id}"}


# Delete a Product for a specific user
@app.delete("/admin/products/{product_id}")
def delete_product(product_id: int, user_id: str = Cookie(None), session: Session = Depends(get_db)):
    if user_id is None:
        raise HTTPException(status_code=404, detail="User not logged in")

    product_table = get_product_table(int(user_id))
    
    product_query = select(product_table).where(product_table.c.id == product_id)
    result = session.execute(product_query).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found for user {user_id}")

    delete_statement = delete(product_table).where(product_table.c.id == product_id)
    session.execute(delete_statement)
    session.commit()
    session.close()

    return {"message": f"Product with id {product_id} deleted for user with id {user_id}"}
