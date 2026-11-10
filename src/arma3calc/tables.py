"""Таблицы стрельбы орудий (мод RHS для Arma 3).

Каждое орудие описано JSON-файлом в каталоге ``data/``. Строка таблицы:
``[дальность_м, возвышение_mil, поправка_mil_на_100м_высоты, (время_полёта_с)]``.
Нулевая поправка на высоту означает, что в таблице её нет (обычно у предельных дальностей).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from importlib import resources
from itertools import pairwise


@dataclass(frozen=True)
class Row:
    range_m: float
    elevation_mil: float
    d_elev_per_100m: float
    time_of_flight_s: float | None = None


@dataclass(frozen=True)
class Charge:
    number: int
    rows: tuple[Row, ...]

    @property
    def min_range(self) -> float:
        return self.rows[0].range_m

    @property
    def max_range(self) -> float:
        return self.rows[-1].range_m

    def covers(self, range_m: float) -> bool:
        return self.min_range <= range_m <= self.max_range


@dataclass(frozen=True)
class Weapon:
    id: str
    name: str
    charges: tuple[Charge, ...]

    @property
    def min_range(self) -> float:
        return min(c.min_range for c in self.charges)

    @property
    def max_range(self) -> float:
        return max(c.max_range for c in self.charges)


def _parse(doc: dict) -> Weapon:
    charges = []
    for ch in doc["charges"]:
        rows = tuple(Row(*r) for r in ch["rows"])
        ranges = [r.range_m for r in rows]
        if len(rows) < 2 or any(a >= b for a, b in pairwise(ranges)):
            raise ValueError(f"{doc['id']}: заряд {ch['charge']} — дальности должны строго возрастать")
        charges.append(Charge(number=ch["charge"], rows=rows))
    return Weapon(id=doc["id"], name=doc["name"], charges=tuple(sorted(charges, key=lambda c: c.number)))


@cache
def load_weapons() -> dict[str, Weapon]:
    """Загружает все орудия из ``data/*.json``; ключ — id орудия."""
    weapons = {}
    for entry in sorted(resources.files("arma3calc.data").iterdir(), key=lambda p: p.name):
        if entry.name.endswith(".json"):
            weapon = _parse(json.loads(entry.read_text(encoding="utf-8")))
            weapons[weapon.id] = weapon
    return weapons


def get_weapon(weapon_id: str) -> Weapon:
    try:
        return load_weapons()[weapon_id]
    except KeyError:
        raise KeyError(f"Неизвестное орудие: {weapon_id}") from None
