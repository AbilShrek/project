from abc import ABC, abstractmethod
from typing import List
import warnings

from src.threads import Thread


class Artifact(ABC):
    MAX_DURABILITY = 100

    def __init__(self, name: str, durability: int = 100):
        if not (0 <= durability <= self.MAX_DURABILITY):
            raise ValueError(
                f"Durability must be in [0, {self.MAX_DURABILITY}], got {durability}"
            )
        self.__durability = durability
        self.name = name

    @property
    def durability(self) -> int:
        return self.__durability

    @durability.setter
    def durability(self, value: int):
        self.__durability = max(0, min(self.MAX_DURABILITY, int(value)))

    def is_broken(self) -> bool:
        return self.__durability <= 0

    @abstractmethod
    def activate(self, thread: Thread) -> float:
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r}, durability={self.__durability})"

    def __str__(self) -> str:
        status = "сломан" if self.is_broken() else f"прочность {self.__durability}%"
        return f"[Артефакт '{self.name}' | {status}]"


class CrystalCore(Artifact):
    AMPLIFY_FACTOR = 1.5
    DURABILITY_COST = 2

    def __init__(self, name: str = "Кристальное Ядро", durability: int = 100):
        super().__init__(name, durability)

    def activate(self, thread: Thread) -> float:
        if self.is_broken():
            warnings.warn(f"Артефакт '{self.name}' сломан и не может быть активирован!")
            return 0.0
        energy = thread.energy() * self.AMPLIFY_FACTOR
        self.durability -= self.DURABILITY_COST
        return energy

    def __str__(self) -> str:
        return (f"[CrystalCore '{self.name}' | "
                f"усиление ×{self.AMPLIFY_FACTOR} | "
                f"прочность {self.durability}%]")


class RuneMatrix(Artifact):
    DURABILITY_COST = 5

    def __init__(self, name: str = "Руническая Матрица",
                 capacity: int = 5, durability: int = 100):
        super().__init__(name, durability)
        if capacity < 1:
            raise ValueError(f"Capacity must be at least 1, got {capacity}")
        self.__capacity = capacity
        self.__stored: List[Thread] = []

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def stored_count(self) -> int:
        return len(self.__stored)

    def store(self, thread: Thread) -> bool:
        if len(self.__stored) >= self.__capacity:
            warnings.warn(f"RuneMatrix '{self.name}' заполнена (ёмкость: {self.__capacity})!")
            return False
        self.__stored.append(thread)
        return True

    def activate(self, thread: Thread) -> float:
        if self.is_broken():
            warnings.warn(f"Артефакт '{self.name}' сломан!")
            return 0.0
        all_threads = self.__stored + [thread]
        total = sum(t.energy() for t in all_threads)
        self.durability -= self.DURABILITY_COST
        return total

    def clear(self):
        self.__stored.clear()

    def __str__(self) -> str:
        return (f"[RuneMatrix '{self.name}' | "
                f"нитей: {len(self.__stored)}/{self.__capacity} | "
                f"прочность {self.durability}%]")
