Database.py -> database url is defined and we have also defined a function to get/connect to our database   

models.py -> Defined basic user and Product Models as derived classes of Base. We have also defined functions to create tables

schemas.py -> All the baseModels are defined here.

userApi -> CRUD Apis coresponding to the user also this creates a new product table whenever a new user is added to the table.  

productApi -> CRUD Apis coresponding to the products

login.py -> takes user id a sinput and regirects to coresponding products page



trial.py -> supposed to be main.py which would have all the CRUD Apis defined for both the user and products, but unable to figure out the login page using sqladmin. Works as expected using swagger (127.0.0.1:8000/docs)