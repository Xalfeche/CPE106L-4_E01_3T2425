from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse  
from pydantic import BaseModel
from datetime import datetime, timedelta
import bcrypt
import jwt
import requests
import os
from typing import Optional, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# --- CONFIG ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./communityconnect.db")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Admin123"
ADMIN_NAME = "Admin"
# -------------- 

Base = declarative_base()

# SQLAlchemy models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    rides = relationship("Ride", back_populates="user")

class Ride(Base):
    __tablename__ = "rides"
    id = Column(Integer, primary_key=True, index=True)
    rider_name = Column(String, nullable=False)
    pickup_location = Column(String, nullable=False)
    dropoff_location = Column(String, nullable=False)
    requested_time = Column(String, nullable=False)
    distance_m = Column(Integer)
    duration_s = Column(Integer)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    driver_id = Column(Integer, nullable=True)
    driver_name = Column(String, nullable=True)
    
    user = relationship("User", back_populates="rides")

# Database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CommunityConnect API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (commented out for Flet desktop mode)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create admin user on startup
@app.on_event("startup")
async def startup():
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        
        if not admin_exists:
            hashed_password = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
            admin_user = User(
                name=ADMIN_NAME,
                email=ADMIN_EMAIL,
                hashed_password=hashed_password,
                is_admin=True,
                created_at=datetime.utcnow()
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully")
    finally:
        db.close()

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

class UserOut(BaseModel):
    name: str
    email: str
    is_admin: bool

class RideOut(BaseModel):
    id: int
    rider_name: str
    pickup_location: str
    dropoff_location: str
    requested_time: str
    distance_m: Optional[int]
    duration_s: Optional[int]
    status: str
    created_at: datetime
    user_id: int
    driver_id: Optional[int] = None
    driver_name: Optional[str] = None

# Helper functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(email: str) -> str:
    payload = {"sub": email, "exp": datetime.utcnow() + timedelta(hours=24)}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# API Endpoints
@app.get("/")
async def read_root():
    return {
        "message": "CommunityConnect API", 
        "version": "1.0.0",
        "docs": "/docs",
        "admin_credentials": {
            "email": "admin@example.com",
            "password": "Admin123"
        }
    }

@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        is_admin=False,
        created_at=datetime.utcnow()
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

@app.post("/token", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db, form_data.username, form_data.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token(authenticated_user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
async def login_for_frontend(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await login_user(form_data, db)

@app.get("/user/me", response_model=UserOut)
async def get_current_user_details(current_user: User = Depends(get_current_user)):
    return UserOut(
        name=current_user.name,
        email=current_user.email,
        is_admin=current_user.is_admin
    )

@app.post("/rides/request")
async def request_ride(r: RideRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        response = requests.get(
            f"http://router.project-osrm.org/route/v1/driving/{r.pickup_location};{r.dropoff_location}?overview=false",
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Routing service unavailable"
            )
            
        data = response.json()
        if data.get('code') != 'Ok':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid coordinates or routing failed"
            )
            
        route = data['routes'][0]
        dist = route['distance']
        dur = route['duration']
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing service error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Routing error: {str(e)}"
        )

    new_ride = Ride(
        rider_name=current_user.name,
        pickup_location=r.pickup_location,
        dropoff_location=r.dropoff_location,
        requested_time=r.requested_time,
        distance_m=int(dist),
        duration_s=int(dur),
        status="pending",
        created_at=datetime.utcnow(),
        user_id=current_user.id
    )
    
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    
    return {"request_id": new_ride.id, "distance_m": dist, "duration_s": dur}

@app.get("/rides/pending")
async def list_pending(db: Session = Depends(get_db)):
    rides = db.query(Ride).filter(Ride.status == "pending").all()
    return [
        {
            "id": ride.id,
            "rider_name": ride.rider_name,
            "pickup_location": ride.pickup_location,
            "dropoff_location": ride.dropoff_location,
            "requested_time": ride.requested_time,
            "distance_m": ride.distance_m,
            "duration_s": ride.duration_s,
            "status": ride.status,
            "created_at": ride.created_at,
            "user_id": ride.user_id
        }
        for ride in rides
    ]

@app.get("/rides/{ride_id}")
async def get_ride(ride_id: int, db: Session = Depends(get_db)):
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(404, "Ride not found")
    return {
        "id": ride.id,
        "rider_name": ride.rider_name,
        "pickup_location": ride.pickup_location,
        "dropoff_location": ride.dropoff_location,
        "requested_time": ride.requested_time,
        "distance_m": ride.distance_m,
        "duration_s": ride.duration_s,
        "status": ride.status,
        "created_at": ride.created_at,
        "user_id": ride.user_id,
        "driver_id": ride.driver_id,
        "driver_name": ride.driver_name
    }

@app.post("/rides/accept/{rid}")
async def accept_ride(rid: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ride = db.query(Ride).filter(Ride.id == rid, Ride.status == "pending").first()
    
    if not ride:
        raise HTTPException(404, "Ride not found or already accepted")
    
    ride.status = "accepted"
    ride.driver_id = current_user.id
    ride.driver_name = current_user.name
    
    db.commit()
    return {"message": "accepted"}

@app.post("/rides/complete/{rid}")
async def complete_ride(rid: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ride = db.query(Ride).filter(Ride.id == rid, Ride.driver_id == current_user.id).first()
    if not ride:
        raise HTTPException(404, "Ride not found or you are not the driver")
    ride.status = "completed"
    db.commit()
    return {"message": "completed"}

@app.get("/analytics/ride_counts")
async def ride_counts(db: Session = Depends(get_db)):
    # Since we're using SQLAlchemy with SQLite, we need to use raw SQL for date functions
    with engine.connect() as connection:
        result = connection.execute("""
            SELECT 
                CAST(strftime('%w', created_at) AS INTEGER) AS day_of_week, 
                COUNT(*) AS count
            FROM rides
            GROUP BY day_of_week
            ORDER BY day_of_week
        """)
        results = result.fetchall()
    
    return [{"day": int(row[0]) + 1, "count": row[1]} for row in results]

@app.get("/analytics/user_rides")
async def user_rides(db: Session = Depends(get_db)):
    with engine.connect() as connection:
        result = connection.execute("""
            SELECT 
                rider_name, 
                COUNT(*) AS count
            FROM rides
            GROUP BY rider_name
            ORDER BY count DESC
            LIMIT 10
        """)
        results = result.fetchall()
    
    return [{"rider_name": row[0], "count": row[1]} for row in results]

@app.get("/analytics/recent_rides")
async def recent_rides(limit: int = 10, db: Session = Depends(get_db)):
    rides = db.query(Ride).order_by(Ride.created_at.desc()).limit(limit).all()
    return [
        {
            "id": ride.id,
            "rider_name": ride.rider_name,
            "pickup_location": ride.pickup_location,
            "dropoff_location": ride.dropoff_location,
            "requested_time": ride.requested_time,
            "distance_m": ride.distance_m,
            "duration_s": ride.duration_s,
            "status": ride.status,
            "created_at": ride.created_at,
            "user_id": ride.user_id,
            "driver_id": ride.driver_id,
            "driver_name": ride.driver_name
        }
        for ride in rides
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)