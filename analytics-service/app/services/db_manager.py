from app.repositories.processed_events import ProcessedEventsRepository
from app.repositories.transactions import TransactionsRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.transactions = TransactionsRepository(self.session)
        self.processed_events = ProcessedEventsRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.session.rollback()
        finally:
            await self.session.close()

    async def commit(self):
        await self.session.commit()
