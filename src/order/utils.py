from decimal import Decimal
from typing import List
from order.schemas import OrderItemCreate


def calculate_total_amount(items: List[OrderItemCreate]) -> Decimal:
    """Sipariş toplam tutarını hesaplar."""
    return sum(item.unit_price * item.quantity for item in items)


def format_item_summary(items: List[OrderItemCreate]) -> str:
    """Sipariş kalemlerini metin olarak özetler (ör: mutfak bildirimi için)."""
    return ", ".join(f"{item.quantity}x {item.item_name}" for item in items)


def validate_item_prices(items: List[OrderItemCreate]):
    """Ürünlerin fiyatlarının negatif olmamasını kontrol eder."""
    for item in items:
        if item.unit_price < 0:
            raise ValueError(f"'{item.item_name}' has a negative price: {item.unit_price}")
