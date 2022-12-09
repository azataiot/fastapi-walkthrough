# sqlm / main.py
# Created by azat at 9.12.2022

from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


# =========== Team Models ============

class TeamBase(SQLModel):
    name: str = Field(index=True)
    headquarters: str


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")


class TeamCreate(TeamBase):
    pass


class TeamRead(TeamBase):
    id: int


class TeamUpdate(SQLModel):
    name: str | None = None
    headquarters: str | None = None


# =========== Hero Models ============

class HeroBase(SQLModel):
    name: str = Field(index=True, unique=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    team_id: int | None = Field(default=None, foreign_key="team.id")


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    team: Team | None = Relationship(back_populates="heroes")


# class Hero(SQLModel, table=True):
#     #  because this same SQLModel object is not only a Pydantic model instance but also a SQLAlchemy model instance,
#     #  we can use it directly in a session to create the row in the database.
#     id: int | None = Field(default=None, primary_key=True)
#     name: str = Field(index=True)
#     secret_name: str
#     age: int | None = Field(default=None, index=True)


# class HeroCreate(SQLModel):
#     name: str
#     secret_name: str
#     age: int | None = None

class HeroCreate(HeroBase):
    pass


# class HeroRead(SQLModel):
#     id: int
#     name: str
#     secret_name: str
#     age: int | None = None

class HeroRead(HeroBase):
    id: int


class HeroUpdate(SQLModel):
    name: str | None = None
    secret_name: str | None = None
    age: int | None = None
    team_id: int | None = None


# =========== Models with Relationship ===========
class HeroReadWithTeam(HeroRead):
    # The HeroReadWithTeam inherits from HeroRead, which means that it will have the normal fields for reading,
    # including the required id that was declared in HeroRead.
    # And then it adds the new field team, which could be None, and is declared with the type TeamRead
    # with the base fields for reading a team.
    team: TeamRead | None = None


class TeamReadWithHeroes(TeamRead):
    # Then we do the same for the TeamReadWithHeroes, it inherits from TeamRead, and declares the new field heroes,
    # which is a list of HeroRead.
    heroes: list["HeroRead"] = []


sqlite_file_name = "simple_hero.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# =========== Team Endpoints ============
@app.post("/teams/", response_model=TeamRead)
def create_team(*, session: Session = Depends(get_session), team: TeamCreate):
    db_team = Team.from_orm(team)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@app.get("/teams/", response_model=list[TeamRead])
def read_teams(
        *,
        session: Session = Depends(get_session),
        offset: int = 0,
        limit: int = Query(default=100, lte=100),
):
    teams = session.exec(select(Team).offset(offset).limit(limit)).all()
    return teams


@app.get("/teams/{team_id}", response_model=TeamReadWithHeroes)
def read_team(*, team_id: int, session: Session = Depends(get_session)):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@app.patch("/teams/{team_id}", response_model=TeamRead)
def update_team(
        *,
        session: Session = Depends(get_session),
        team_id: int,
        team: TeamUpdate,
):
    db_team = session.get(Team, team_id)
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    team_data = team.dict(exclude_unset=True)
    for key, value in team_data.items():
        setattr(db_team, key, value)
    session.add(db_team)
    session.commit()
    session.refresh(db_team)
    return db_team


@app.delete("/teams/{team_id}")
def delete_team(*, session: Session = Depends(get_session), team_id: int):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"ok": True}


# @app.post("/heroes/", response_model=HeroRead)
# def create_hero(hero: HeroCreate):
#     with Session(engine) as session:
#         db_hero = Hero.from_orm(hero)
#         session.add(db_hero)
#         session.commit()
#         session.refresh(db_hero)
#         return db_hero

@app.post("/heroes/", response_model=HeroRead, status_code=201)
def create_hero(*, session: Session = Depends(get_session), hero: HeroCreate):
    # Python would normally complain about that, but we can use the initial "parameter" *,
    # to mark all the rest of the parameters as "keyword only", which solves the problem.
    db_hero = Hero.from_orm(hero)
    db_team_id = db_hero.team_id
    if db_team_id:
        db_team = session.get(Team, db_team_id)
        if not db_team:
            raise HTTPException(status_code=404, detail="Team not found")
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.get("/heroes/", response_model=list[Hero])
def read_heroes(
        *,
        session: Session = Depends(get_session),
        offset: int = 0, limit: int = Query(default=100, lte=100)):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes


@app.get("/heroes/{hero_id}", response_model=HeroReadWithTeam)
def read_hero(
        *,
        session: Session = Depends(get_session),
        hero_id: int):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Item mot Found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroRead)
def update_hero(*,
                session: Session = Depends(get_session),
                hero_id: int, hero: HeroUpdate):
    # hero_id the hero id to update
    # we read the hero from database by the provided id
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        # checking if it exists, possibly raising an error for the client if it doesn't exist
        raise HTTPException(status_code=404, detail="Item mot Found")
    hero_data = hero.dict(exclude_unset=True)
    # Now that we have a dictionary with the data sent by the client, we can iterate for
    # each one of the keys and the values, and then we set them in the database hero model db_hero using setattr().
    for key, value in hero_data.items():
        setattr(hero_db, key, value)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db


@app.delete("/heroes/{hero_id}")
def delete_hero(
        *,
        session: Session = Depends(get_session),
        hero_id: int):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Item mot Found")
    session.delete(hero_db)
    session.commit()
    return {"status": "success"}
