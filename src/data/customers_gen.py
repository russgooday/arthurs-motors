''' Generate random car sales data and save it to a JSON file '''
from random import choice
from ..dependencies import ROOT_PATH
from ..utils.file_utils import load_json_data

# Function to generate a car entry
def generate_customer(customer: dict, location: dict, index: int) -> dict:
    '''Generate a random car entry'''
    details = {
        'customer_id': index + 1,
        'first_name': customer['first_name'],
        'last_name': customer['last_name'],
        'town': location['town'],
        'county': location['county']
    }

    return details

def generate_customers(num_entries: int) -> list[dict]:
    '''Generate random car sales data and save it to a JSON file'''
    # Load JSON data
    customers = load_json_data(f'{ROOT_PATH}/data/json/customers_names.json')
    locations = load_json_data(f'{ROOT_PATH}/data/json/locations.json')

    return [
        generate_customer(choice(customers), choice(locations), i) for i in range(num_entries)
    ]
