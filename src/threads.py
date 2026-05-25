import logging

logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Thread:
    FREQUENCY_MIN = 0.1
    FREQUENCY_MAX = 999.9
    STABILITY_MIN = 0.0
    STABILITY_MAX = 1.0

    def __init__(self, name: str, frequency: float, stability: float):
        self.__name = name
        self.frequency = frequency
        self.stability = stability

    @property
    def name(self) -> str:
        return self.__name

    @property
    def frequency(self) -> float:
        return self.__frequency

    @frequency.setter
    def frequency(self, value: float):
        if not isinstance(value, (int, float)):
            msg = f"Frequency must be a number, got {type(value).__name__}"
            logger.error(msg)
            raise TypeError(msg)
        if not (self.FREQUENCY_MIN <= value <= self.FREQUENCY_MAX):
            msg = (f"Frequency {value} out of range "
                   f"[{self.FREQUENCY_MIN}, {self.FREQUENCY_MAX}]")
            logger.error(msg)
            raise ValueError(msg)
        self.__frequency = float(value)

    @property
    def stability(self) -> float:
        return self.__stability

    @stability.setter
    def stability(self, value: float):
        if not isinstance(value, (int, float)):
            msg = f"Stability must be a number, got {type(value).__name__}"
            logger.error(msg)
            raise TypeError(msg)
        if not (self.STABILITY_MIN <= value <= self.STABILITY_MAX):
            msg = (f"Stability {value} out of range "
                   f"[{self.STABILITY_MIN}, {self.STABILITY_MAX}]")
            logger.error(msg)
            raise ValueError(msg)
        self.__stability = float(value)

    def resonate(self, other: 'Thread') -> float:
        return (self.__frequency * self.__stability +
                other.frequency * other.stability)

    def energy(self) -> float:
        return self.__frequency * self.__stability

    def __add__(self, other: 'Thread') -> 'Thread':
        new_freq = min((self.__frequency + other.frequency) / 2,
                       self.FREQUENCY_MAX)
        new_stab = (self.__stability + other.stability) / 2
        return Thread(
            name=f"{self.__name}+{other.name}",
            frequency=new_freq,
            stability=new_stab
        )

    def __repr__(self) -> str:
        return (f"Thread(name={self.__name!r}, "
                f"frequency={self.__frequency:.2f}, "
                f"stability={self.__stability:.2f})")

    def __str__(self) -> str:
        return (f"[Нить '{self.__name}' | "
                f"частота={self.__frequency:.2f} | "
                f"стабильность={self.__stability:.2%}]")


class EnergyThread(Thread):
    def __init__(self, name: str, frequency: float, stability: float,
                 power_level: int = 1):
        super().__init__(name, frequency, stability)
        if not isinstance(power_level, int) or power_level < 1:
            raise ValueError("power_level must be a positive integer")
        self.__power_level = power_level

    @property
    def power_level(self) -> int:
        return self.__power_level

    def resonate(self, other: 'Thread') -> float:
        base = super().resonate(other)
        return base * self.__power_level

    def __repr__(self) -> str:
        return (f"EnergyThread(name={self.name!r}, "
                f"frequency={self.frequency:.2f}, "
                f"stability={self.stability:.2f}, "
                f"power_level={self.__power_level})")

    def __str__(self) -> str:
        return (f"[Нить Энергии '{self.name}' | "
                f"мощь×{self.__power_level} | "
                f"частота={self.frequency:.2f}]")


class FormThread(Thread):
    def __init__(self, name: str, frequency: float, stability: float,
                 shape: str = "sphere"):
        super().__init__(name, frequency, stability)
        self.__shape = shape

    @property
    def shape(self) -> str:
        return self.__shape

    def resonate(self, other: 'Thread') -> float:
        return (self.frequency * self.stability ** 2 +
                other.frequency * other.stability ** 2)

    def __repr__(self) -> str:
        return (f"FormThread(name={self.name!r}, "
                f"frequency={self.frequency:.2f}, "
                f"stability={self.stability:.2f}, "
                f"shape={self.__shape!r})")

    def __str__(self) -> str:
        return (f"[Нить Формы '{self.name}' | "
                f"форма={self.__shape} | "
                f"частота={self.frequency:.2f}]")


class TimeThread(Thread):
    def __init__(self, name: str, frequency: float, stability: float,
                 epoch: int = 0):
        super().__init__(name, frequency, stability)
        self.__epoch = epoch

    @property
    def epoch(self) -> int:
        return self.__epoch

    def resonate(self, other: 'Thread') -> float:
        base = super().resonate(other)
        epoch_other = other.epoch if isinstance(other, TimeThread) else 0
        amplifier = 1 + abs(self.__epoch - epoch_other) * 0.1
        return base * amplifier

    def __repr__(self) -> str:
        return (f"TimeThread(name={self.name!r}, "
                f"frequency={self.frequency:.2f}, "
                f"stability={self.stability:.2f}, "
                f"epoch={self.__epoch})")

    def __str__(self) -> str:
        return (f"[Нить Времени '{self.name}' | "
                f"эпоха={self.__epoch} | "
                f"частота={self.frequency:.2f}]")
