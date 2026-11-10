import pytest
from fastapi.testclient import TestClient

from arma3calc.web.app import app

client = TestClient(app)


def test_weapons():
    r = client.get("/api/weapons")
    assert r.status_code == 200
    ids = {w["id"] for w in r.json()}
    assert ids == {"2b11", "2b14", "d30a"}


def test_solve():
    r = client.post(
        "/api/solve",
        json={"weapon": "2b11", "gun": {"x": 1000, "y": 1000, "z": 0}, "target": {"x": 1000, "y": 2000, "z": 50}},
    )
    assert r.status_code == 200
    d = r.json()
    assert d["range_m"] == pytest.approx(1000)
    assert d["in_range"] is True
    assert [c["charge"] for c in d["charges"]] == [0, 1]
    assert d["charges"][0]["elevation_mil"] == pytest.approx(1199 - 13)


def test_solve_unknown_weapon():
    r = client.post("/api/solve", json={"weapon": "nope", "gun": {"x": 0, "y": 0}, "target": {"x": 0, "y": 500}})
    assert r.status_code == 404


def test_solve_validation():
    r = client.post("/api/solve", json={"weapon": "2b11", "gun": {"x": -5, "y": 0}, "target": {"x": 0, "y": 500}})
    assert r.status_code == 422


def test_index_and_static():
    assert client.get("/").status_code == 200
    assert client.get("/static/manifest.webmanifest").status_code == 200
