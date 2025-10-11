from fastapi import FastAPI
from core.costs.routes import router as costs_routes
from core.users.routes import router as users_routs
app = FastAPI(
    title="Cost Management API",             
    description="An API for managing and tracking costs in your application.",  
    version="0.0.1",                        
    terms_of_service="https://example.com/terms/",  
    contact={                                
        "name": "Maryam Kalantari",
        "url": "https://maryamkalantarii.github.io/",
        "email": "you@example.com",
    },
    license_info={                           
        "name": "MIT License",
    },
)


# add routes
app.include_router(costs_routes,prefix="/api/V1")
app.include_router(users_routs,prefix="/api/V1")