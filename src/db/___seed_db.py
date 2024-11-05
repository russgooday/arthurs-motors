import pandas as pd
from sqlalchemy import insert
from .connection import engine, create_session
from ..dependencies import ROOT_PATH
from ..utils.file_utils import pd_load_json
from .table_classes import (
    Base, Makes, Models, Colours, FuelTypes, Transmissions #, Cars
)


def create_unique_column(df: pd.DataFrame, column: str, rename_column: str='') -> pd.Series:
    ''' creates a unique series from a column, indexed from 1 '''
    if not rename_column:
        rename_column = column

    df = pd.DataFrame({rename_column: df[column].drop_duplicates().sort_values()})
    df.index = pd.Index(range(1, df.index.size + 1), name=f'{column}_id')

    return df


def create_makes(car_data: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car makes series indexed from 1 '''
    return create_unique_column(car_data, column='make', rename_column='make_name')


def create_colours(car_data: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car colours series indexed from 1 '''
    return create_unique_column(car_data, column='color', rename_column='colour_name')


def create_fuel_types(car_data: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car fuel types series indexed from 1 '''
    return create_unique_column(car_data, column='fuel_type')


def create_transmissions(car_data: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car transmissions series indexed from 1 '''
    return create_unique_column(car_data, column='transmission', rename_column='transmission_type')


def create_models(car_data: pd.DataFrame, car_makes: pd.DataFrame) -> pd.DataFrame:
    ''' creates a car models series indexed from 1 with reference to car_makes '''

    car_makes_indexed = pd.Series(car_makes.index, car_makes['make_name'])
    car_models = car_data[['make', 'model']].drop_duplicates().sort_values(['make'])

    return pd.DataFrame({
        'model_name': car_models['model'],
        'make_id': car_makes_indexed.get(car_models['make']).values
    }).set_index(pd.Index(range(1, car_models.index.size + 1), name='model_id'))


def create_cars(car_data: pd.DataFrame):
    ''' creates a car series indexed from 1 with reference to the other tables '''
    # return {
    #     "make": cars_data['make'],
    #     "model": "E-Class",
    #     "year": 2012,
    #     "fuel_type": "Petrol",
    #     "transmission": "Automatic",
    #     "color": "Blue",
    #     "location": "Brighton and Hove",
    #     "mileage": 73287,
    #     "price": 5319
    # }

def join_tables(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    left_on: str='',
    right_on: str='',
    columns: list[str] = [],
    sort_by: str=''
):
    pd_merged = (
        pd.merge(left, right.reset_index(), left_on=left_on, right_on=right_on)[columns]
        .drop_duplicates()
        .sort_values(sort_by if sort_by else f'{left_on}_id')
    )

    return pd_merged.set_index(pd.Index(range(1, pd_merged.index.size + 1)))

def rename_columns(df: pd.DataFrame, index: str, columns: dict):
    return df.rename(columns=columns).set_index(name=index)

def join_tables2(
    left: pd.DataFrame,
    right: pd.DataFrame,
    *,
    left_on: str='',
    right_on: str='',
    columns: list[str] = [],
    index: str=''
):
    right_col_indexed = pd.Series(right.index, right[right_on])
    left_col = left[columns].drop_duplicates().sort_values([left_on])

    return pd.DataFrame({
        'model_name': left_col['model'],
        'make_id': right_col_indexed.get(left_col[left_on]).values
    }).set_index(pd.Index(range(1, left_col.index.size + 1), name=index))


def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    if not (session := create_session()):
        return None

    with session.begin():
        cars_pd_json = pd_load_json('./src/data/json/car-data.json')

        car_makes = create_makes(cars_pd_json)
        car_models = join_tables(
            cars_pd_json, car_makes, left_on='make', right_on='make_name',
            columns=['model', 'make_id']
        ).rename(columns={'model': 'model_name'}).rename_axis('model_id')

        print(car_models)


        # car_colours = create_colours(cars_pd_json)
        # car_fuel_types = create_fuel_types(cars_pd_json)
        # car_transmissions = create_transmissions(cars_pd_json)
        # car_models = create_models(cars_pd_json, car_makes)

        # print(car_models.merge(car_makes, on='make_id')[['make_name', 'model_name']])

        # session.execute(insert(Makes).values(car_makes.to_dict('records')))
        # session.execute(insert(Colours).values(car_colours.to_dict('records')))
        # session.execute(insert(FuelTypes).values(car_fuel_types.to_dict('records')))
        # session.execute(insert(Transmissions).values(car_transmissions.to_dict('records')))
        # session.execute(insert(Models).values(car_models.to_dict('records')))



if __name__ == '__main__':
    create_tables()