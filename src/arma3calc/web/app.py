"""Веб-интерфейс калькулятора: JSON API и одна страница."""

from __future__ import annotations

from importlib import resources

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from arma3calc import Point, get_weapon, load_weapons, solve

STATIC_DIR = resources.files("arma3calc.web") / "static"

app = FastAPI(title="Arma 3 Artillery Calculator", version="0.2.0")


class PointIn(BaseModel):
    x: float = Field(ge=0, le=100_000, description="Восток, м")
    y: float = Field(ge=0, le=100_000, description="Север, м")
    z: float = Field(default=0, ge=-1_000, le=10_000, description="Высота над уровнем моря, м")


class SolveIn(BaseModel):
    weapon: str
    gun: PointIn
    target: PointIn


class ChargeOut(BaseModel):
    charge: int
    elevation_mil: float
    table_elevation_mil: float
    height_correction_mil: float
    time_of_flight_s: float | None
    height_correction_known: bool


class SolveOut(BaseModel):
    weapon: str
    range_m: float
    azimuth_mil: float
    height_diff_m: float
    in_range: bool
    min_range_m: float
    max_range_m: float
    charges: list[ChargeOut]


class ChargeInfo(BaseModel):
    charge: int
    min_range_m: float
    max_range_m: float


class WeaponOut(BaseModel):
    id: str
    name: str
    min_range_m: float
    max_range_m: float
    charges: list[ChargeInfo]


@app.get("/api/weapons", response_model=list[WeaponOut])
def weapons() -> list[WeaponOut]:
    return [
        WeaponOut(
            id=w.id,
            name=w.name,
            min_range_m=w.min_range,
            max_range_m=w.max_range,
            charges=[ChargeInfo(charge=c.number, min_range_m=c.min_range, max_range_m=c.max_range) for c in w.charges],
        )
        for w in load_weapons().values()
    ]


@app.post("/api/solve", response_model=SolveOut)
def solve_endpoint(req: SolveIn) -> SolveOut:
    try:
        weapon = get_weapon(req.weapon)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e.args[0])) from None
    sol = solve(weapon, Point(**req.gun.model_dump()), Point(**req.target.model_dump()))
    return SolveOut(
        weapon=weapon.id,
        range_m=sol.range_m,
        azimuth_mil=sol.azimuth_mil,
        height_diff_m=sol.height_diff_m,
        in_range=sol.in_range,
        min_range_m=weapon.min_range,
        max_range_m=weapon.max_range,
        charges=[ChargeOut(**c.__dict__) for c in sol.charges],
    )


@app.get("/healthz", include_in_schema=False)
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
