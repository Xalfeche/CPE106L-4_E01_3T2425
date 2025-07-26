from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import googlemaps
import bcrypt
import jwt
from typing import Optional

# --- CONFIG ---
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "project"
GOOGLE_MAPS_API_KEY = "API_KEY_HERE"
JWT_SECRET = "SECRET_KEY_HERE"  
ALGORITHM = "HS256"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123"
ADMIN_NAME = "Admin"
# --------------

# Initialize app and services
app = FastAPI(title="CommunityConnect API")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
rides_col = db["ride_requests"]
users_col = db["users"]

# Create admin account at startup
@app.on_event("startup")
async def create_admin():
    # Check if admin exists
    admin_exists = await users_col.find_one({"email": ADMIN_EMAIL})
    if not admin_exists:
        # Hash admin password
        hashed_password = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
        admin_user = {
            "name": ADMIN_NAME,
            "email": ADMIN_EMAIL,
            "hashed_password": hashed_password,
            "is_admin": True,
            "created_at": datetime.utcnow()
        }
        await users_col.insert_one(admin_user)
        print("Admin account created")

# Pydantic models
class RideRequest(BaseModel):
    pickup_location: str
    dropoff_location: str
    requested_time: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(email: str) -> str:
    payload = {"sub": email}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

async def authenticate_user(email: str, password: str) -> Optional[dict]:
    user = await users_col.find_one({"email": email})
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

async def get_current_user(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = await users_col.find_one({"email": email})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# --- User Authentication Endpoints ---
@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister):
    # Check if email already exists
    existing_user = await users_col.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and create user
    hashed_password = hash_password(user.password)
    new_user = {
        "name": user.name,
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "is_admin": False  # Only admin is hardcoded
    }
    
    result = await users_col.insert_one(new_user)
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

@app.post("/login", response_model=Token)
async def login_user(user: UserLogin):
    authenticated_user = await authenticate_user(user.email, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}

# --- Ride Endpoints (Protected) ---
@app.post("/rides/request")
async def request_ride(r: RideRequest, token: str = Depends(get_current_user)):
    # Use authenticated user's name
    rider_name = token["name"]
    
    # Calculate real distance & duration
    matrix = gmaps.distance_matrix(r.pickup_location, r.dropoff_location, mode="driving")
    elem = matrix["rows"][0]["elements"][0]
    dist = elem["distance"]["value"]
    dur = elem["duration"]["value"]

    doc = {
        "rider_name": rider_name,
        "pickup_location": r.pickup_location,
        "dropoff_location": r.dropoff_location,
        "requested_time": r.requested_time,
        "distance_m": dist,
        "duration_s": dur,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "user_id": str(token["_id"])
    }
    
    res = await rides_col.insert_one(doc)
    return {"request_id": str(res.inserted_id), "distance_m": dist, "duration_s": dur}

@app.get("/rides/pending")
async def list_pending():
    return await rides_col.find({"status": "pending"}).to_list(100)

@app.post("/rides/accept/{rid}")
async def accept_ride(rid: str):
    upd = await rides_col.update_one(
        {"_id": rid, "status": "pending"},
        {"$set": {"status": "accepted"}}
    )
    if upd.modified_count == 0:
        raise HTTPException(404, "Ride not found or already accepted")
    return {"message": "accepted"}

@app.get("/analytics/ride_counts")
async def ride_counts():
    pipeline = [
        {"$group": {
            "_id": {"$dayOfWeek": "$created_at"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    raw = await rides_col.aggregate(pipeline).to_list(length=7)
    return [{"day": doc["_id"], "count": doc["count"]} for doc in raw]