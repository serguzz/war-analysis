# src/models/db/repositories/base.py
from typing import Generic, Type, TypeVar, Optional, Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

# Працює з будь-якою моделлю SQLAlchemy
ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get(self, id: int) -> Optional[ModelType]:
        """Отримати один запис за ID."""
        return self.session.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Отримати список записів із пагінацією."""
        statement = select(self.model).offset(skip).limit(limit)
        result = self.session.execute(statement)
        return result.scalars().all()

    def create(self, data: dict) -> ModelType:
        """Створити новий запис."""
        db_obj = self.model(**data)
        self.session.add(db_obj)
        return db_obj

    def update(self, id: int, data: dict) -> Optional[ModelType]:
        """Оновити запис за ID (SQLAlchemy 2.0 стиль)."""
        statement = (
            update(self.model)
            .where(self.model.id == id)
            .values(**data)
            .returning(self.model)
        )
        result = self.session.execute(statement)
        return result.scalar_one_or_none()

    def delete(self, id: int) -> bool:
        """Видалити запис за ID."""
        statement = delete(self.model).where(self.model.id == id)
        result = self.session.execute(statement)
        return result.rowcount > 0
