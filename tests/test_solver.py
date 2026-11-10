import pytest

from arma3calc import Point, azimuth_mil, distance, get_weapon, interpolate, load_weapons, solve

ORIGIN = Point(1000, 1000, 0)


@pytest.mark.parametrize(
    ("dx", "dy", "expected"),
    [
        (0, 100, 0),  # север — в старой версии здесь получалось 6400
        (100, 100, 800),
        (100, 0, 1600),  # восток
        (100, -100, 2400),
        (0, -100, 3200),  # юг
        (-100, -100, 4000),
        (-100, 0, 4800),  # запад
        (-100, 100, 5600),
    ],
)
def test_azimuth_cardinal_directions(dx, dy, expected):
    assert azimuth_mil(ORIGIN, Point(ORIGIN.x + dx, ORIGIN.y + dy)) == pytest.approx(expected)


def test_azimuth_matches_old_formula_inside_quadrant():
    # Старая формула: asin(dx / r) * 1018.591636, 1-я четверть — 0 + |alpha|
    import math

    dx, dy = 300, 400
    old = math.asin(dx / 500) * 1018.591636
    assert azimuth_mil(ORIGIN, Point(ORIGIN.x + dx, ORIGIN.y + dy)) == pytest.approx(old, abs=1e-3)


def test_distance_ignores_altitude():
    assert distance(Point(0, 0, 0), Point(300, 400, 250)) == pytest.approx(500)


def test_tables_loaded():
    weapons = load_weapons()
    assert set(weapons) == {"2b11", "2b14", "d30a"}
    assert [c.number for c in weapons["2b11"].charges] == list(range(7))
    assert (weapons["2b11"].min_range, weapons["2b11"].max_range) == (485, 7188)
    assert (weapons["2b14"].min_range, weapons["2b14"].max_range) == (100, 4500)
    assert (weapons["d30a"].min_range, weapons["d30a"].max_range) == (950, 15400)


def test_exact_table_row():
    charge0 = get_weapon("2b11").charges[0]
    row = interpolate(charge0, 1250)
    assert (row.elevation_mil, row.d_elev_per_100m, row.time_of_flight_s) == (1045, 71, 20.5)


def test_interpolation_between_rows():
    # 1250 м → 1045, 1300 м → 1004. Для 1270 м: 1045 - 0.4 * 41 = 1028.6
    # (Android-версия выдавала здесь ~988 из-за ошибки в elev_calc).
    charge0 = get_weapon("2b11").charges[0]
    row = interpolate(charge0, 1270)
    assert row.elevation_mil == pytest.approx(1028.6)
    assert row.d_elev_per_100m == pytest.approx(71 + 0.4 * (143 - 71))


def test_last_row_is_inclusive():
    charge0 = get_weapon("2b11").charges[0]
    assert interpolate(charge0, 1416).elevation_mil == 800


def test_interpolate_out_of_range_raises():
    with pytest.raises(ValueError):
        interpolate(get_weapon("2b11").charges[0], 1500)


def test_solve_selects_all_covering_charges():
    target = Point(ORIGIN.x, ORIGIN.y + 1000, 0)
    sol = solve(get_weapon("2b11"), ORIGIN, target)
    assert sol.range_m == pytest.approx(1000)
    assert sol.azimuth_mil == pytest.approx(0)
    assert [c.charge for c in sol.charges] == [0, 1]
    assert sol.charges[0].elevation_mil == 1199


def test_height_correction_sign():
    # 2Б11, заряд 0, 1000 м: возвышение 1199, поправка 26 mil на 100 м высоты.
    weapon = get_weapon("2b11")
    higher = solve(weapon, ORIGIN, Point(ORIGIN.x, ORIGIN.y + 1000, 50)).charges[0]
    lower = solve(weapon, ORIGIN, Point(ORIGIN.x, ORIGIN.y + 1000, -50)).charges[0]
    assert higher.height_correction_mil == pytest.approx(13)
    assert higher.elevation_mil == pytest.approx(1199 - 13)  # цель выше — возвышение меньше
    assert lower.elevation_mil == pytest.approx(1199 + 13)  # цель ниже — возвышение больше
    assert higher.height_correction_known and lower.height_correction_known


def test_height_correction_unknown_near_max_range():
    # У 2Б11 заряд 0 для 1350+ м поправки на высоту в таблице нет.
    weapon = get_weapon("2b11")
    sol = solve(weapon, Point(0, 0, 0), Point(0, 1380, 30))
    ch0 = next(c for c in sol.charges if c.charge == 0)
    assert not ch0.height_correction_known
    assert ch0.elevation_mil == ch0.table_elevation_mil
    flat = solve(weapon, Point(0, 0, 0), Point(0, 1380, 0))
    assert next(c for c in flat.charges if c.charge == 0).height_correction_known


def test_out_of_range():
    sol = solve(get_weapon("2b14"), Point(0, 0), Point(0, 50))
    assert not sol.in_range
    assert solve(get_weapon("2b14"), Point(0, 0), Point(0, 5000)).charges == ()
