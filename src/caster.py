import warnings
from typing import Optional, runtime_checkable
try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol  # pragma: no cover

from src.spells import Spell
from src.artifacts import Artifact


@runtime_checkable
class ArcaneInterface(Protocol):
    def cast(self, caster, target) -> str: ...
    def describe(self) -> str: ...


class Caster:
    def __init__(self, name: str, energy: float,
                 artifact: Optional[Artifact] = None):
        if energy < 0:
            raise ValueError(f"Energy cannot be negative, got {energy}")
        self.name = name
        self.energy = energy
        self.artifact = artifact
        self.__spell_book: dict[str, Spell] = {}

    def learn(self, spell: Spell) -> None:
        self.__spell_book[spell.name] = spell
        print(f"📖 {self.name} выучил заклинание '{spell.name}'.")

    def forget(self, spell_name: str) -> bool:
        if spell_name in self.__spell_book:
            del self.__spell_book[spell_name]
            print(f"💨 {self.name} забыл заклинание '{spell_name}'.")
            return True
        print(f"⚠️  У {self.name} нет заклинания '{spell_name}'.")
        return False

    def cast(self, spell_name: str, target) -> str:
        if spell_name not in self.__spell_book:
            return f"❌ {self.name} не знает заклинания '{spell_name}'!"
        spell = self.__spell_book[spell_name]
        if self.energy < spell.cost:
            return (f"❌ У {self.name} недостаточно энергии! "
                    f"(нужно {spell.cost}, есть {self.energy})")
        return spell.cast(self, target)

    def equip(self, artifact: Artifact) -> None:
        if self.artifact is not None:
            warnings.warn(
                f"⚠️  {self.name} заменяет '{self.artifact.name}' "
                f"на '{artifact.name}'!"
            )
        self.artifact = artifact
        print(f"🔮 {self.name} экипировал артефакт '{artifact.name}'.")

    def get_spells(self) -> list:
        return list(self.__spell_book.values())

    def has_spell(self, spell_name: str) -> bool:
        return spell_name in self.__spell_book

    def __len__(self) -> int:
        return len(self.__spell_book)

    def __repr__(self) -> str:
        return (f"Caster(name={self.name!r}, energy={self.energy}, "
                f"spells={len(self)}, artifact={self.artifact})")

    def __str__(self) -> str:
        artifact_str = str(self.artifact) if self.artifact else "нет артефакта"
        return (f"🧙 Нитяр '{self.name}' | "
                f"энергия={self.energy} | "
                f"заклинаний={len(self)} | "
                f"{artifact_str}")
