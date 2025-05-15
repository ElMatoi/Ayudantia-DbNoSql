from motor.motor_asyncio import AsyncIOMotorClient  
import redis
from neo4j import GraphDatabase


mongo_client = AsyncIOMotorClient("mongodb://mongo:27017/") 
mongo_db = mongo_client["system_db"]
users_collection = mongo_db["users"]
products_collection = mongo_db["products"]


redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)


NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "dazzer123"
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
