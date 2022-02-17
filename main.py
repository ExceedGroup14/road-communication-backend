from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import Optional
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient('mongodb://localhost', 27017)
db =client["user-data"]
collection1 = db["user"]


class User(BaseModel):
    UserName: str
    Password: str
    FirstName: str
    LastName: str
    Email: str


# register new user
@app.post("/user-register/")
def user_register(u: User):
    query = {
        "Email": u.Email
    }

    check_Email = collection1.find_one(query, {"_id": 0})

    if check_Email is None:
        user = {
            "UserName": u.UserName,
            "Password": u.Password,
            "FirstName": u.FirstName,
            "LastName": u.LastName,
            "Email": u.Email,
            "IdCar": []
        }
        collection1.insert_one(user)
        return {
            "result": "register successfully"
        }
    else:
        return {
            "result": "username or serial number is already use"
        }

#user information
@app.get("/get/user-info/")
def user_login(u: User):
    query = {
        "username": u.username,
        "password": u.password
    }

    user = collection1.find_one(query, {"_id": 0})

    if user is None:
        raise HTTPException(404, f"Couldn't find user: {u.username}")
    
    return user

# add text to 4 bottoms
@app.put("/user-update/")
def add_text_bt(u: User, text1: Optional[str] = None, text2: Optional[str] = None,
text3: Optional[str] = None, text4: Optional[str] = None):
    query = {
        "username": u.username,
        "password": u.password
    }

    new_value = {
        "$set": {
            "bt1": text1,
            "bt2": text2,
            "bt3": text3,
            "bt4": text4
        }
    }

    collection1.update_one(query, new_value)
    
    return {
        "result": "update complete"
    }