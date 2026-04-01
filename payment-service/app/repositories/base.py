from pydantic import BaseModel
from sqlalchemy import insert, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ObjectNotFoundException


class BaseRepository:
    model = None
    schema = None
    session: AsyncSession

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

    async def get_all(self, **filter_by) -> list[BaseModel]:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            models = result.scalars().all()
        except NoResultFound as ex:
            raise ObjectNotFoundException from ex
        return [self.schema.model_validate(model, from_attributes=True) for model in models]

    async def add(self, data: BaseModel) -> BaseModel:
        add_data_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_data_stmt)
        model = result.scalar_one()
        return self.schema.model_validate(model, from_attributes=True)

    async def update(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> None:
        update_data_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(update_data_stmt)
