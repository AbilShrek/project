import sys
import os
import warnings
import logging

import pytest
from unittest.mock import patch, MagicMock, call

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.threads import Thread, EnergyThread, FormThread, TimeThread
from src.spells import (
    Spell, WeaveSpell, CutSpell, BindSpell,
    LegendaryWeaveSpell, CombinedSpell, Rarity, execute_all
)
from src.artifacts import Artifact, CrystalCore, RuneMatrix
from src.caster import Caster, ArcaneInterface


@pytest.fixture
def basic_thread():
    return Thread("Базовая", frequency=100.0, stability=0.5)

@pytest.fixture
def energy_thread():
    return EnergyThread("Энергия", frequency=200.0, stability=0.8, power_level=2)

@pytest.fixture
def form_thread():
    return FormThread("Форма", frequency=150.0, stability=0.6, shape="cube")

@pytest.fixture
def time_thread():
    return TimeThread("Время", frequency=100.0, stability=0.7, epoch=3)

@pytest.fixture
def weave_spell():
    return WeaveSpell("Плетение", cost=10.0, bond_strength=1.5)

@pytest.fixture
def cut_spell():
    return CutSpell("Разрыв", cost=15.0, severity=0.3, rarity=Rarity.RARE)

@pytest.fixture
def bind_spell():
    return BindSpell("Привязь", cost=8.0, effect="слепота", duration=3)

@pytest.fixture
def legendary_spell():
    return LegendaryWeaveSpell("Легенда", cost=50.0, bond_strength=5.0, amplifier=2.0)

@pytest.fixture
def crystal_core():
    return CrystalCore("Тест Кристалл", durability=50)

@pytest.fixture
def rune_matrix():
    return RuneMatrix("Тест Матрица", capacity=3)

@pytest.fixture
def varn(weave_spell, legendary_spell):
    c = Caster("Варн", energy=200.0)
    c.learn(weave_spell)
    c.learn(legendary_spell)
    return c

@pytest.fixture
def sel(cut_spell, bind_spell):
    c = Caster("Сел", energy=40.0)
    c.learn(cut_spell)
    c.learn(bind_spell)
    return c


class TestThreadEncapsulation:
    def test_thread_happy_path_creation(self, basic_thread):
        assert basic_thread.name == "Базовая"
        assert basic_thread.frequency == 100.0
        assert basic_thread.stability == 0.5

    def test_thread_raises_value_error_on_negative_frequency(self):
        with pytest.raises(ValueError):
            Thread("X", frequency=-1.0, stability=0.5)

    def test_thread_raises_value_error_on_zero_frequency(self):
        with pytest.raises(ValueError):
            Thread("X", frequency=0.0, stability=0.5)

    def test_thread_raises_value_error_on_frequency_too_high(self):
        with pytest.raises(ValueError):
            Thread("X", frequency=1000.0, stability=0.5)

    def test_thread_frequency_boundary_min(self):
        t = Thread("Min", frequency=0.1, stability=0.5)
        assert t.frequency == 0.1

    def test_thread_frequency_boundary_max(self):
        t = Thread("Max", frequency=999.9, stability=0.5)
        assert t.frequency == 999.9

    def test_thread_raises_value_error_on_stability_out_of_range(self):
        with pytest.raises(ValueError):
            Thread("X", frequency=100.0, stability=1.1)

    def test_thread_raises_value_error_on_negative_stability(self):
        with pytest.raises(ValueError):
            Thread("X", frequency=100.0, stability=-0.1)

    def test_thread_stability_boundary_zero(self):
        t = Thread("Zero", frequency=100.0, stability=0.0)
        assert t.stability == 0.0

    def test_thread_stability_boundary_one(self):
        t = Thread("Full", frequency=100.0, stability=1.0)
        assert t.stability == 1.0

    def test_thread_setter_raises_type_error_on_string_frequency(self):
        with pytest.raises(TypeError):
            Thread("X", frequency="fast", stability=0.5)

    def test_thread_setter_raises_type_error_on_string_stability(self):
        with pytest.raises(TypeError):
            Thread("X", frequency=100.0, stability="stable")

    def test_thread_energy_calculation(self, basic_thread):
        assert basic_thread.energy() == pytest.approx(100.0 * 0.5)

    def test_thread_resonate(self, basic_thread):
        other = Thread("Другая", frequency=200.0, stability=0.4)
        result = basic_thread.resonate(other)
        expected = 100.0 * 0.5 + 200.0 * 0.4
        assert result == pytest.approx(expected)

    def test_thread_add_operator(self, basic_thread, form_thread):
        combined = basic_thread + form_thread
        assert isinstance(combined, Thread)
        assert "+" in combined.name

    def test_thread_str_representation(self, basic_thread):
        assert "Базовая" in str(basic_thread)

    def test_thread_repr_representation(self, basic_thread):
        assert "Thread" in repr(basic_thread)

    def test_thread_private_field_not_accessible_directly(self, basic_thread):
        assert not hasattr(basic_thread, '__frequency')
        assert not hasattr(basic_thread, '__stability')


