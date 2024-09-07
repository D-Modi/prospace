from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import MetaData, Table, insert, update, delete
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from schemas import ProductCreate
from database import get_db, engine     
 
app = FastAPI()

#gets the product table for a given user_id
def get_product_table(user_id: int):
    metadata = MetaData()
    table_name = f'products_{user_id}'
    
    product_table = Table(
        table_name, 
        metadata, 
        autoload_with=engine,  
    )
    
    return product_table

# Create Product for a specific user
@app.post("/admin/products/{user_id}/")
def create_product(user_id: int, product: ProductCreate, session: Session = Depends(get_db)):
    product_table = get_product_table(user_id)

    product_data = {
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock
    }

    insert_statement = insert(product_table).values(product_data)
    session.execute(insert_statement)
    session.commit()

    return {"message": f"Product created for user {user_id}"}

# Read all Products for a specific user
@app.get("/admin/products/{user_id}/", response_model=List[ProductCreate])
def read_products(user_id: int, session: Session = Depends(get_db)):
    product_table = get_product_table(user_id)
    
    query = session.query(product_table).all()
    session.close()
    
    # Convert to Pydantic model list
    product_list_pydantic = [ProductCreate.from_orm(user) for user in query]
    
    return product_list_pydantic

# Update a Product for a specific user
@app.put("/admin/products/{user_id}/{product_id}")
def update_product(user_id: int, product_id: int, product: ProductCreate, session: Session = Depends(get_db)):
    product_table = get_product_table(user_id)

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

    return {"message": f"Product with id {product_id} updated for user {user_id}"}


# Delete a Product for a specific user
@app.delete("/admin/products/{user_id}/{product_id}")
def delete_product(user_id: int, product_id: int, session: Session = Depends(get_db)):
    product_table = get_product_table(user_id)

    delete_statement = delete(product_table).where(product_table.c.id == product_id)
    session.execute(delete_statement)
    session.commit()

    return {"message": f"Product with id {product_id} deleted for user {user_id}"}