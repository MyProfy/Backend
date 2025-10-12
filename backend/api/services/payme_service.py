from Backend.backend.config import settings

from payme import Payme
from payme.models import PaymeTransactions

from Backend.backend.api.models import Order

payme = Payme(
    payme_id=settings.PAYME_ID
)

class PaymeService:

    @staticmethod
    def successfully_payment(params):
        transaction = PaymeTransactions.get_by_transaction_id(
            transaction_id=params["id"]
        )

        order = Order.objects.get(id=transaction.account_id)
        order.status = "Completed"
        order.save()

    @staticmethod
    def canceled_payment(params):
        transaction = PaymeTransactions.get_by_transaction_id(
            transaction_id=params["id"]
        )

        if transaction.state == PaymeTransactions.CANCELED:
            order = Order.objects.get(id=transaction.account_id)
            if order:
                order.status = "Cancelled"
                order.save()