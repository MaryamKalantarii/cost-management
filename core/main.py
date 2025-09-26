from fastapi import FastAPI, HTTPException, status
from typing import Dict
from schemas import *

app = FastAPI(title="Cost Management API")



# -------------------------
# DATABASE
# -------------------------
costs_DB: Dict[int, CostBase] = {
    1: CostBase(description="for test1", amount=1.5),
    2: CostBase(description="for test2", amount=324.23),
    3: CostBase(description="for test3", amount=480.65),
}

next_id = max(costs_DB.keys()) + 1 if costs_DB else 1

# -------------------------
# CRUD Routes
# -------------------------

@app.get("/costs/", response_model=Dict[int, CostBase])
def get_costs():
    return costs_DB


@app.get("/cost/{id}/", response_model=CostResponse)
def get_cost(id: int):
    if id in costs_DB:
        return CostResponse(id=id, **costs_DB[id].dict())
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cost not found")


@app.post("/cost/", response_model=CostResponse, status_code=status.HTTP_201_CREATED)
def create_cost(cost: CostCreate):
    global next_id
    costs_DB[next_id] = cost
    response = CostResponse(id=next_id, **cost.dict())
    next_id += 1
    return response


@app.put("/cost/{id}/", response_model=CostResponse)
def update_cost(id: int, cost: CostUpdate):
    if id in costs_DB:
        costs_DB[id] = cost
        return CostResponse(id=id, **cost.dict())
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cost not found")


@app.delete("/cost/{id}/", status_code=status.HTTP_200_OK)
def delete_cost(id: int):
    if id in costs_DB:
        del costs_DB[id]
        return {"message": f"Cost with ID {id} deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cost not found")
