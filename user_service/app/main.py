from fastapi import FastAPI
from user_service.app.api.users import router as user_router

app = FastAPI(title="User Service")

app.include_router(user_router)