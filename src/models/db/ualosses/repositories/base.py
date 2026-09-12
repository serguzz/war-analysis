# src/models/db/repositories/base.py
from typing import Generic, Type, TypeVar, Optional, Sequence
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

# Працює з будь-якою моделлю SQLAlchemy
ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get(self, id: UUID) -> Optional[ModelType]:
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

    def update(self, id: UUID, data: dict) -> Optional[ModelType]:
        """Оновити запис за ID (SQLAlchemy 2.0 стиль)."""
        db_obj = self.session.get(self.model, id)
        if db_obj is None:
            return None
        
        for field, value in data.items():
            setattr(db_obj, field, value)

        return db_obj

    def delete(self, id: UUID) -> bool:
        """Видалити запис за ID."""
        db_obj = self.session.get(self.model, id)

        if db_obj is None:
            return False

        self.session.delete(db_obj)
        return True
