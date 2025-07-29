from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm  # Added import
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
import bcrypt
from database import SessionLocal  # Assuming you have this
from models_users import User  # Assuming you have this model

app = FastAPI()

# Configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper functions
def get_user_from_db(email: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()

def authenticate_user(email: str, password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        if not bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
            return False
        return user
    finally:
        db.close()

# Models and routes remain the same
class User(BaseModel):
    name: str
    email: str
    password: str

class RideRequest(BaseModel):
    pickup_location: str
    dropoff_location: str
    requested_time: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = get_user_from_db(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
async def register(user: User):
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()
        new_user = User(
            name=user.name,
            email=user.email,
            hashed_password=hashed_password,
            is_admin=False
        )
        
        db.add(new_user)
        db.commit()
        return {"message": "User created successfully"}
    finally:
        db.close()

@app.get("/user/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/rides/request")
async def request_ride(ride: RideRequest, current_user: User = Depends(get_current_user)):
    # Create new ride in database
    return {"message": "Ride requested successfully"}