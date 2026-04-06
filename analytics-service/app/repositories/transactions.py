from app.models.transactions import TransactionsOrm
from app.repositories.base import BaseRepository
from app.schemas.transactions import Transaction


class TransactionsRepository(BaseRepository):
    model = TransactionsOrm
    schema = Transaction
