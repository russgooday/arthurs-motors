'''SQLAlchemy tables for the database'''
from typing import Annotated
from decimal import Decimal
from sqlalchemy import Numeric
from sqlalchemy.dialects.postgresql import VARCHAR
from sqlalchemy.schema import CreateTable, ForeignKeyConstraint
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    registry
)

Varchar50 = Annotated[str, 50]
Varchar100 = Annotated[str, 100]
Decimal2 = Annotated[Decimal, 2]
IntPrimary = Annotated[int, mapped_column(primary_key=True)]

# pylint: disable=too-few-public-methods

class Base(DeclarativeBase):
    '''Base class for tables'''
    registry = registry(
        type_annotation_map={
            Varchar100: VARCHAR(100),
            Varchar50: VARCHAR(50),
            Decimal2: Numeric(10, 2),
        }
    )


class Makes(Base):
    '''Shops table'''
    __tablename__ = 'makes'

    make_id:    Mapped[IntPrimary]
    make_name:  Mapped[Varchar50]


class Models(Base):
    '''Models table'''
    __tablename__ = 'models'
    __table_args__ = (
        ForeignKeyConstraint(
            ['make_id'],
            ['makes.make_id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
    )

    model_id:   Mapped[IntPrimary]
    model_name: Mapped[Varchar50]
    make_id:    Mapped[int]


class Colours(Base):
    '''Colours table'''
    __tablename__ = 'colours'

    colour_id:      Mapped[IntPrimary]
    colour_name:    Mapped[Varchar50]


class FuelTypes(Base):
    '''Fuel types table'''
    __tablename__ = 'fuel_types'

    fuel_type_id:   Mapped[IntPrimary]
    fuel_type:      Mapped[Varchar50]


class Transmissions(Base):
    '''Transmissions table'''
    __tablename__ = 'transmissions'

    transmission_id:    Mapped[IntPrimary]
    transmission_type:  Mapped[Varchar50]


class Counties(Base):
    '''Counties table'''
    __tablename__ = 'counties'

    county_id:      Mapped[IntPrimary]
    county_name:    Mapped[Varchar50]


class Towns(Base):
    '''towns table'''
    __tablename__ = 'towns'
    __table_args__ = (
        ForeignKeyConstraint(
            ['county_id'],
            ['counties.county_id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
    )

    town_id:    Mapped[IntPrimary]
    town_name:  Mapped[Varchar50]
    county_id:  Mapped[int]


class Cars(Base):
    '''Cars table'''
    __tablename__ = 'cars'
    __table_args__ = (
        ForeignKeyConstraint(
            ['model_id'],
            ['models.model_id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        ForeignKeyConstraint(
            ['colour_id'],
            ['colours.colour_id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        ForeignKeyConstraint(
            ['fuel_type_id'],
            ['fuel_types.fuel_type_id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        ForeignKeyConstraint(
            ['transmission_id'],
            ['transmissions.transmission_id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
        ForeignKeyConstraint(
            ['town_id'],
            ['towns.town_id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        )
    )

    car_id:             Mapped[IntPrimary]
    model_id:           Mapped[int]
    colour_id:          Mapped[int]
    fuel_type_id:       Mapped[int]
    transmission_id:    Mapped[int]
    town_id:            Mapped[int]
    year:               Mapped[int]
    price:              Mapped[Decimal2]
    mileage:            Mapped[int]


if __name__ == '__main__':
    # test to see SQL generated
    print(CreateTable(Makes.__table__))
    print(CreateTable(Models.__table__))
    print(CreateTable(Counties.__table__))
    print(CreateTable(Towns.__table__))
    print(CreateTable(Colours.__table__))
    print(CreateTable(FuelTypes.__table__))
    print(CreateTable(Transmissions.__table__))
    print(CreateTable(Cars.__table__))
