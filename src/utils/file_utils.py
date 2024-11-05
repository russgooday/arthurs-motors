''' Module for file operations '''
from os import path
import json
import pandas as pd
from ..dependencies import ROOT_PATH

def load_json_data(file_path: str, root=True) -> dict:
    '''Load JSON data from the file based on the provided key'''
    if root:
        file_path = path.join(ROOT_PATH, file_path)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f'Error loading {file_path}: {e}') from e


def pd_load_json(file_path: str, root=True) -> pd.DataFrame:
    '''Load JSON data from the file into a pandas DataFrame'''
    if root:
        file_path = path.join(ROOT_PATH, file_path)
    return pd.read_json(
        file_path, orient='records', dtype_backend='pyarrow', encoding='utf-8'
    )

def pd_save_json(df: pd.DataFrame, file_path: str, root=True):
    '''Save a pandas DataFrame to a JSON file'''
    if root:
        file_path = path.join(ROOT_PATH, file_path)
    df.to_json(
        path_or_buf=file_path, orient='records', indent=2, force_ascii=False
    )
