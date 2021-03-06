from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import Optional
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from jose import JWTError, jwt
import time

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


passwordContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Car(BaseModel):
    token: str
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


SECRET = "aa452d886485af0c397cb635cab16f4213ea9b97e311b38dd7d47c0184461151"


# login
@app.post("/login/")
def user_login(u: User):
    query = {
        "username": u.username,
    }

    user = dbUser.find_one(query, {})
    if user is None:
        return {
            "result": "Username not found"
        }
    elif passwordContext.verify(u.password, user["password"]):
        expirationTime = int(time.time() + 3600)
        token = jwt.encode({"exp": expirationTime, "email": user["email"]}, SECRET, algorithm="HS256")

        return {
            "token": token
        }
    else:
        return {
            "result": "Incorrect password"
        }


class Text(BaseModel):
    token: str
    serial_number: str
    text1: str
    text2: str
    text3: str
    text4: str


# add text to bottom
@app.put("/add-text/")
def user_add_text(t: Text):
    isValid, processed_token = verify_token(t.token)
    if not isValid:
        return {"result": "Invalid token"}
    email = processed_token["email"]
    query = {"email": email, "serial_number": t.serial_number, }
    car = dbCar.find_one(query, {})
    if t.text1 != car['bt1']:
        new_value = {"$set": {"bt1": t.text1, "Numbt1": 0}}
        dbCar.update_one(query, new_value)

    if t.text2 != car['bt2']:
        new_value = {"$set": {"bt2": t.text2, "Numbt2": 0}}
        dbCar.update_one(query, new_value)

    if t.text3 != car['bt3']:
        new_value = {"$set": {"bt3": t.text3, "Numbt3": 0}}
        dbCar.update_one(query, new_value)

    if t.text4 != car['bt4']:
        new_value = {"$set": {"bt4": t.text4, "Numbt4": 0}}
        dbCar.update_one(query, new_value)
    return {
        "result": "add text to bottom successfully!"
    }


@app.post('/add-car/')
def add_car(car: Car):
    isValid, processed_token = verify_token(car.token)
    if not isValid:
        return {"result": "Invalid token"}

    email = processed_token["email"]
    query = {"ID": car.ID}
    query2 = {"serial_number": car.serial_number}
    query3 = {"email": email}

    check_user = dbUser.find_one(query3, {})
    check_id_car = dbCar.find_one(query, {"_id": 0})
    check_Snum_in_dbCar = dbCar.find_one(query2, {})
    check_Snum_in_dbSnum = dbSnum.find_one(query2, {})

    if check_user is None:
        return {
            "result": "This email has no in Database."
        }

    if check_Snum_in_dbSnum is None:
        return {
            "result": "This serial number is not in database."
        }

    if check_id_car is None and check_Snum_in_dbCar is None:
        car = {"email": email,
               "ID": car.ID,
               "serial_number": car.serial_number,
               "bt1": "Hello",
               "bt2": "Safety First",
               "bt3": "Thank you",
               "bt4": "don't drive drunk",
               "break_light": "Break !!",
               "broken": "Sorry the tail light broke",
               "Numbt1": 0,
               "Numbt2": 0,
               "Numbt3": 0,
               "Numbt4": 0,
               "status_bt1": 0,
               "status_bt2": 0,
               "status_bt3": 0,
               "status_bt4": 0,
               "status_break": 0,
               "status_broken_l": 0,
               "status_broken_r": 0
               }
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
def get_all_car(token: str):
    isValid, processed_token = verify_token(token)
    if not isValid:
        return {"result": "Invalid token"}
    email = processed_token["email"]
    car = dbCar.find({"email": email}, {"_id": 0})
    data = []
    for i in car:
        data.append(i)
    return {
        "result": data
    }


@app.get('/get_car/')
def get_car(token: str, serial_number: str):
    isValid, processed_token = verify_token(token)
    if not isValid:
        return {"result": "Invalid token"}
    email = processed_token["email"]
    car = dbCar.find_one({"email": email, "serial_number": serial_number}, {"_id": 0})
    return {"result": car}


@app.get('/sorted_car/')
def sorted_car(token: str, serial_number: str):
    isValid, processed_token = verify_token(token)
    if not isValid:
        return {"result": "Invalid token"}
    email = processed_token["email"]
    car = dbCar.find_one({"email": email, "serial_number": serial_number}, {"_id": 0})
    cars = {car["bt1"]: car["Numbt1"], car["bt2"]: car["Numbt2"], car["bt3"]: car["Numbt3"], car["bt4"]: car["Numbt4"]}
    sortedCars = {k: v for k, v in sorted(cars.items(), key=lambda item: item[1],reverse=True)}
    return {"result": sortedCars}


class Input(BaseModel):
    serial_number: str
    bt1: int
    bt2: int
    bt3: int
    bt4: int
    bt_break: int
    senlight1: int
    senlight2: int


