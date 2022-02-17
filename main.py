from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import Optional
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
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
collection_user = db["user"]


class NewUser(BaseModel):
    username: str
    password: str
    email: str
    firstname: str
    lastname: str

class User(BaseModel):
    username: str
    password: str

passwordContext = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

# register new user
@app.post("/register/")
def user_register(u: NewUser):
    query1 = {
        "email": u.email
    }
    query2 = {
        "username": u.username
    }

    check_Email = collection_user.find_one(query1, {})
    check_username = collection_user.find_one(query2, {})

    if check_Email is None and check_username is None:
        hashedPassword = passwordContext.hash(u.password)
        u.password = hashedPassword
        user = jsonable_encoder(u)
        collection_user.insert_one(user)
        return {
            "result": "register successfully"
        }
    else:
        return {
            "result": "Username or Email is already use"
        }

# login
@app.get("/login/")
def user_login(u: User):
    query = {
        "username": u.username,
    }

    user = collection_user.find_one(query, {})

    if user is None:
        raise HTTPException(404, detail = f"Couldn't find user: {u.username}")
    elif passwordContext.verify(u.password, user["password"]):
        return {
            "username": user["username"],
            "email": user["email"]
        }
    else:
        return {
            "result": "Incorrect password"
        }


# add text to 4 bottoms
# @app.put("/user-update/")
# def add_text_bt(u: User, text1: Optional[str] = None, text2: Optional[str] = None,
# text3: Optional[str] = None, text4: Optional[str] = None):
#     query = {
#         "username": u.username,
#         "password": u.password
#     }

#     new_value = {
#         "$set": {
#             "bt1": text1,
#             "bt2": text2,
#             "bt3": text3,
#             "bt4": text4
#         }
#     }

#     collection1.update_one(query, new_value)
    
#     return {
#         "result": "update complete"
#     }