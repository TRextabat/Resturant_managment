from src.payment.schemas import CreatePaymentRequest
from src.payment.payment_repository import PaymentRepository
from src.models import Payment, Order
from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status


class PaymentService:
    def __init__(self, db: AsyncSession, repo: PaymentRepository):
        self.db = db
        self.repo = repo

    async def create_payment(self, customer_id: UUID | None, request: CreatePaymentRequest) -> Payment:
        # Siparişi getir
        stmt = select(Order).where(Order.id == request.order_id)
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Toplam ödeme kontrolü
        total_paid = await self.repo.get_total_paid_for_order(order.id)
        remaining = order.total_amount - Decimal(total_paid)
        if request.amount > remaining:
            raise HTTPException(
                status_code=400,
                detail=f"Ödeme tutarı kalan bakiyeden fazla: {request.amount} > {remaining}"
            )

        # Ödeme nesnesi oluştur
        payment = Payment(
            order_id=request.order_id,
            customer_id=customer_id,
            amount=request.amount,
            method=request.method,
            is_successful=True  # Bu örnekte doğrudan başarılı sayılıyor
        )

        self.db.add(payment)

        # Gerekirse otomatik olarak order.is_paid = True yap
        if request.amount == remaining:
            order.is_paid = True

        await self.db.commit()
        await self.db.refresh(payment)
        return payment
