from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import neo4j_driver as driver
from schemas.response import ResponseMessage, ErrorMessage  

endpoint = APIRouter(prefix="/usuario")

class User(BaseModel):
    name: str
    city: str

class AddFriend(BaseModel):
    name1: str
    name2: str

@endpoint.post("/createNodo", response_model=ResponseMessage)
def create_user(req: User):
    try:
        with driver.session() as session:
            session.run(
                "MERGE (u:User {name: $name, city: $city}) RETURN u",
                name=req.name,
                city=req.city
            )
        return ResponseMessage(
            success=True,
            message=f"Usuario '{req.name}' creado",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@endpoint.post("/addFriend", response_model=ResponseMessage)
def make_friends(req: AddFriend):
    try:
        with driver.session() as session:
            session.run("""
                MATCH (a:User {name: $name1})
                MATCH (b:User {name: $name2})
                MERGE (a)-[:FRIEND]->(b)
                MERGE (b)-[:FRIEND]->(a)
            """, name1=req.name1, name2=req.name2)
        return ResponseMessage(
            success=True,
            message=f"{req.name1}  {req.name2} are friends",
            data=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@endpoint.get("/recomendaciones/friend/{name}", response_model=ResponseMessage[list[str]])
def recommend_friends_of_friends(name: str):
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (me:User {name: $name})-[:FRIEND]->(:User)-[:FRIEND]->(fof:User)
                WHERE NOT (me)-[:FRIEND]->(fof) AND fof.name <> $name
                RETURN DISTINCT fof.name AS recommendation
            """, name=name)
            recommendations = [record["recommendation"] for record in result]

        return ResponseMessage(
            success=True,
            message=f"Tal vez conocas a:",
            data=recommendations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



