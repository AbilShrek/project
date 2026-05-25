from abc import ABC, abstractmethod
from enum import Enum
from typing import List


class Rarity(Enum):
    COMMON = "обычное"
    RARE = "редкое"
    LEGENDARY = "легендарное"


class Spell(ABC):
    def __init__(self, name: str, cost: float, rarity: Rarity = Rarity.COMMON):
        if cost < 0:
            raise ValueError(f"Spell cost cannot be negative, got {cost}")
        self.name = name
        self.cost = cost
        self.rarity = rarity

    @abstractmethod
    def cast(self, caster, target) -> str:
        pass

    @abstractmethod
    def describe(self) -> str:
        pass

    def __gt__(self, other: 'Spell') -> bool:
        rarity_order = {Rarity.COMMON: 0, Rarity.RARE: 1, Rarity.LEGENDARY: 2}
        if rarity_order[self.rarity] != rarity_order[other.rarity]:
            return rarity_order[self.rarity] > rarity_order[other.rarity]
        return self.cost > other.cost

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(name={self.name!r}, "
                f"cost={self.cost}, rarity={self.rarity.value})")

    def __str__(self) -> str:
        return f"[{self.rarity.value.upper()}] {self.name} (стоимость: {self.cost})"


class WeaveSpell(Spell):
    def __init__(self, name: str, cost: float, bond_strength: float = 1.0,
                 rarity: Rarity = Rarity.COMMON):
        super().__init__(name, cost, rarity)
        self.bond_strength = bond_strength

    def cast(self, caster, target) -> str:
        if hasattr(caster, 'energy'):
            caster.energy = max(0, caster.energy - self.cost)
        bond = self.bond_strength * (caster.energy if hasattr(caster, 'energy') else 1)
        return (f"✨ {caster.name} плетёт нить к {target}: "
                f"связь силой {bond:.1f} установлена! "
                f"(осталось энергии: {getattr(caster, 'energy', '?')})")

    def describe(self) -> str:
        return (f"Плетение '{self.name}': соединяет объекты нитью "
                f"прочностью {self.bond_strength}. Стоимость: {self.cost}.")


class CutSpell(Spell):
    def __init__(self, name: str, cost: float, severity: float = 0.2,
                 rarity: Rarity = Rarity.COMMON):
        super().__init__(name, cost, rarity)
        if not (0.0 < severity <= 1.0):
            raise ValueError(f"severity must be in (0, 1], got {severity}")
        self.severity = severity

    def cast(self, caster, target) -> str:
        if hasattr(caster, 'energy'):
            caster.energy = max(0, caster.energy - self.cost)
        return (f"⚔️  {caster.name} разрывает нити {target}: "
                f"стабильность снижена на {self.severity:.0%}! "
                f"(осталось энергии: {getattr(caster, 'energy', '?')})")

    def describe(self) -> str:
        return (f"Разрыв '{self.name}': снижает стабильность цели "
                f"на {self.severity:.0%}. Стоимость: {self.cost}.")


class BindSpell(Spell):
    def __init__(self, name: str, cost: float, effect: str = "замедление",
                 duration: int = 3, rarity: Rarity = Rarity.COMMON):
        super().__init__(name, cost, rarity)
        self.effect = effect
        self.duration = duration

    def cast(self, caster, target) -> str:
        if hasattr(caster, 'energy'):
            caster.energy = max(0, caster.energy - self.cost)
        return (f"🔗 {caster.name} привязывает {target}: "
                f"эффект '{self.effect}' на {self.duration} ходов! "
                f"(осталось энергии: {getattr(caster, 'energy', '?')})")

    def describe(self) -> str:
        return (f"Привязка '{self.name}': накладывает '{self.effect}' "
                f"на {self.duration} ходов. Стоимость: {self.cost}.")


class LegendaryWeaveSpell(WeaveSpell):
    # MRO: LegendaryWeaveSpell → WeaveSpell → Spell → ABC → object
    # Python обходит MRO слева направо при поиске методов.
    # super() в cast() вызывает WeaveSpell.cast(), переиспользуя логику.

    def __init__(self, name: str, cost: float, bond_strength: float = 3.0,
                 amplifier: float = 2.0):
        super().__init__(name, cost, bond_strength, rarity=Rarity.LEGENDARY)
        self.amplifier = amplifier

    def cast(self, caster, target) -> str:
        base_result = super().cast(caster, target)
        return (f"🌟 ЛЕГЕНДАРНОЕ ЗАКЛИНАНИЕ! "
                f"{base_result} [усиление ×{self.amplifier}]")

    def describe(self) -> str:
        return (f"Легендарное Плетение '{self.name}': "
                f"{super().describe()} Усиление ×{self.amplifier}.")


print_mro = lambda: print(
    "MRO LegendaryWeaveSpell:",
    [cls.__name__ for cls in LegendaryWeaveSpell.__mro__]
)


class CombinedSpell(Spell):
    def __init__(self, name: str, spells: List[Spell]):
        if not spells:
            raise ValueError("CombinedSpell requires at least one spell")
        total_cost = sum(s.cost for s in spells)
        max_rarity = max(spells, key=lambda s: list(Rarity).index(s.rarity))
        super().__init__(name, total_cost, max_rarity.rarity)
        self.spells = spells

    def cast(self, caster, target) -> str:
        results = [f"💫 КОМБО '{self.name}':"]
        for spell in self.spells:
            results.append(f"  → {spell.cast(caster, target)}")
        return "\n".join(results)

    def describe(self) -> str:
        spell_names = ", ".join(s.name for s in self.spells)
        return (f"Комбо '{self.name}': [{spell_names}]. "
                f"Суммарная стоимость: {self.cost}.")


def execute_all(spells: list, caster, target) -> None:
    print(f"\n{'='*50}")
    print(f"Выполнение {len(spells)} заклинаний:")
    print(f"{'='*50}")
    for spell in spells:
        result = spell.cast(caster, target)
        print(result)
    print(f"{'='*50}\n")
