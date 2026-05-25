# Аркана Прима — Кодекс Нитей

Комплексное учебное задание: ООП · Автотестирование · CI/CD

GitHub: https://github.com/AbilShrek/project

## Структура проекта

```
arcana_prima/
├── src/
│   ├── threads.py      # Нити (Инкапсуляция)
│   ├── spells.py       # Заклинания (Наследование + Полиморфизм)
│   ├── artifacts.py    # Артефакты (Абстракция)
│   ├── caster.py       # Нитяр (Абстракция + Инкапсуляция)
│   └── main.py         # Демо-сценарий
├── tests/
│   └── test_algorithms.py
├── .github/workflows/ci.yml
├── requirements.txt
├── ARCHITECTURE.md
└── README.md
```

## Запуск

```bash
# Демонстрация
python src/main.py

# Тесты
pytest tests/ -v

# Покрытие
coverage run -m pytest tests/
coverage report -m
coverage html

# HTML-отчёт
pytest --html=report.html --self-contained-html
```

## Принципы ООП

| Принцип | Класс | Как реализован |
|---------|-------|---------------|
| Инкапсуляция | `Thread` | `__frequency`, `__stability` + `@property` |
| Наследование | `Spell` → `WeaveSpell` → `LegendaryWeaveSpell` | Иерархия + `super()` |
| Полиморфизм | Все заклинания | `cast()` + `execute_all()` duck typing |
| Абстракция | `Artifact`, `ArcaneInterface` | ABC + Protocol |
