from app.repositories.outbox import OutboxRepository
from app.repositories.payments import PaymentsRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.payments = PaymentsRepository(self.session)
        self.outbox = OutboxRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.session.rollback()
        finally:
            await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def refresh(self, data):
        await self.session.refresh(data)

    async def flush(self):
        await self.session.flush()

