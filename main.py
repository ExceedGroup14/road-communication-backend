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
db = client["user-data"]
collection1 = db["user"]
data_car = db['car']


class User(BaseModel):
    username: str
    password: str
    email: str
    SerialNumber: str


class Car(BaseModel):
    email: str
    ID: str


# register new user
@app.post("/user-register/")
def user_register(u: User):
    query1 = {
        "username": u.username,
    }
    query2 = {
        "SerialNumber": u.SerialNumber
    }

    check_username = collection1.find_one(query1, {"_id": 0})
    check_SerialNumber = collection1.find_one(query2, {"_id": 0})

    if check_username is None and check_SerialNumber is None:
        user = {
            "username": u.username,
            "password": u.password,
            "SerialNumber": u.SerialNumber,
            "bt1": None,
            "bt2": None,
            "bt3": None,
            "bt4": None,
            "BreakText": "Break!!!",
            "LightBrokenText": "ไฟเสีย"
        }
        collection1.insert_one(user)
        return {
            "result": "register successfully"
        }
    else:
        return {
            "result": "username or serial number is already use"
        }


# user information
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


@app.post('/add-car/')
def add_car(car: Car):
    query = {"ID": car.ID}
    check_id_car = data_car.find_one(query, {"_id": 0})
    if check_id_car is None:
        car = {"email": car.email,
               "ID": car.ID,
               "bt1": None,
               "bt2": None,
               "bt3": None,
               "bt4": None,
               "break_light": "Break !!",
               "broken": "ขอโทษครับ ไฟเสียครับ"}
        c = jsonable_encoder(car)
        data_car.insert_one(c)
        return {
            "result": "The car was added successfully."
        }
    else:
        return {
            "result": "This car ID already has."
        }
