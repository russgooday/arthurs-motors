from pytest import mark, fixture
import time
import pandas as pd
import numpy as np
from src.data.source.car_models import makes_models
from src.db.seed_db import (
    create_makes,
    create_models,
    create_cars
)

@fixture(scope='class')
def fetch_car_data():
    car_data = pd.read_json(
        './src/data/json/car-data.json',
        orient='records',
        dtype_backend='pyarrow',
        encoding='utf-8'
    )
    return car_data

@mark.describe('Test tables creation functions')
class TestSeeding():

    @mark.it('returns the correct pd.Series of car makes')
    def test_makes(self, fetch_car_data):
        car_data = fetch_car_data
        src_car_makes = pd.DataFrame(makes_models)['make'].unique()
        car_makes = create_makes(car_data)

        assert isinstance(car_makes, pd.Series)
        assert car_makes.index.start == 1
        assert car_makes.index.stop == len(src_car_makes) + 1

        src_car_makes.sort()
        assert np.array_equal(car_makes, src_car_makes)


    @mark.it('returns the correct pd.Series of car models')
    def test_models(self, fetch_car_data):
        car_data = fetch_car_data
        car_makes = create_makes(car_data)
        start = time.time()
        car_models = create_models(car_data, car_makes)
        print(f'time taken: {time.time() - start}')
        print(car_models)

        assert False
