''' Database connection module for SQLAlchemy '''
from os import environ as env
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..dependencies import ROOT_PATH
from .logger import log_query_time

# Load the environment variables based on the app environment
APP_ENV = env.get('APP_ENV', default='test')
load_dotenv(f'{ROOT_PATH}/.env.{APP_ENV}')

print(f'\nEnvironment: {APP_ENV}')
print(env.get('PG_USER'))
# create a connection URL for SQLAlchemy
CONNECTION_URL = URL.create(
    'postgresql+pg8000',
    username    = env.get('PG_USER'),
    password    = env.get('PG_PASSWORD'),
    host        = env.get('PG_HOST'),
    database    = env.get('PG_DATABASE'),
    port        = env.get('PG_PORT')
)

# Create the SQLAlchemy engine
engine = create_engine(CONNECTION_URL)

def create_connection(logging: str = ''):
    ''' Standard function to create a connection '''
    try:
        if logging:
            log_query_time(f'log.{APP_ENV}.{logging}')
        return engine.connect()
    except SQLAlchemyError as exc:
        print(f'Error during connection: {exc}')
        return None

def create_session(logging: str = ''):
    ''' Standard function to create a session '''
    try:
        if logging:
            log_query_time(f'log.{APP_ENV}.{logging}')
        return Session(engine)
    except SQLAlchemyError as exc:
        print(f'Error with session: {exc}')
        return None
