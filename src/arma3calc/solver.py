"""Расчёт данных для стрельбы: дальность, азимут и возвышение для каждого подходящего заряда.

Координаты — метры карты Arma 3: X растёт на восток, Y на север, Z — высота над уровнем моря.
Углы — в тысячных (mil), полный круг 6400.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import dataclass

from .tables import Charge, Row, Weapon

MILS_PER_CIRCLE = 6400


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float = 0.0


@dataclass(frozen=True)
class ChargeSolution:
    charge: int
    elevation_mil: float
    """Итоговое возвышение с поправкой на высоту."""
    table_elevation_mil: float
    """Возвышение из таблицы (интерполированное), без поправки на высоту."""
    height_correction_mil: float
    time_of_flight_s: float | None
    height_correction_known: bool
    """False, если в таблице нет поправки на высоту для этой дальности, а цель выше или ниже орудия."""


@dataclass(frozen=True)
class Solution:
    range_m: float
    azimuth_mil: float
    height_diff_m: float
    charges: tuple[ChargeSolution, ...]

    @property
    def in_range(self) -> bool:
        return bool(self.charges)


def distance(a: Point, b: Point) -> float:
    return math.hypot(b.x - a.x, b.y - a.y)


def azimuth_mil(a: Point, b: Point) -> float:
    """Азимут с A на B в тысячных, от севера по часовой стрелке, в диапазоне [0, 6400)."""
    angle = math.atan2(b.x - a.x, b.y - a.y)
    return (angle / (2 * math.pi) * MILS_PER_CIRCLE) % MILS_PER_CIRCLE


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def interpolate(charge: Charge, range_m: float) -> Row:
    """Линейная интерполяция строки таблицы для произвольной дальности внутри диапазона заряда."""
    if not charge.covers(range_m):
        raise ValueError(f"Дальность {range_m:.0f} м вне диапазона заряда {charge.number}")
    rows = charge.rows
    i = bisect_right([r.range_m for r in rows], range_m) - 1
    if i >= len(rows) - 1:
        return rows[-1]
    lo, hi = rows[i], rows[i + 1]
    t = (range_m - lo.range_m) / (hi.range_m - lo.range_m)
    # Нулевая поправка означает «нет данных», её нельзя смешивать с реальными значениями.
    d_elev = (
        0.0 if lo.d_elev_per_100m == 0 or hi.d_elev_per_100m == 0 else _lerp(lo.d_elev_per_100m, hi.d_elev_per_100m, t)
    )
    tof = None
    if lo.time_of_flight_s is not None and hi.time_of_flight_s is not None:
        tof = _lerp(lo.time_of_flight_s, hi.time_of_flight_s, t)
    return Row(range_m, _lerp(lo.elevation_mil, hi.elevation_mil, t), d_elev, tof)


def solve_charge(charge: Charge, range_m: float, height_diff_m: float) -> ChargeSolution:
    """Цель выше орудия (height_diff_m > 0) — возвышение уменьшается, ниже — увеличивается."""
    row = interpolate(charge, range_m)
    correction = height_diff_m / 100 * row.d_elev_per_100m
    return ChargeSolution(
        charge=charge.number,
        elevation_mil=row.elevation_mil - correction,
        table_elevation_mil=row.elevation_mil,
        height_correction_mil=correction,
        time_of_flight_s=row.time_of_flight_s,
        height_correction_known=row.d_elev_per_100m != 0 or height_diff_m == 0,
    )


def solve(weapon: Weapon, gun: Point, target: Point) -> Solution:
    range_m = distance(gun, target)
    height_diff = target.z - gun.z
    charges = tuple(solve_charge(c, range_m, height_diff) for c in weapon.charges if c.covers(range_m))
    return Solution(
        range_m=range_m,
        azimuth_mil=azimuth_mil(gun, target),
        height_diff_m=height_diff,
        charges=charges,
    )
