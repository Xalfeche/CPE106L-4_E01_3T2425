# 1. Backend: User auth API & MongoDB setup.
# This section handles user authentication and MongoDB interactions.
# This code directly implements logic for a self-contained application.
class CommunityConnectBackend:
    """
    Manages all data and core logic for CommunityConnect.
    This class connects to MongoDB for data persistence.
    """
    def __init__(self):
        try:
            # Establish MongoDB connection

            self.client = MongoClient("mongodb://localhost:*insert port*/")
            self.db = self.client.communityconnect_db # Your database name

            # Define collections
            self.users_collection = self.db.users
            self.drivers_collection = self.db.drivers
            self.vehicles_collection = self.db.vehicles
            self.locations_collection = self.db.locations
            self.ride_requests_collection = self.db.ride_requests
            self.accessibility_needs_collection = self.db.accessibility_needs
            self.driver_availabilities_collection = self.db.driver_availabilities

            # Ensures unique index
            self.users_collection.create_index("user_id", unique=True)
            self.users_collection.create_index("email", unique=True)
            self.drivers_collection.create_index("driver_id", unique=True)
            self.vehicles_collection.create_index("vehicle_id", unique=True)
            self.locations_collection.create_index("location_id", unique=True)
            self.ride_requests_collection.create_index("request_id", unique=True)
            self.accessibility_needs_collection.create_index("accessibility_id", unique=True)
            self.driver_availabilities_collection.create_index("availability_id", unique=True)

            print("Successfully connected to MongoDB.")

        except pymongo_errors.ConnectionFailure as e:
            QMessageBox.critical(None, "Database Connection Error",
                                 f"Could not connect to MongoDB: {e}\n"
                                 "Please ensure MongoDB is installed and running on localhost:27017.")
            # Exit application
            sys.exit(1) # Exit if cannot connect to DB at startup
        except Exception as e:
            QMessageBox.critical(None, "Initialization Error",
                                 f"An unexpected error occurred during backend initialization: {e}")
            sys.exit(1)