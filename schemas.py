from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    role: str
    
    class Config:
        orm_mode = True
        from_attributes = True 
        
class LoginDetails(BaseModel):
    email: str
    username: str   
    
    class Config:
        orm_mode = True 
        from_attributes = True 
        
class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: float
    
    class Config:
        orm_mode = True 
        from_attributes = True 
        
class IntegerInput(BaseModel):
    input_id: int
    class Config:
        orm_mode = True 
        from_attributes = True     
    
