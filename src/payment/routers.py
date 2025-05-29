from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.dependencies import get_db
from src.dependencies import get_current_user
from src.models import User

from src.payment.schemas import CreatePaymentRequest, PaymentResponse
from src.payment.payment_repository import PaymentRepository
from src.payment.services import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    request: CreatePaymentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    repo = PaymentRepository(db)
    service = PaymentService(db, repo)
    return await service.create_payment(customer_id=user.id, request=request)
