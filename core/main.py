from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

app = FastAPI()

costs_DB = {
    1: {"description": "for test1", "amount": 1.5},
    2: {"description": "for test2", "amount": 324.23},
    3: {"description": "for test3", "amount": 480.65},
}


next_id = max(costs_DB.keys()) + 1 if costs_DB else 1



@app.get("/costs/")
def get_costs():
    return JSONResponse(content=costs_DB, status_code=status.HTTP_200_OK)



@app.get("/cost/{id}/")
def get_cost(id: int):
    if id in costs_DB:
        return JSONResponse(content={"id": id, **costs_DB[id]}, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cost not found")



@app.post("/cost/")
def create_cost(description: str, amount: float):
    global next_id
    new_cost = {"description": description, "amount": amount}
    costs_DB[next_id] = new_cost
    response = {"id": next_id, **new_cost}
    next_id += 1
    return JSONResponse(content=response, status_code=status.HTTP_201_CREATED)



@app.put("/cost/{id}/")
def update_cost(id: int, description: str, amount: float):
    if id in costs_DB:
        costs_DB[id]["description"] = description
        costs_DB[id]["amount"] = amount
        return JSONResponse(content={"message": f"Cost with ID {id} updated successfully"}, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cost not found")



@app.delete("/cost/{id}/")
def delete_cost(id: int):
    if id in costs_DB:
        del costs_DB[id]
        return JSONResponse(content={"message": f"Cost with ID {id} deleted successfully"}, status_code=status.HTTP_200_OK)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cost not found")

