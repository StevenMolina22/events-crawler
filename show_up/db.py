from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from pymongo import MongoClient
import asyncio
import os

load_dotenv()

URI = os.getenv("MONGODB_URI")
assert URI is not None


async def ping_server():
    # Replace the placeholder with your Atlas connection string
    # Set the Stable API version when creating a new client
    client = AsyncIOMotorClient(URI, server_api=ServerApi("1"))

    # Send a ping to confirm a successful connection
    try:
        await client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)


def print_events():
    """Use example"""
    db = get_db()
    coll_events = db["events"]

    for event in coll_events.find():
        print(event)


def get_db():
    client = MongoClient(URI)
    db = client["showup_events"]
    return db


if __name__ == "__main__":
    asyncio.run(ping_server())
    print_events()  # use example
