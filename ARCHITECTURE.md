# ARCHITECTURE.md — Кодекс Нитей: Архитектура системы

## Обзор системы

«Кодекс Нитей» — магический движок мира Аркана Прима.
Реализует все четыре принципа ООП через конкретные слои архитектуры.

---

## Принципы ООП → Слои системы

| Принцип       | Слой            | Файл            |
|---------------|-----------------|-----------------|
| Инкапсуляция  | Нити            | `threads.py`    |
| Наследование  | Заклинания      | `spells.py`     |
| Полиморфизм   | Заклинания      | `spells.py`     |
| Абстракция    | Артефакты/Маги  | `artifacts.py`, `caster.py` |

---

## Иерархия классов

```
object
│
├── Thread                  ← Инкапсуляция (__frequency, __stability)
│   ├── EnergyThread        ← +power_level, resonate() ×power_level
│   ├── FormThread          ← +shape, resonate() с stability²
│   └── TimeThread          ← +epoch, resonate() с усилением по эпохам
│
├── Spell (ABC)             ← Абстракция + Наследование
│   ├── WeaveSpell          ← bond_strength, cast() плетёт связь
│   │   └── LegendaryWeaveSpell  ← amplifier, super().cast() + усиление
│   ├── CutSpell            ← severity, cast() снижает стабильность
│   ├── BindSpell           ← effect, duration, постоянный эффект
│   └── CombinedSpell       ← Composite: список spell, cast() применяет все
│
├── Artifact (ABC)          ← Абстракция (activate() скрывает детали)
│   ├── CrystalCore         ← ×1.5, -2 durability за активацию
│   └── RuneMatrix          ← накапливает нити, суммирует при activate()
│
└── Caster                  ← Инкапсуляция (__spell_book)
    └── ArcaneInterface     ← Protocol (duck typing без наследования)
```

---

## Описание принципов в коде

### 1. Инкапсуляция (`Thread`, `Caster`)
- `Thread.__frequency`, `Thread.__stability`, `Caster.__spell_book` — приватные поля
- Доступ только через `@property` с валидацией в сеттерах
- При некорректных значениях поднимается `ValueError`/`TypeError`

### 2. Наследование (`Spell` → конкретные заклинания)
- `Spell` — абстрактный базовый класс с `@abstractmethod cast()` и `describe()`
- `WeaveSpell`, `CutSpell`, `BindSpell` — конкретные реализации
- `LegendaryWeaveSpell(WeaveSpell)` — вызывает `super().cast()` для переиспользования
- MRO: `LegendaryWeaveSpell → WeaveSpell → Spell → ABC → object`

### 3. Полиморфизм (`cast()`)
- Единый метод `cast(caster, target)` вызывается у разных типов заклинаний
- `execute_all()` работает через duck typing — без `isinstance()`
- `CombinedSpell` ведёт себя полиморфно как одиночное заклинание

### 4. Абстракция (`Artifact`, `ArcaneInterface`)
- `Artifact` — абстрактный класс, скрывает детали активации за `activate()`
- `ArcaneInterface` — `typing.Protocol`: duck typing без явного наследования
- Пользователь вызывает только публичный API, не зная внутренней реализации

---

## Связи между модулями

```
main.py
  ├── threads.py   (EnergyThread, FormThread, TimeThread)
  ├── spells.py    (WeaveSpell, CutSpell, BindSpell, LegendaryWeaveSpell, CombinedSpell)
  ├── artifacts.py (CrystalCore, RuneMatrix)  — зависит от threads.py
  └── caster.py    (Caster, ArcaneInterface)  — зависит от spells.py, artifacts.py
```
