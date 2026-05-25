import sys
import os
import warnings

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.threads import EnergyThread, FormThread, TimeThread
from src.spells import (
    WeaveSpell, CutSpell, BindSpell, LegendaryWeaveSpell,
    CombinedSpell, Rarity, execute_all, print_mro
)
from src.artifacts import CrystalCore, RuneMatrix
from src.caster import Caster


def separator(title: str = ""):
    line = "═" * 60
    if title:
        print(f"\n{line}")
        print(f"  {title}")
        print(f"{line}")
    else:
        print(f"\n{line}\n")


def main():
    print("\n" + "★" * 60)
    print("      АРКАНА ПРИМА — КОДЕКС НИТЕЙ")
    print("★" * 60)

    separator("1. НИТИ РЕАЛЬНОСТИ (Инкапсуляция)")

    energy_thread = EnergyThread("Нить Силы", frequency=450.0, stability=0.9, power_level=3)
    form_thread = FormThread("Нить Формы", frequency=300.0, stability=0.7, shape="dragon")
    time_thread = TimeThread("Нить Времени", frequency=200.0, stability=0.85, epoch=5)

    print("Созданные нити:")
    print(f"  {energy_thread}")
    print(f"  {form_thread}")
    print(f"  {time_thread}")

    combined_thread = energy_thread + form_thread
    print(f"\nОбъединение нитей (+): {combined_thread}")

    resonance = energy_thread.resonate(form_thread)
    print(f"Резонанс Нити Силы и Нити Формы: {resonance:.2f}")

    separator("2. ЗАКЛИНАНИЯ (Наследование)")

    weave = WeaveSpell("Плетение Связей", cost=15, bond_strength=2.0)
    cut = CutSpell("Разрыв Оков", cost=20, severity=0.35, rarity=Rarity.RARE)
    bind = BindSpell("Привязь Теней", cost=10, effect="слепота", duration=5)
    legendary = LegendaryWeaveSpell("Великое Плетение", cost=50, bond_strength=5.0, amplifier=3.0)
    combo = CombinedSpell("Шторм Нитей", [weave, cut])

    print("Описания заклинаний:")
    for spell in [weave, cut, bind, legendary, combo]:
        print(f"  {spell}")
        print(f"    → {spell.describe()}")

    print()
    print_mro()

    print(f"\nlegendary > weave: {legendary > weave}")
    print(f"cut > bind: {cut > bind}")

    separator("3. НИТЯРЫ И АРТЕФАКТЫ (Абстракция)")

    varn = Caster("Архимаг Варн", energy=200)
    varn.learn(legendary)
    varn.learn(weave)
    varn.learn(combo)

    sel = Caster("Ученица Сел", energy=40)
    sel.learn(cut)
    sel.learn(bind)

    rune_matrix = RuneMatrix("Матрица Варна", capacity=3)
    rune_matrix.store(energy_thread)
    rune_matrix.store(time_thread)
    varn.equip(rune_matrix)

    crystal = CrystalCore("Кристалл Сел")
    sel.equip(crystal)

    print("\nПроверяем замену артефакта у Варна:")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        varn.equip(CrystalCore("Новый Кристалл"))
        if caught:
            print(f"  ⚠️  Предупреждение: {caught[0].message}")
    varn.equip(rune_matrix)

    varn_energy = varn.artifact.activate(energy_thread)
    sel_energy = sel.artifact.activate(form_thread)
    print(f"\nВарн активирует артефакт: энергия = {varn_energy:.2f}")
    print(f"Сел активирует артефакт: энергия = {sel_energy:.2f}")

    separator("4. ДУЭЛЬ НИТЯРОВ (Полиморфизм)")
    print("  Начинается дуэль между Варном и Сел!\n")

    print("  → Ход Варна:")
    result = varn.cast("Великое Плетение", sel.name)
    print(f"    {result}")

    result = varn.cast("Плетение Связей", sel.name)
    print(f"    {result}")

    print("\n  → Ход Сел:")
    result = sel.cast("Разрыв Оков", varn.name)
    print(f"    {result}")

    result = sel.cast("Привязь Теней", varn.name)
    print(f"    {result}")

    separator("5. EXECUTE_ALL — Duck Typing (Полиморфизм)")

    mixed_spells = [weave, cut, bind, legendary, combo]
    print("  Список смешанных заклинаний (без isinstance!):")
    execute_all(mixed_spells, varn, "Цель")

    separator("6. ИТОГОВЫЙ ОТЧЁТ ДВИЖКА")

    for caster in [varn, sel]:
        print(f"\n{caster}")
        print(f"  Заклинаний в книге (len): {len(caster)}")
        if caster.artifact:
            print(f"  Артефакт: {caster.artifact}")

    print("\n" + "★" * 60)
    print("      ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("★" * 60 + "\n")


if __name__ == "__main__":
    main()
