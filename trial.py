
from fastapi import FastAPI, status, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import MetaData, Table
from sqladmin import Admin, ModelView
from starlette.middleware.sessions import SessionMiddleware
from database import engine, get_db     
from schemas import UserCreate, LoginDetails, ProductCreate
from models import User, create_user_products_table, create_tables, Product

create_tables(["users"])
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="qwerty")  
metadata = MetaData()
token = None
produts_table_name = None

# class UserAdmin(ModelView, model=User):
#     column_list = [User.id, User.username, User.email, User.role]  # Fields to display

# # Initialize SQLAdmin
# admin = Admin(app, engine)
# admin.add_view(UserAdmin)   

# Create an authentication backend
# class SQLAdminAuth(AuthenticationBackend):
#     async def login(self, request: Request) -> bool:
#         form = await request.form()
#         email = form.get("email")
#         username = form.get("username")
        
#         db: Session = next(get_db())
#         user = db.query(User).filter(User.email == email).first()
        
#         if not user:
#             return False
#         if username != user.username:   
#             return False    
        
#         # Set user info in session or cookies
#         request.session.update({"user_id": user.id, "is_admin": user.is_admin})
        
#         return True

#     async def logout(self, request: Request) -> bool:
#         # Clear the session to log out the user
#         request.session.clear()
#         return True

#     async def authenticate(self, request: Request) -> bool:
#         # Check if user is logged in and has admin privileges
#         if "user_id" in request.session and request.session["is_admin"]:
#             return True
#         return False


# Initialize SQLAdmin with authentication


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.role]
    column_searchable_list = [User.username, User.email]
    column_sortable_list = [User.id]

# Define a ModelView for the Product model
class DynamicProductAdmin(ModelView, mosel=Product):
    # This function will dynamically get the user's product table based on the login
    def get_model(self, request: Request):
        user_id = request.cookies.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Dynamically define the user's product table
        product_table_name = f"products_{user_id}"
        product_table = Table(product_table_name, metadata, autoload_with=request.db)
        return product_table
    
    # Define columns to display in the dynamic table
    column_list = [Product.id, Product.name, Product.description, Product.price, Product.stock]
    column_searchable_list = [Product.name, Product.description]
    column_sortable_list = [Product.id, Product.price]

# Initialize Admin interface and register views
admin = Admin(app, engine)
admin.add_view(UserAdmin)
admin.add_view(DynamicProductAdmin)

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
    ProductTable = create_user_products_table(user.id)
    create_tables(ProductTable, i=1)
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

@app.post("/admin/login/")
def login(email: str = Form(...), username: str = Form(...), session: Session = Depends(get_db)):
    user = session.query(User).filter(User.email == email, User.username == username).first()
    
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid email or username")
    
    user_id = user.id
    # Store the user_id in the session or return as a token
    response = Response({"message": "Login Successful", "user_id": user_id})
    response.set_cookie("user_id", str(user_id))  # Store user_id in a cookie for subsequent requests
    return response 

@app.get("/admin/products")
def get_user_products(request: Request, session: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Assuming you have some mechanism to access the session and db
    product_table_name = f'products_{user_id}'
    product_table = Table(product_table_name, metadata, autoload_with=engine)
    query = session.query(product_table).all()
    product_list_pydantic = [ProductCreate.from_orm(product) for product in query]
    session.close()
    
    # Return the queried products
    return product_list_pydantic


