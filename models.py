
from sqlalchemy import Column, Integer, String, Float, Table, MetaData
from database import Base, engine

# User Model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)   
    
class Product(Base):    
    __abstract__ = True 
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Float, nullable=False)
    
def create_tables(table_names=None, i=0):
    if table_names: 
        if i == 1:  
            Base.metadata.create_all(bind=engine, tables=table_names)   
        else:
            tables_to_create = [Base.metadata.tables[table_name] for table_name in table_names if table_name in Base.metadata.tables]
            Base.metadata.create_all(bind=engine, tables=tables_to_create)
    else:
        # Create all tables if no specific tables are provided
        Base.metadata.create_all(bind=engine)

def get_user_table(user_id):
    tablename = f'products_{user_id}' 
    class_name = f'Product{user_id}'
    Model = type(class_name, (Product,), {
        '__tablename__': tablename
    })
    create_tables([tablename])
    print("Table Created")
    return Model

def drop_all_tables():
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)
    print("All tables dropped successfully.")   
    
# get_user_table(50)

