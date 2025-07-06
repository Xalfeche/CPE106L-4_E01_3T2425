'''
Alfeche, Paul Janric E.
06-07-2025
'''


import pymongo
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "music_db"

def create_and_populate_db():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        print(f"Connected to MongoDB. Using database: {DATABASE_NAME}")

        artists_data = [
            {"artist_id": 1, "name": "The Beatles"},
            {"artist_id": 2, "name": "Queen"},
            {"artist_id": 3, "name": "Adele"}
        ]
        artists_result = db.artists.insert_many(artists_data)
        print(f"Inserted {len(artists_result.inserted_ids)} artists.")

        albums_data = [
            {"album_id": 101, "title": "Abbey Road", "artist_id": 1},
            {"album_id": 102, "title": "A Night at the Opera", "artist_id": 2},
            {"album_id": 103, "title": "21", "artist_id": 3},
            {"album_id": 104, "title": "Let It Be", "artist_id": 1}
        ]
        albums_result = db.albums.insert_many(albums_data)
        print(f"Inserted {len(albums_result.inserted_ids)} albums.")

        tracks_data = [
            {
                "track_id": 1001,
                "name": "Come Together",
                "album_id": 101,
                "media_type_id": 1,
                "genre_id": 1,
                "composer": "Lennon/McCartney",
                "milliseconds": 260000,
                "bytes": 5200000,
                "unit_price": 0.99
            },
            {
                "track_id": 1002,
                "name": "Something",
                "album_id": 101,
                "media_type_id": 1,
                "genre_id": 1,
                "composer": "George Harrison",
                "milliseconds": 180000,
                "bytes": 3600000,
                "unit_price": 0.99
            },
            {
                "track_id": 1003,
                "name": "Bohemian Rhapsody",
                "album_id": 102,
                "media_type_id": 1,
                "genre_id": 2,
                "composer": "Freddie Mercury",
                "milliseconds": 354000,
                "bytes": 7080000,
                "unit_price": 1.29
            },
            {
                "track_id": 1004,
                "name": "Someone Like You",
                "album_id": 103,
                "media_type_id": 1,
                "genre_id": 3,
                "composer": "Adele Adkins, Dan Wilson",
                "milliseconds": 285000,
                "bytes": 5700000,
                "unit_price": 0.99
            },
            {
                "track_id": 1005,
                "name": "Get Back",
                "album_id": 104,
                "media_type_id": 1,
                "genre_id": 1,
                "composer": "Lennon/McCartney",
                "milliseconds": 187000,
                "bytes": 3740000,
                "unit_price": 0.99
            }
        ]
        tracks_result = db.tracks.insert_many(tracks_data)
        print(f"Inserted {len(tracks_result.inserted_ids)} tracks.")

        print("\nDatabase creation and population complete!")

        print("\n--- Retrieving all data from the database ---")
        read_all_artists(db)
        read_all_albums(db)
        read_all_tracks(db)

    except pymongo.errors.ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")
        print("Please ensure MongoDB is running and accessible at the specified URI.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if 'client' in locals() and client:
            client.close()
            print("MongoDB connection closed.")

def read_all_artists(db):
    print("\n--- Artists ---")
    for artist in db.artists.find({}):
        print(artist)

def read_all_albums(db):
    print("\n--- Albums ---")
    for album in db.albums.find({}):
        print(album)

def read_all_tracks(db):
    print("\n--- Tracks ---")
    for track in db.tracks.find({}):
        print(track)

if __name__ == "__main__":
    create_and_populate_db()
