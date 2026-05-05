from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from user_service.app.db.session import get_db
from user_service.app.services.user_service import UserService
from user_service.app.schemas import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        return await service.create_user(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    try:
        return await service.update_user(user_id, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))