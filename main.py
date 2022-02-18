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
dbUser = db["user"]
dbCar = db["car"]
dbSnum = db["serial_number"]


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

class Car(BaseModel):
    email: str
    ID: str
    serial_number: str


# register new user
@app.post("/register/")
def user_register(u: NewUser):
    query1 = {
        "email": u.email
    }
    query2 = {
        "username": u.username
    }
    check_Email = dbUser.find_one(query1, {})
    check_username = dbUser.find_one(query2, {})

    if check_Email is None and check_username is None:
        hashedPassword = passwordContext.hash(u.password)
        u.password = hashedPassword
        user = jsonable_encoder(u)
        dbUser.insert_one(user)
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

    user = dbUser.find_one(query, {})
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

class Text(BaseModel):
    text1: Optional[str] = None
    text2: Optional[str] = None
    text3: Optional[str] = None
    text4: Optional[str] = None

# add text to bottom
@app.put("/add-text/")
def user_add_text(t: Text, email: str):
    query = {
        "email": email
    }
    if t.text1 is None and t.text2 is None and t.text3 is None and t.text4 is None:
        return {
            "result": "nothing change"
        }
    
    if t.text1 is not None:
        new_value = {"$set": {"bt1": t.text1}}
        dbCar.update_one(query, new_value)
    if t.text2 is not None:
        new_value = {"$set": {"bt2": t.text2}}
        dbCar.update_one(query, new_value)
    if t.text3 is not None:
        new_value = {"$set": {"bt3": t.text3}}
        dbCar.update_one(query, new_value)
    if t.text4 is not None:
        new_value = {"$set": {"bt4": t.text4}}
        dbCar.update_one(query, new_value)
    return {
        "result": "add text to bottom successfully!"
    }
 
@app.post('/add-car/')
def add_car(car: Car):
    query = {"ID": car.ID}
    query2 = {"serial_number": car.serial_number}

    check_id_car = dbCar.find_one(query, {"_id": 0})
    check_Snum_in_dbCar = dbCar.find_one(query2, {})
    check_Snum_in_dbSnum = dbSnum.find_one(query2, {})

    if check_Snum_in_dbSnum is None:
        return {
            "result": "This serial number is not in database."
        }

    if check_id_car is None and check_Snum_in_dbCar is None:
        car = {"email": car.email,
               "ID": car.ID,
               "serial_number": car.serial_number,
               "bt1": "สวัสดีครับ",
               "bt2": "ขับขี่ ปลอดภัยนะครับ",
               "bt3": "ขอบคุณครับ",
               "bt4": "เมาไม่ขับ ครับ",
               "break_light": "Break !!",
               "broken": "ขอโทษครับ ไฟเสียครับ"}
        c = jsonable_encoder(car)
        dbCar.insert_one(c)
        return {
            "result": "The car was added successfully."
        }
    else:
        return {
            "result": "This car ID or serial number already has."
        }


@app.get('/all-car/')
def get_all_car(email: str):
    car = dbCar.find({"email": email}, {"_id": 0})
    data = []
    for i in car:
        data.append(i)
    return {
        "result": data
    }
