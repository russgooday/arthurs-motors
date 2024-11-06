''' Generate random car sales data and save it to a JSON file '''
import json
from random import choice, randint
import numpy as np
from .customers_gen import generate_customers
from ..dependencies import ROOT_PATH
from ..utils.file_utils import load_json_data

OLDEST = 2010
NEWEST = 2024
AVG_YEARLY_MILEAGE = [5_000, 12_000]
EXPECTED_YEARLY_MILEAGE = 10_000
DECREASE_PER_YEAR = np.array([0,19,31,42,51,60,65,71,76,82,85,91,95]) / 100
NUM_ENTRIES = 500

def calculate_price(year: int, init_price: int, mileage: int) -> int:
    '''Calculate the price of a car based on its year, initial price, and mileage'''
    age = NEWEST - year
    expected_mileage = age * EXPECTED_YEARLY_MILEAGE
    percentage_for_mileage = (mileage - expected_mileage) * 0.000_001
    decrease = DECREASE_PER_YEAR.take(age, mode='clip') + percentage_for_mileage
    price = int(init_price - init_price * decrease)

    return price

def calculate_mileage(year: int) -> int:
    '''Calculate the mileage of a car based on its year'''
    age = NEWEST - year
    yearly_mileage = randint(*AVG_YEARLY_MILEAGE)
    mileage = sum(
        randint(yearly_mileage-1000, yearly_mileage+1000) for _ in range(age)
    )

    return mileage

# Function to generate a car entry
def generate_car_entry(car: dict, customer: dict) -> dict:
    '''Generate a random car entry'''
    details = {
        'make': car['make'],
        'model': car['model'],
        'year': randint(OLDEST, NEWEST),
        'fuel_type': choice(car['fuel_types']),
        'transmission': choice(car['transmissions']),
        'color': choice(car['colours']),
        'customer_id': customer['customer_id']
    }

    details['mileage'] = calculate_mileage(details['year'])
    details['price'] = calculate_price(details['year'], car['retail_price'], details['mileage'])

    return details

def generate_cars(customers: list[dict]) -> list[dict]:
    '''Generate random car sales data and save it to a JSON file'''
    # Load JSON data
    cars = load_json_data(f'{ROOT_PATH}/data/json/cars.json')
    num_entries = len(customers)

    return [
        generate_car_entry(choice(cars), choice(customers)) for _ in range(num_entries)
    ]

if __name__ == '__main__':
    rand_customers = generate_customers(NUM_ENTRIES)
    with open(f'{ROOT_PATH}/data/json/customers.json', 'w', encoding='utf-8') as out_file:
        json.dump(rand_customers, out_file, indent=4)

    with open(f'{ROOT_PATH}/data/json/cars_for_sale.json', 'w', encoding='utf-8') as out_file:
        json.dump(generate_cars(rand_customers), out_file, indent=4)
