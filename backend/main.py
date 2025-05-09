from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from db import redis_client, mongo_collection
import uuid
import json
from graph import endpoint as graph_router

app = FastAPI()
app.include_router(graph_router)

class SensorMedicion(BaseModel):  # modelo de transferencia de datos (DTO) usando pydantic
    sensorId: str
    value: float
    unit: str
    timestamp: str



@app.get("/getSensor/{sensor_id}") ## endpoint para obtener los dartos de un sensor en la cache --> http://localhost:8000/getSensor/sensor-123-fdc7a306-6bfc-4f69-aa8e-bd8e3046aae1 (clave guardada en redis)
async def get_sensor_from_redis(sensor_id: str):
    sensor_json = redis_client.get(f"medicion:{sensor_id}")

    if sensor_json:
        sensor_data = json.loads(sensor_json)
        return {
            "sensor_id": sensor_id,
            "sensor_data": sensor_data
        }
    else:
        return {"message": "Sensor no encontrado en la cache"}


@app.post("/saveDataSensorInCache/") #ndpoint para guardar datos en la cache ->  http://localhost:8000/saveDataSensorInCache/
async def saveDataSensorInCache(medicion: SensorMedicion):
  
    cache_id = f"{medicion.sensorId}-{str(uuid.uuid4())}"
    
   
    sensor_json = {
        "sensorId": medicion.sensorId,
        "value": medicion.value,
        "unit": medicion.unit,
        "timestamp": medicion.timestamp
    }

   
    redis_client.set(f"medicion:{cache_id}", json.dumps(sensor_json))

    return {
        "message": "Medición guardada en la cache",
        "cache_id": cache_id,
        "data": sensor_json
    }

@app.post("/volcarDatosRedisAMongo/")  # endpoint para mover los datos de la cache a mongo --> http://localhost:8000/volcarDatosRedisAMongo/
async def flush_all_sensor_data_to_mongo():
    all_sensor_keys = redis_client.keys("medicion:*")  
    
    if not all_sensor_keys:
        raise HTTPException(status_code=404, detail="La cache esta vacia")

    sensor_documents = []

    for key in all_sensor_keys:
        sensor_json = redis_client.get(key)
        if sensor_json:
            measurement_data = json.loads(sensor_json)
            new_sensor_document = {
                "sensorId": measurement_data["sensorId"],
                "mediciones": [
                    {
                        "value": measurement_data["value"],
                        "unit": measurement_data["unit"],
                        "timestamp": measurement_data["timestamp"]
                    }
                ]
            }
            sensor_documents.append(new_sensor_document)
            redis_client.delete(key)  

    if sensor_documents:
        result = mongo_collection.insert_many(sensor_documents)
        return {
            "message": f"{len(sensor_documents)} sensores insertados correctamente en MongoDB",
            "mongo_ids": [str(doc_id) for doc_id in result.inserted_ids]
        }
    else:
                return {"message": "hubo un error a traspasar a mongo"}
        
