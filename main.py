from fastapi import FastAPI
from uvicorn import run
from pydantic import BaseModel
from typing import Annotated

from fastapi import Depends, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Given that the container hosting the database is named postgres, postgres-db is used as the uri.
engine = create_engine(
    "postgresql://myuser:mypassword@postgres-db:5432/mydb",
)


class Hero(SQLModel, table=True):
    __table_args__ = {
        "extend_existing": True
    }  # Allows modification of 'users' table if it already exists
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)
    secret_name: str


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

SQLModel.metadata.create_all(engine)


@app.post("/heroes/")
def create_hero(hero: Hero, session: SessionDep) -> Hero:
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


@app.get("/heroes/")
def read_heroes(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Hero]:
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return list(heroes)


class Data(BaseModel):
    name: str
    email: str


@app.get("/")
def root():
    return Data(name="john", email="johndoe@gmail.com")


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.get("/plaintext")
def plaintext() -> str:
    return "Hello world"


@app.post("/post_data")
def post_data(data: Data):
    print(data)
    return data
