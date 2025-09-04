"""Base repository for database operations."""

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    """Base repository interface for CRUD operations."""

    @abstractmethod
    async def find_by_id(self, entity_id: Any) -> Optional[T]:
        """Find entity by ID."""
        pass

    @abstractmethod
    async def get_all(self, **filters) -> List[T]:
        """Get all entities with optional filters."""
        pass

    @abstractmethod
    async def delete(self, entity_id: Any) -> bool:
        """Delete entity by ID."""
        pass

    @abstractmethod
    async def update(self, entity_id: Any, entity: T) -> Optional[T]:
        """Update entity by ID."""
        pass
