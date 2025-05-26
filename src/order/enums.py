from enum import Enum
class OrderStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    SERVED = "served"
    PAID = "paid"
    CANCELED = "canceled"
