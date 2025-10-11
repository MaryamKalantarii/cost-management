from fastapi import FastAPI, Depends, HTTPException, status,APIRouter
from sqlalchemy.orm import Session
from core.costs import models, schemas
from core.core import database
from core.core.database import get_db 

router = APIRouter(tags=["costs"])

models.Base.metadata.create_all(bind=database.engine)




@router.post("/cost/", response_model=schemas.CostResponse, status_code=status.HTTP_201_CREATED)
async def create_cost(cost: schemas.CostCreate, db: Session = Depends(get_db)):
    db_cost = models.Cost(description=cost.description, amount=cost.amount)
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost


@router.get("/costs/", response_model=list[schemas.CostResponse])
async def get_costs(db: Session = Depends(get_db)):
    return db.query(models.Cost).all()


@router.get("/cost/{id}/", response_model=schemas.CostResponse)
async def get_cost(id: int, db: Session = Depends(get_db)):
    cost = db.query(models.Cost).filter(models.Cost.id == id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    return cost


@router.put("/cost/{id}/", response_model=schemas.CostResponse)
async def update_cost(id: int, updated: schemas.CostUpdate, db: Session = Depends(get_db)):
    cost = db.query(models.Cost).filter(models.Cost.id == id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    cost.description = updated.description
    cost.amount = updated.amount
    db.commit()
    db.refresh(cost)
    return cost


@router.delete("/cost/{id}/", status_code=200)
async def delete_cost(id: int, db: Session = Depends(get_db)):
    cost = db.query(models.Cost).filter(models.Cost.id == id).first()
    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found")
    db.delete(cost)
    db.commit()
    return {"message": f"Cost with ID {id} deleted successfully"}