class TestEnergyThread:
    def test_energy_thread_creation(self, energy_thread):
        assert energy_thread.power_level == 2
        assert energy_thread.frequency == 200.0

    def test_energy_thread_resonate_amplified(self, energy_thread, basic_thread):
        result = energy_thread.resonate(basic_thread)
        base = 200.0 * 0.8 + basic_thread.frequency * basic_thread.stability
        assert result == pytest.approx(base * 2)

    def test_energy_thread_invalid_power_level(self):
        with pytest.raises(ValueError):
            EnergyThread("X", 100.0, 0.5, power_level=0)

    def test_energy_thread_str(self, energy_thread):
        assert "Энергия" in str(energy_thread)


class TestFormThread:
    def test_form_thread_shape(self, form_thread):
        assert form_thread.shape == "cube"

    def test_form_thread_resonate_uses_stability_squared(self, form_thread, basic_thread):
        result = form_thread.resonate(basic_thread)
        expected = (150.0 * 0.6**2 + basic_thread.frequency * basic_thread.stability**2)
        assert result == pytest.approx(expected)


class TestTimeThread:
    def test_time_thread_epoch(self, time_thread):
        assert time_thread.epoch == 3

    def test_time_thread_resonate_amplified_by_epoch_diff(self, time_thread):
        other = TimeThread("OtherTime", 100.0, 0.5, epoch=8)
        result = time_thread.resonate(other)
        base = 100.0 * 0.7 + 100.0 * 0.5
        amplifier = 1 + abs(3 - 8) * 0.1
        assert result == pytest.approx(base * amplifier)

    def test_time_thread_resonate_no_diff(self, time_thread, basic_thread):
        result = time_thread.resonate(basic_thread)
        base = 100.0 * 0.7 + basic_thread.frequency * basic_thread.stability
        assert result == pytest.approx(base * 1.0)


class TestSpellBase:
    def test_spell_is_abstract(self):
        with pytest.raises(TypeError):
            Spell("Тест", 10)  # type: ignore

    def test_spell_negative_cost_raises(self):
        with pytest.raises(ValueError):
            WeaveSpell("X", cost=-5.0)

    def test_spell_comparison_by_rarity(self, legendary_spell, weave_spell):
        assert legendary_spell > weave_spell

    def test_spell_comparison_by_cost_same_rarity(self, weave_spell):
        expensive = WeaveSpell("Дорогое", cost=100.0)
        assert expensive > weave_spell

    def test_spell_str(self, weave_spell):
        assert "Плетение" in str(weave_spell)


class TestWeaveSpell:
    def test_weave_cast_reduces_caster_energy(self, weave_spell, varn):
        initial = varn.energy
        weave_spell.cast(varn, "Цель")
        assert varn.energy == initial - weave_spell.cost

    def test_weave_cast_returns_string(self, weave_spell, varn):
        result = weave_spell.cast(varn, "Цель")
        assert isinstance(result, str)
        assert varn.name in result

    def test_weave_describe(self, weave_spell):
        desc = weave_spell.describe()
        assert "Плетение" in desc


class TestCutSpell:
    def test_cut_invalid_severity_zero(self):
        with pytest.raises(ValueError):
            CutSpell("X", 10.0, severity=0.0)

    def test_cut_invalid_severity_over_one(self):
        with pytest.raises(ValueError):
            CutSpell("X", 10.0, severity=1.1)

    def test_cut_cast_result(self, cut_spell, sel):
        result = cut_spell.cast(sel, "Варн")
        assert "разрывает" in result


class TestBindSpell:
    def test_bind_cast_includes_effect(self, bind_spell, sel):
        result = bind_spell.cast(sel, "Варн")
        assert "слепота" in result

    def test_bind_describe(self, bind_spell):
        assert "слепота" in bind_spell.describe()


