from fastapi import FastAPI, HTTPException, status, Query,status
from pydantic import BaseModel
from schemas.response import ResponseMessage, ErrorMessage
from db import redis_client, users_collection, products_collection, neo4j_driver
import json
from typing import List

class UserSistem(BaseModel):
   
    name: str
    lastName: str

class ProducSistem(BaseModel):
    
    name: str
    category: str

class VistaProducto(BaseModel):
    user_id: str
    product_id: str
    category_name: str


app = FastAPI()

@app.post("/crearUsuario", status_code=status.HTTP_201_CREATED, response_model=ResponseMessage)
async def agregar_usuario(datos_usuario: UserSistem) -> ResponseMessage:
    try:
       
        usuario = await users_collection.insert_one(datos_usuario.dict())  
        nuevo_usuario = await users_collection.find_one({"_id": usuario.inserted_id})  
        return ResponseMessage[dict](
            success=True,
            message="user agregado ",
            data=user_helper(nuevo_usuario)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from fastapi import status, HTTPException
import json

@app.post("/crearProducto", status_code=status.HTTP_201_CREATED, response_model=ResponseMessage)
async def agregar_producto(datos_producto: ProducSistem) -> ResponseMessage:
    try:
        producto = await products_collection.insert_one(datos_producto.dict())
        nuevo_producto = await products_collection.find_one({"_id": producto.inserted_id})
        product_id = str(nuevo_producto["_id"])

        redis_client.set(product_id, json.dumps(product_helper(nuevo_producto)))

        
        with neo4j_driver.session() as session:
            session.run(
                """
                MERGE (p:Producto {id: $product_id, name: $name})
                MERGE (c:Categoria {name: $category})
                MERGE (p)-[:PERTENECE_A]->(c)
                """,
                product_id=product_id,
                name=nuevo_producto["name"],
                category=nuevo_producto["category"]
            )

        return ResponseMessage[dict](
            success=True,
            message="producto agregado ",
            data=product_helper(nuevo_producto)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.post("/relacionVistaUserProducto", status_code=status.HTTP_201_CREATED, response_model=ResponseMessage)
async def agregar_vista_producto(view_data: VistaProducto) -> ResponseMessage:
    try:
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MERGE (u:Usuario {id: $user_id})
                MERGE (p:Producto {id: $product_id})
                MERGE (c:Categoria {name: $category_name})
                MERGE (u)-[:VIO]->(p)
                MERGE (p)-[:PERTENECE_A]->(c)
                """,
                user_id=view_data.user_id, product_id=view_data.product_id, category_name=view_data.category_name
            )
            return ResponseMessage[dict](
                success=True,
                message="",
                data={"user_id": view_data.user_id, "product_id": view_data.product_id, "category": view_data.category_name}
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.get("/recomendarProductos", status_code=status.HTTP_200_OK, response_model=ResponseMessage[List[dict]])
async def recomendar_productos(user_id: str = Query(...)) -> ResponseMessage[List[dict]]:
    try:
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (u:Usuario {id: $user_id})-[:VIO]->(p:Producto)-[:PERTENECE_A]->(c:Categoria)
                WITH u, c, collect(p) AS productos_vistos
                MATCH (p2:Producto)-[:PERTENECE_A]->(c)
                WHERE NOT (u)-[:VIO]->(p2)
                RETURN p2.id AS producto_id, p2.name AS producto_name, c.name AS categoria
                LIMIT 5
                """,
                user_id=user_id
            )

            recomendaciones = []
            for record in result:
                recomendaciones.append({
                    "producto_id": record["producto_id"],
                    "producto_name": record["producto_name"],
                    "categoria": record["categoria"]
                })

            if not recomendaciones:
                return ResponseMessage[List[dict]](
                    success=False,
                    message="",
                    data=[]
                )

            return ResponseMessage[List[dict]](
                success=True,
                message="",
                data=recomendaciones
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def user_helper(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "lastName": user["lastName"]
    }

def product_helper(product: dict) -> dict:
    return {
        "id": str(product["_id"]),
        "name": product["name"],
        "category": product["category"]
    }

