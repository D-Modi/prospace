
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
    __tablename__ = "products"
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

def create_user_table(user_id: int):
    metadata = MetaData()
    table_name = f'products_{user_id}'   
    
    new_table = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True, index=True),
        Column('name', String, nullable=False),
        Column('description', String, nullable=True),
        Column('price', Float, nullable=False),
        Column('stock', Float, nullable=False)
    )
    
    metadata.create_all(bind=engine, tables=[new_table])
    
def create_user_products_table(user_id):
    
    class Product(Base):
        __tablename__ = f'products_{user_id}'
        id = Column(Integer, primary_key=True, index=True)
        name = Column(String)
        description = Column(String)
        price = Column(Float)
        stock = Column(Float)

    return Product

def drop_all_tables():
    metadata = MetaData()
    metadata.reflect(bind=engine)
    metadata.drop_all(bind=engine)
    print("All tables dropped successfully.")   
    
drop_all_tables()

