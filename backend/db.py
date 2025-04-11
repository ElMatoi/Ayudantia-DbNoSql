from pymongo import MongoClient
import redis


mongo_client = MongoClient("mongodb://mongo:27017/") ## cliente para trabajar con mongo nombre y puertos declarados en el docker compose 
mongo_db = mongo_client["sensor_db"]
mongo_collection = mongo_db["sensores"]


redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)##cliente para trabajar con redis, puertos y nombre declarados en el docker compose
