from pymongo import MongoClient
import redis
from neo4j import GraphDatabase


mongo_client = MongoClient("mongodb://mongo:27017/") ## cliente para trabajar con mongo nombre y puertos declarados en el docker compose 
mongo_db = mongo_client["sensor_db"]
mongo_collection = mongo_db["sensores"]


redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)##cliente para trabajar con redis, puertos y nombre declarados en el docker compose

NEO4J_URI = "bolt://neo4j:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "dazzer123"
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))