class TestLegendaryWeaveSpell:
    def test_legendary_rarity(self, legendary_spell):
        assert legendary_spell.rarity == Rarity.LEGENDARY

    def test_legendary_cast_calls_super(self, legendary_spell, varn):
        result = legendary_spell.cast(varn, "Цель")
        assert "ЛЕГЕНДАРНОЕ" in result

    def test_legendary_mro(self):
        mro = [cls.__name__ for cls in LegendaryWeaveSpell.__mro__]
        assert mro[0] == "LegendaryWeaveSpell"
        assert "WeaveSpell" in mro
        assert "Spell" in mro


class TestCombinedSpell:
    def test_combined_total_cost(self, weave_spell, cut_spell):
        combo = CombinedSpell("Комбо", [weave_spell, cut_spell])
        assert combo.cost == weave_spell.cost + cut_spell.cost

    def test_combined_cast_applies_all(self, weave_spell, bind_spell, varn):
        combo = CombinedSpell("Комбо", [weave_spell, bind_spell])
        result = combo.cast(varn, "Цель")
        assert "Плетение" in result
        assert "Привязь" in result

    def test_combined_empty_raises(self):
        with pytest.raises(ValueError):
            CombinedSpell("Пустое", [])

    def test_combined_is_arcane_interface(self, weave_spell, bind_spell):
        combo = CombinedSpell("Комбо", [weave_spell, bind_spell])
        assert isinstance(combo, ArcaneInterface)


class TestCrystalCore:
    def test_crystal_activate_amplifies(self, crystal_core, form_thread):
        energy = form_thread.energy()
        result = crystal_core.activate(form_thread)
        assert result == pytest.approx(energy * 1.5)

    def test_crystal_activate_reduces_durability(self, crystal_core, form_thread):
        before = crystal_core.durability
        crystal_core.activate(form_thread)
        assert crystal_core.durability == before - 2

    def test_crystal_broken_returns_zero(self, form_thread):
        broken = CrystalCore("Сломан", durability=0)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = broken.activate(form_thread)
        assert result == 0.0

    def test_crystal_invalid_durability(self):
        with pytest.raises(ValueError):
            CrystalCore("X", durability=150)

    def test_crystal_is_broken_after_depletion(self, form_thread):
        core = CrystalCore("Core", durability=2)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            core.activate(form_thread)
        assert core.is_broken()


class TestRuneMatrix:
    def test_rune_matrix_store(self, rune_matrix, energy_thread):
        result = rune_matrix.store(energy_thread)
        assert result is True
        assert rune_matrix.stored_count == 1

    def test_rune_matrix_store_overflow(self, rune_matrix, energy_thread, form_thread, time_thread, basic_thread):
        rune_matrix.store(energy_thread)
        rune_matrix.store(form_thread)
        rune_matrix.store(time_thread)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = rune_matrix.store(basic_thread)
        assert result is False
        assert len(w) == 1

    def test_rune_matrix_activate_sums_energy(self, rune_matrix, energy_thread, basic_thread):
        rune_matrix.store(energy_thread)
        result = rune_matrix.activate(basic_thread)
        expected = energy_thread.energy() + basic_thread.energy()
        assert result == pytest.approx(expected)

    def test_rune_matrix_broken(self, basic_thread):
        broken = RuneMatrix("Сломана", durability=0)
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = broken.activate(basic_thread)
        assert result == 0.0

    def test_rune_matrix_invalid_capacity(self):
        with pytest.raises(ValueError):
            RuneMatrix("X", capacity=0)

    def test_rune_matrix_clear(self, rune_matrix, energy_thread):
        rune_matrix.store(energy_thread)
        rune_matrix.clear()
        assert rune_matrix.stored_count == 0


class TestCaster:
    def test_caster_learn_spell(self, varn, weave_spell):
        assert len(varn) >= 1

    def test_caster_len(self, varn):
        assert isinstance(len(varn), int)
        assert len(varn) == 2

    def test_caster_cast_known_spell(self, varn):
        result = varn.cast("Плетение", "Цель")
        assert isinstance(result, str)

    def test_caster_cast_unknown_spell(self, varn):
        result = varn.cast("Несуществующее", "Цель")
        assert "не знает" in result

    def test_caster_cast_insufficient_energy(self):
        poor = Caster("Бедный", energy=0)
        spell = WeaveSpell("Дорогое", cost=100.0)
        poor.learn(spell)
        result = poor.cast("Дорогое", "Цель")
        assert "недостаточно" in result

    def test_caster_forget_spell(self, varn):
        result = varn.forget("Плетение")
        assert result is True
        assert not varn.has_spell("Плетение")

    def test_caster_forget_unknown_spell(self, varn):
        result = varn.forget("Несуществующее")
        assert result is False

    def test_caster_equip_artifact(self, varn, crystal_core):
        varn.equip(crystal_core)
        assert varn.artifact is crystal_core

    def test_caster_equip_warns_on_replace(self, varn, crystal_core, rune_matrix):
        varn.equip(crystal_core)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            varn.equip(rune_matrix)
        assert len(w) == 1
        assert "заменяет" in str(w[0].message)

    def test_caster_negative_energy_raises(self):
        with pytest.raises(ValueError):
            Caster("X", energy=-10)

    def test_caster_str(self, varn):
        assert "Варн" in str(varn)

    def test_caster_repr(self, varn):
        assert "Caster" in repr(varn)

    def test_caster_get_spells(self, varn):
        spells = varn.get_spells()
        assert isinstance(spells, list)
        assert len(spells) == len(varn)

    def test_caster_has_spell_true(self, varn):
        assert varn.has_spell("Плетение")

    def test_caster_has_spell_false(self, varn):
        assert not varn.has_spell("Несуществующее")


