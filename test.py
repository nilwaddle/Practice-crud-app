
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "postgresql://nil.waddle:nil2020@db:5432/test_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ItemModel(Base):
    __tablename__ = "table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    title = Column(String, index=True, nullable=True)

class Item(BaseModel):
    id: int
    name: str
    title: str = None

    class Config:
        orm_mode = True

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items/", response_model=Item)
def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[Item])
def read_items(db: Session = Depends(get_db)):
    return db.query(ItemModel).all()

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = updated_item.name
    item.title = updated_item.title
    db.commit()
    db.refresh(item)
    return item

@app.delete("/items/{item_id}", response_model=Item)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return item

# @app.post("/items/", response_model=Item)
# def create_item(item: Item):
#     items.append(item)
#     return item

# @app.get("/items/", response_model=List[Item])
# def read_items():
#     return items

# @app.put("/items/{item_id}", response_model=Item)
# def update_item(item_id: int, updated_item: Item):
#     for index, item in enumerate(items):
#         if item.id == item_id:
#             items[index] = updated_item
#             return updated_item
#     raise HTTPException(status_code=404, detail="Item not found")

# @app.delete("/items/{item_id}", response_model=Item)
# def delete_item(item_id: int):
#     for index, item in enumerate(items):
#         if item.id == item_id:
#             deleted_item = items.pop(index)
#             return deleted_item
#     raise HTTPException(status_code=404, detail="Item not found")
