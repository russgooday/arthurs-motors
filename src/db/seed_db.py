import pandas as pd
from sqlalchemy import insert
from .connection import engine, create_session
from ..utils.file_utils import pd_load_json, load_json_data
from .table_classes import (
    Base,
    Makes,
    Models,
    Colours,
    FuelTypes,
    Transmissions,
    Counties,
    Towns,
    Cars
)


def normalize(data: pd.DataFrame) -> pd.DataFrame:
    ''' deal with nested json data returning a normalized dataframe
        e.g. {"location": { "town": "Birmingham", "county": "West Midlands" } }
        -> ["location.town", "location.county"], [["Birmingham", ...], ["West Midlands", ...]]
    '''
    return pd.json_normalize(data).convert_dtypes(dtype_backend='pyarrow')


def create_indexed_column(
    column: pd.Series, new_column_name: str='', index: str='', unique: bool=False
) -> pd.DataFrame:
    ''' returns column as dataframe with indexed column '''
    if not new_column_name:
        new_column_name = column.name

    if not index:
        index = f'{column.name}_id'

    if unique:
        column = column.drop_duplicates()

    return (
        pd.DataFrame({new_column_name: column.sort_values()})
            .set_index(pd.Index(range(1, column.size + 1), name=index))
    )

# Car Makes
def create_makes_table(car_data: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car makes series indexed from 1 '''
    return create_indexed_column(
        car_data['make'], new_column_name='make_name', unique=True
    )


# Car Colours
def create_colours_table(car_data: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car colours series indexed from 1 '''
    return create_indexed_column(
        car_data['color'], new_column_name='colour_name', index='colour_id', unique=True
    )


# Car Fuel Types
def create_fuel_types_table(car_data: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car fuel types series indexed from 1 '''
    return create_indexed_column(car_data['fuel_type'], unique=True)


# Car Transmissions
def create_transmissions_table(car_data: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car transmissions series indexed from 1 '''
    return create_indexed_column(
        car_data['transmission'], new_column_name='transmission_type', unique=True
    )


# Locations Counties
def create_counties_table(locations: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car counties series indexed from 1 '''
    return create_indexed_column(locations['county'], new_column_name='county_name', unique=True)


# Locations Towns
def create_towns_table(locations: pd.DataFrame, counties: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car towns series indexed from 1 '''
    towns_joined = (
        pd.merge(locations, counties.reset_index(), left_on='county', right_on='county_name')
            .rename(columns={'town': 'town_name'})
            .set_index(pd.Index(range(1, locations.index.size + 1), name='town_id'))
    )

    return towns_joined[['town_name', 'county_id']]


# Car Models
def create_models_table(
    car_data: pd.DataFrame,
    car_makes: pd.DataFrame
) -> pd.DataFrame:
    ''' creates a car models series indexed from 1 with reference to car_makes '''
    car_models = (
        pd.merge(car_data, car_makes.reset_index(), left_on='make', right_on='make_name')
        [['model', 'make_id']]
        .rename(columns={'model': 'model_name'})
        .drop_duplicates()
        .sort_values('make_id')
    )

    return (
        car_models.set_index(pd.Index(range(1, car_models.index.size + 1), name='model_id'))
    )


def create_cars(car_data: pd.DataFrame, tables: dict = None) -> pd.DataFrame:
    ''' creates a car series indexed from 1 with reference to the other tables '''
    if not isinstance(tables, dict):
        return None

    # Move indexes to columns to make name, id columns accessible
    fk_model_ids = tables[Models].reset_index()
    fk_colour_ids = tables[Colours].reset_index()
    fk_fuel_type_ids = tables[FuelTypes].reset_index()
    fk_transmission_ids = tables[Transmissions].reset_index()
    fk_town_ids = pd.merge(tables[Towns].reset_index(), tables[Counties], on='county_id')

    # Replace the car data column data with the foreign key ids

    # car models
    model_ids = pd.merge(
        car_data['model'], fk_model_ids,
        left_on='model', right_on='model_name'
    )

    # car colours
    colour_ids = pd.merge(
        car_data['color'], fk_colour_ids,
        left_on='color', right_on='colour_name'
    )

    # car fuel types
    fuel_type_ids = pd.merge(
        car_data['fuel_type'], fk_fuel_type_ids,
        left_on='fuel_type', right_on='fuel_type'
    )

    # car transmission types
    transmission_ids = pd.merge(
        car_data['transmission'], fk_transmission_ids,
        left_on='transmission', right_on='transmission_type'
    )

    # towns
    town_ids = pd.merge(
        car_data, fk_town_ids,
        left_on=['location.town', 'location.county'], right_on=['town_name', 'county_name']
    )

    cars = pd.DataFrame({
        'model_id': model_ids['model_id'],
        'colour_id': colour_ids['colour_id'],
        'fuel_type_id': fuel_type_ids['fuel_type_id'],
        'transmission_id': transmission_ids['transmission_id'],
        'town_id': town_ids['town_id'],
        'year': car_data['year'],
        'price': car_data['price'],
        'mileage': car_data['mileage']
    })

    return cars.set_index(pd.Index(range(1, cars.index.size + 1), name='car_id'))


def create_tables():
    ''' creates the tables in the database '''
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    if not (session := create_session()):
        return None

    with session.begin():
        cars_df = pd.load_json('data/json/cars.json')
        locations_df = pd_load_json('data/json/locations.json')
        cars_for_sale_df = normalize(load_json_data('data/json/cars_for_sale.json'))

        car_makes_df = create_makes_table(cars_df)
        counties_df = create_counties_table(locations_df)

        tables = {
            Makes: car_makes_df,
            Counties: counties_df,
            Models: create_models_table(cars_df, car_makes_df),
            Colours: create_colours_table(cars_for_sale_df),
            FuelTypes: create_fuel_types_table(cars_for_sale_df),
            Transmissions: create_transmissions_table(cars_for_sale_df),
            Towns: create_towns_table(locations_df, counties_df)
        }

        cars_df = create_cars(cars_for_sale_df, tables=tables)

        for table, df in tables.items():
            records = df.to_dict('records')
            session.execute(insert(table).values(records))

        # print(cars_for_sale_df)
        session.execute(insert(Cars).values(cars_df.to_dict('records')))



if __name__ == '__main__':
    create_tables()
