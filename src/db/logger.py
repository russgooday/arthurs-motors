'''module for logging for query times'''
import time
import re
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine
# pylint: disable=too-many-arguments, too-many-positional-arguments, disable=unused-argument

# regex to match INSERT INTO statements
INSERT_EXPR = re.compile(r'INSERT INTO[^)]+\)')

def log_query_time(name: str ='log') -> None:
    '''sets up logging for query times'''
    logging.basicConfig(filename='query.log')
    time_logger = logging.getLogger(name)
    time_logger.setLevel(logging.DEBUG)


    @event.listens_for(Engine, 'before_cursor_execute')
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        '''Logs the start of a query filtering out INSERT INTO statements'''
        conn.info.setdefault('query_start_time', []).append(time.time())
        statement = statement.strip()

        if (command:= INSERT_EXPR.search(statement)):
            statement = command.group()

        time_logger.debug('Start Query:\n %s', statement)


    @event.listens_for(Engine, 'after_cursor_execute')
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        '''Logs the end of a query with total time for the query'''
        total = time.time() - conn.info['query_start_time'].pop(-1)
        time_logger.debug('Total Time: %f', total)
