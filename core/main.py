from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core import models,database,schemas

app = FastAPI("Cost Management API")

models.Base.metadata.create_all(bind=database.engine)


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------- CRUD -------------------

@app.post("/cost/", response_model=schemas.CostResponse, status_code=status.HTTP_201_CREATED)
def create_cost(cost: schemas.CostCreate, db: Session = Depends(get_db)):
    db_cost = models.Cost(description=cost.description, amount=cost.amount)
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost


@app.get("/costs/", response_model=list[schemas.CostResponse])
def get_costs(db: Session = Depends(get_db)):
    return db.query(models.Cost).all()


@app.get("/cost/{id}/", response_model=schemas.CostResponse)
def get_cost(id: int, db: Session = Depends(get_db)):
    cost = db.query(models.Cost).filter(models.Cost.id == id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    return cost


@app.put("/cost/{id}/", response_model=schemas.CostResponse)
def update_cost(id: int, updated: schemas.CostUpdate, db: Session = Depends(get_db)):
    cost = db.query(models.Cost).filter(models.Cost.id == id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    cost.description = updated.description
    cost.amount = updated.amount
    db.commit()
    db.refresh(cost)
    return cost


@app.delete("/cost/{id}/", status_code=200)
def delete_cost(id: int, db: Session = Depends(get_db)):
    cost = db.query(models.Cost).filter(models.Cost.id == id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    db.delete(cost)
    db.commit()
    return {"message": f"Cost with ID {id} deleted successfully"}