@app.post("/output/")
def output_text_hardware(input: Input):
    print(input)
    query = {
        "serial_number": input.serial_number
    }
    car = dbCar.find_one(query, {})

    if input.bt_break == 1 and input.senlight1 == 1 and input.senlight2 == 1:
        new_value = {"$set": {"status_break": 1, "status_broken_l": 0, "status_broken_r": 0}}
        dbCar.update_one(query, new_value)
        return {
            "text": car["break_light"]
        }
    elif input.bt_break == 1 and input.senlight2 == 1 and input.senlight1 == 0:
        new_value = {"$set": {"status_broken_r": 1, "status_broken_l": 0}}
        dbCar.update_one(query, new_value)
        return {
            "text": car["broken"]
        }
    elif input.bt_break == 1 and input.senlight1 == 1 and input.senlight2 == 0:
        new_value = {"$set": {"status_broken_l": 1, "status_broken_r": 0}}
        dbCar.update_one(query, new_value)
        return {
            "text": car["broken"]
        }
    elif input.bt_break == 1 and input.senlight1 == 0 and input.senlight2 == 0:
        new_value = {"$set": {"status_broken_l": 1, "status_broken_r": 1}}
        dbCar.update_one(query, new_value)
        return {
            "text": car["broken"]
        }
    elif input.bt_break == 0:
        new_value = {"$set": {"status_break": 0}}
        dbCar.update_one(query, new_value)

    if input.bt1 == 1:
        value = car["Numbt1"] + 1
        new_value = {"$set": {"Numbt1": value, "status_bt1": 1}}
        dbCar.update_one(query, new_value)
        return {
            "text": car["bt1"]
        }
    elif input.bt1 == 0:
        new_value = {"$set": {"status_bt1": 0}}
        dbCar.update_one(query, new_value)

    if input.bt2 == 1:
        value = car["Numbt2"] + 1
        new_value = {"$set": {"Numbt2": value, "status_bt2": 1}}
        dbCar.update_one(query, new_value)
        return {
            "text": car["bt2"]
        }

    elif input.bt2 == 0:
        new_value = {"$set": {"status_bt2": 0}}
        dbCar.update_one(query, new_value)

    if input.bt3 == 1:
        value = car["Numbt3"] + 1
        new_value = {"$set": {"Numbt3": value, "status_bt3": 1}}
        dbCar.update_one(query, new_value)
        return {
            "text": car["bt3"]
        }
    elif input.bt3 == 0:
        new_value = {"$set": {"status_bt3": 0}}
        dbCar.update_one(query, new_value)

    if input.bt4 == 1:
        value = car["Numbt4"] + 1
        new_value = {"$set": {"Numbt4": value, "status_bt4": 1}}
        dbCar.update_one(query, new_value)
        return {
            "text": car["bt4"]
        }
    elif input.bt4 == 0:
        new_value = {"$set": {"status_bt4": 0}}
        dbCar.update_one(query, new_value)

# @app.post("/output/")
# def output_text_hardware(input: Input):
#     query = {
#         "serial_number": input.serial_number
#     }
#     car = dbCar.find_one(query, {})

#     if input.bt_break == 1 and input.senlight1 == 1 and input.senlight2 == 1:
#         new_value = {"$set": {"status_break": 1, "status_broken": 0}}
#         dbCar.update_one(query, new_value)
#         return {
#             "text": car["break_light"]
#         }
#     elif input.bt_break == 1:
#         new_value = {"$set": {"status_broken": 1}}
#         dbCar.update_one(query, new_value)
#         return {
#             "text": car["broken"]
#         }
#     elif input.bt_break == 0:
#         new_value = {"$set": {"status_break": 0}}
#         dbCar.update_one(query, new_value)

#     if input.bt1 == 1:
#         value = car["Numbt1"] + 1
#         new_value = {"$set": {"Numbt1": value, "status_bt1": 1}}
#         dbCar.update_one(query, new_value)
#         return {
#             "text": car["bt1"]
#         }
#     elif input.bt1 == 0:
#         new_value = {"$set": {"status_bt1": 0}}
#         dbCar.update_one(query, new_value)

#     if input.bt2 == 1:
#         value = car["Numbt2"] + 1
#         new_value = {"$set": {"Numbt2": value, "status_bt2": 1}}
#         dbCar.update_one(query, new_value)
#         return {
#             "text": car["bt2"]
#         }

#     elif input.bt2 == 0:
#         new_value = {"$set": {"status_bt2": 0}}
#         dbCar.update_one(query, new_value)

#     if input.bt3 == 1:
#         value = car["Numbt3"] + 1
#         new_value = {"$set": {"Numbt3": value, "status_bt3": 1}}
#         dbCar.update_one(query, new_value)
#         return {
#             "text": car["bt3"]
#         }
#     elif input.bt3 == 0:
#         new_value = {"$set": {"status_bt3": 0}}
#         dbCar.update_one(query, new_value)

#     if input.bt4 == 1:
#         value = car["Numbt4"] + 1
#         new_value = {"$set": {"Numbt4": value, "status_bt4": 1}}
#         dbCar.update_one(query, new_value)
#         return {
#             "text": car["bt4"]
#         }
#     elif input.bt4 == 0:
#         new_value = {"$set": {"status_bt4": 0}}
#         dbCar.update_one(query, new_value)




def verify_token(token):
    try:
        email = jwt.decode(token, SECRET, algorithms="HS256")

        return True, email
    except:
        return False, {}
