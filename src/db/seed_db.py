import pandas as pd
from sqlalchemy import insert
from .connection import engine, create_session
from ..utils.file_utils import pd_load_json, load_json_data
from .table_classes import (
    Base,
    Makes,
    Models,
    Colours,
    Counties,
    Customers,
    CarsForSale
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
        car_data['colours'].explode(), new_column_name='colour_name', index='colour_id', unique=True
    )


# Locations Counties
def create_counties_table(customers: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car counties series indexed from 1 '''
    return create_indexed_column(customers['county'], new_column_name='county_name', unique=True)


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

# Customers
def create_customers_table(
        customers: pd.DataFrame,
        counties: pd.DataFrame
) -> pd.DataFrame:
    ''' creates a customers series indexed from 1 with reference to counties '''
    customers = pd.merge(
        customers, counties.reset_index(),
        left_on='county', right_on='county_name'
    )

    return (
        customers[['first_name', 'last_name', 'town', 'county_id']]
            .rename(columns={'town': 'town_name'})
            .set_index(pd.Index(range(1, customers.index.size + 1), name='customer_id'))
    )


def create_cars_for_sale(cars_for_sale: pd.DataFrame, tables: dict = None) -> pd.DataFrame:
    ''' creates a car series indexed from 1 with reference to the other tables '''
    if not isinstance(tables, dict):
        return None

    # Move indexes to columns to make name, id columns accessible
    fk_model_ids = tables[Models].reset_index()
    fk_colour_ids = tables[Colours].reset_index()

    # Replace the car data column data with the foreign key ids

    # car models
    model_ids = pd.merge(
        cars_for_sale['model'], fk_model_ids,
        left_on='model', right_on='model_name'
    )

    # car colours
    colour_ids = pd.merge(
        cars_for_sale['color'], fk_colour_ids,
        left_on='color', right_on='colour_name'
    )

    cars = pd.DataFrame({
        'model_id': model_ids['model_id'],
        'colour_id': colour_ids['colour_id'],
        'fuel_type': cars_for_sale['fuel_type'].str.lower(),
        'transmission_type': cars_for_sale['transmission'].str.lower(),
        'customer_id': cars_for_sale['customer_id'],
        'year': cars_for_sale['year'],
        'price': cars_for_sale['price'],
        'mileage': cars_for_sale['mileage'],
        'description': cars_for_sale['description']
    })

    return cars.set_index(pd.Index(range(1, cars.index.size + 1), name='car_id'))


def create_tables():
    ''' creates the tables in the database '''
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    if not (session := create_session()):
        return 'Failed to create session'

    with session.begin():
        cars_df = pd_load_json('data/json/cars.json')
        customers_df = pd_load_json('data/json/customers.json')
        cars_for_sale_df = normalize(load_json_data('data/json/cars_for_sale.json'))
        car_makes_df = create_makes_table(cars_df)
        counties_df = create_counties_table(customers_df)

        tables = {
            Makes: car_makes_df,
            Counties: counties_df,
            Models: create_models_table(cars_df, car_makes_df),
            Colours: create_colours_table(cars_df),
            Customers: create_customers_table(customers_df, counties_df)
        }

        cars_df = create_cars_for_sale(cars_for_sale_df, tables=tables)

        for table, df in tables.items():
            records = df.to_dict('records')
            session.execute(insert(table).values(records))

        session.execute(insert(CarsForSale).values(cars_df.to_dict('records')))

    return 'Tables created successfully!!'

if __name__ == '__main__':
    print(create_tables())
