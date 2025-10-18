from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.auth.jwt_auth import get_authenticated_user
from core.costs import models, schemas
from core.core.database import get_db
from core.users.models import UserModel

router = APIRouter(tags=["costs"], prefix="/costs")


@router.post("/", response_model=schemas.CostResponse, status_code=status.HTTP_201_CREATED)
async def create_cost(
    cost: schemas.CostCreate,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user)
):
    """
    Create a new cost entry for the authenticated user.
    Only authenticated users can create costs.
    """
    db_cost = models.Cost(
        description=cost.description,
        amount=cost.amount,
        user_id=user.id  # link cost to user
    )
    db.add(db_cost)
    db.commit()
    db.refresh(db_cost)
    return db_cost


@router.get("/", response_model=list[schemas.CostResponse])
async def get_costs(
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user)
):
    """
    Return all costs that belong to the authenticated user.
    """
    return db.query(models.Cost).filter(models.Cost.user_id == user.id).all()


@router.get("/{id}/", response_model=schemas.CostResponse)
async def get_cost(
    id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user)
):
    """
    Get a specific cost by ID, only if it belongs to the authenticated user.
    """
    cost = db.query(models.Cost).filter(
        models.Cost.id == id,
        models.Cost.user_id == user.id
    ).first()

    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found or not owned by this user")

    return cost


@router.put("/{id}/", response_model=schemas.CostResponse)
async def update_cost(
    id: int,
    updated: schemas.CostUpdate,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user)
):
    """
    Update a cost if it belongs to the authenticated user.
    """
    cost = db.query(models.Cost).filter(
        models.Cost.id == id,
        models.Cost.user_id == user.id
    ).first()

    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found or not owned by this user")

    cost.description = updated.description
    cost.amount = updated.amount
    db.commit()
    db.refresh(cost)
    return cost


@router.delete("/{id}/", status_code=status.HTTP_200_OK)
async def delete_cost(
    id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user)
):
    """
    Delete a cost if it belongs to the authenticated user.
    """
    cost = db.query(models.Cost).filter(
        models.Cost.id == id,
        models.Cost.user_id == user.id
    ).first()

    if not cost:
        raise HTTPException(status_code=404, detail="Cost not found or not owned by this user")

    db.delete(cost)
    db.commit()
    return {"message": f"Cost with ID {id} deleted successfully"}
