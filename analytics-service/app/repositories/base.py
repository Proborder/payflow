from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    model = None
    schema = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_one_or_none(self, **filter_by) -> BaseModel | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.schema.model_validate(model)

    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump())
        await self.session.execute(add_data_stmt)
