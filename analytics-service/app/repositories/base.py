from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ObjectNotFoundException


class BaseRepository:
    model = None
    schema = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_one(self, **filter_by) -> BaseModel:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound as ex:
            raise ObjectNotFoundException from ex
        return self.schema.model_validate(model, from_attributes=True)

    async def get_one_or_none(self, **filter_by) -> BaseModel | None:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.schema.model_validate(model, from_attributes=True)

    async def get_filtered(self, *filter, **filter_by) -> list[BaseModel | None]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs) -> list[BaseModel | None]:
        return await self.get_filtered(*args, **kwargs)

    async def add(self, data: BaseModel):
        add_data_stmt = insert(self.model).values(**data.model_dump())
        await self.session.execute(add_data_stmt)
