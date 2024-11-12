'''SQLAlchemy tables for the database'''
# pylint: disable=invalid-name
import enum
from typing import Annotated
from decimal import Decimal
from sqlalchemy import Numeric, Enum, create_mock_engine
from sqlalchemy.dialects.postgresql import VARCHAR
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry


Varchar50 = Annotated[str, 50]
Varchar100 = Annotated[str, 100]
Decimal2 = Annotated[Decimal, 2]
IntPrimary = Annotated[int, mapped_column(primary_key=True)]

class FuelTypes(enum.Enum):
    '''Fuel types enum'''
    petrol = 'petrol'
    diesel = 'diesel'
    electric = 'electric'
    hybrid = 'hybrid'

class TransmissionTypes(enum.Enum):
    '''Transmission types enum'''
    manual = 'manual'
    automatic = 'automatic'

# pylint: disable=too-few-public-methods
class Base(DeclarativeBase):
    '''Base class for tables'''

    registry = registry(
        type_annotation_map={
            Varchar100: VARCHAR(100),
            Varchar50: VARCHAR(50),
            Decimal2: Numeric(10, 2),
            FuelTypes: Enum(FuelTypes),
            TransmissionTypes: Enum(TransmissionTypes),
        }
    )

class Makes(Base):
    '''Shops table'''

    __tablename__ = 'makes'

    make_id: Mapped[IntPrimary]
    make_name: Mapped[Varchar50]

class Models(Base):
    '''Models table'''

    __tablename__ = 'models'
    __table_args__ = (
        ForeignKeyConstraint(
            ['make_id'], ['makes.make_id'], onupdate='CASCADE', ondelete='CASCADE'
        ),
    )

    model_id: Mapped[IntPrimary]
    model_name: Mapped[Varchar50]
    make_id: Mapped[int]

class Colours(Base):
    '''Colours table'''

    __tablename__ = 'colours'

    colour_id: Mapped[IntPrimary]
    colour_name: Mapped[Varchar50]

class Counties(Base):
    '''Counties table'''

    __tablename__ = 'counties'

    county_id: Mapped[IntPrimary]
    county_name: Mapped[Varchar50]

class Customers(Base):
    '''Customers table'''

    __tablename__ = 'customers'
    __table_args__ = (
        ForeignKeyConstraint(
            ['county_id'], ['counties.county_id'], onupdate='CASCADE', ondelete='CASCADE'
        ),
    )

    customer_id: Mapped[IntPrimary]
    first_name: Mapped[Varchar50]
    last_name: Mapped[Varchar50]
    town_name: Mapped[Varchar50]
    county_id: Mapped[int]

# -------- Cars_For_Sale Tables --------

class CarsForSale(Base):
    '''Cars for sale table'''

    __tablename__ = 'cars_for_sale'
    __table_args__ = (
        ForeignKeyConstraint(
            ['model_id'], ['models.model_id'], onupdate='CASCADE', ondelete='CASCADE'
        ),
        ForeignKeyConstraint(
            ['colour_id'], ['colours.colour_id'], onupdate='CASCADE', ondelete='CASCADE'
        ),
        ForeignKeyConstraint(
            ['customer_id'],
            ['customers.customer_id'],
            onupdate='CASCADE',
            ondelete='CASCADE',
        ),
    )

    car_id: Mapped[IntPrimary]
    model_id: Mapped[int]
    colour_id: Mapped[int]
    fuel_type: Mapped[FuelTypes]
    transmission_type: Mapped[TransmissionTypes]
    customer_id: Mapped[int]
    year: Mapped[int]
    price: Mapped[Decimal2]
    mileage: Mapped[int]
    description: Mapped[str]

if __name__ == '__main__':
    # output SQL from metadata
    # pylint: disable=unused-argument
    def dump(sql, *multiparams, **params):
        ''' Output SQL '''
        print(sql.compile(dialect=engine.dialect))

    engine = create_mock_engine('postgresql+pg8000://', strategy='mock', executor=dump)
    Base.metadata.create_all(engine, checkfirst=False)
