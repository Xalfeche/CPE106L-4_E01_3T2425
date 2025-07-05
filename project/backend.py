from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import googlemaps

# --- CONFIG ---
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "communityconnect"
GOOGLE_MAPS_API_KEY = "AIzaSyAQGNBrrl9hB9exTYzmhxGgYWBB3np458A"
# --------------

# init
app = FastAPI(title="CommunityConnect API")
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
rides_col = db["ride_requests"]

# Pydantic model
class RideRequest(BaseModel):
    rider_name: str
    pickup_location: str
    dropoff_location: str
    requested_time: str

# create a ride request
@app.post("/rides/request")
async def request_ride(r: RideRequest):
    # calculate real distance & duration
    matrix = gmaps.distance_matrix(r.pickup_location, r.dropoff_location, mode="driving")
    elem = matrix["rows"][0]["elements"][0]
    dist = elem["distance"]["value"]
    dur  = elem["duration"]["value"]

    doc = r.dict()
    doc.update({
        "distance_m": dist,
        "duration_s": dur,
        "status": "pending",
        "created_at": datetime.utcnow()
    })
    res = await rides_col.insert_one(doc)
    return {"request_id": str(res.inserted_id), "distance_m": dist, "duration_s": dur}

# list pending
@app.get("/rides/pending")
async def list_pending():
    return await rides_col.find({"status": "pending"}).to_list(100)

# accept a ride
@app.post("/rides/accept/{rid}")
async def accept_ride(rid: str):
    upd = await rides_col.update_one({"_id": rid, "status": "pending"}, {"$set": {"status": "accepted"}})
    if upd.modified_count == 0:
        raise HTTPException(404, "Ride not found or already accepted")
    return {"message": "accepted"}

# analytics: rides per weekday
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
    # transform for frontend
    return [{"day": doc["_id"]["$dayOfWeek"] if isinstance(doc["_id"], dict) else doc["_id"],
             "count": doc["count"]} for doc in raw]