class TestLogging:
    def test_invalid_frequency_logs_error(self):
        with patch('src.threads.logger') as mock_logger:
            with pytest.raises(ValueError):
                Thread("X", frequency=-1.0, stability=0.5)
            mock_logger.error.assert_called_once()
            args = mock_logger.error.call_args[0][0]
            assert "out of range" in args or "frequency" in args.lower()

    def test_invalid_stability_logs_error(self):
        with patch('src.threads.logger') as mock_logger:
            with pytest.raises(ValueError):
                Thread("X", frequency=100.0, stability=2.0)
            mock_logger.error.assert_called_once()

    def test_type_error_frequency_logs_error(self):
        with patch('src.threads.logger') as mock_logger:
            with pytest.raises(TypeError):
                Thread("X", frequency="fast", stability=0.5)
            mock_logger.error.assert_called_once()


class TestMocks:
    def test_crystal_activate_mocked(self, basic_thread):
        core = CrystalCore("Мок Кристалл")
        with patch.object(core, 'activate', return_value=99.9) as mock_activate:
            result = core.activate(basic_thread)
            assert result == 99.9
            mock_activate.assert_called_once_with(basic_thread)

    def test_rune_matrix_activate_magic_mock(self, basic_thread):
        matrix = RuneMatrix("Мок Матрица")
        mock_activate = MagicMock(return_value=42.0)
        matrix.activate = mock_activate

        result = matrix.activate(basic_thread)

        assert result == 42.0
        mock_activate.assert_called_once_with(basic_thread)

    def test_spell_cast_side_effect_exception(self, varn):
        spell = WeaveSpell("Взрывное", cost=10.0)
        with patch.object(spell, 'cast', side_effect=RuntimeError("Магия взорвалась!")):
            with pytest.raises(RuntimeError, match="Магия взорвалась!"):
                spell.cast(varn, "Цель")

    def test_artifact_activate_called_multiple_times(self, basic_thread):
        core = CrystalCore("Тест")
        mock_activate = MagicMock(return_value=10.0)
        core.activate = mock_activate

        core.activate(basic_thread)
        core.activate(basic_thread)

        assert mock_activate.call_count == 2

    def test_caster_cast_with_mocked_spell(self, basic_thread):
        caster = Caster("Тест", energy=100)
        mock_spell = MagicMock(spec=Spell)
        mock_spell.name = "МокЗаклинание"
        mock_spell.cost = 5.0
        mock_spell.cast.return_value = "Мок результат"

        caster.learn(mock_spell)
        result = caster.cast("МокЗаклинание", "Цель")

        mock_spell.cast.assert_called_once()
        assert result == "Мок результат"


class TestPolymorphism:
    def test_execute_all_calls_each_spell(self, varn, weave_spell, cut_spell):
        mock1 = MagicMock()
        mock1.cast.return_value = "результат 1"
        mock2 = MagicMock()
        mock2.cast.return_value = "результат 2"

        execute_all([mock1, mock2], varn, "Цель")

        mock1.cast.assert_called_once_with(varn, "Цель")
        mock2.cast.assert_called_once_with(varn, "Цель")

    def test_all_spells_polymorphic_cast(self, weave_spell, cut_spell, bind_spell,
                                         legendary_spell, varn):
        spells = [weave_spell, cut_spell, bind_spell, legendary_spell]
        for spell in spells:
            result = spell.cast(varn, "Цель")
            assert isinstance(result, str)

    def test_arcane_interface_protocol(self, weave_spell):
        assert isinstance(weave_spell, ArcaneInterface)
