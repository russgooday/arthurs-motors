''' models and functions for treasures table '''

# from typing import Literal, Optional, Any
# import pandas as pd
# from pydantic import BaseModel, field_validator, PositiveInt
# from fastapi import HTTPException
from sqlalchemy import select, join, case, or_, distinct # insert, desc, asc, bindparam
from ..db.connection import create_connection
from ..db.table_classes import Customers, Counties


def fetch_column(conn, column, is_distinct: bool=False) -> list[str]:
    ''' fetches all distinct values in a column '''
    stmt = select(column).where(column.is_not(None))
    response = conn.execute(stmt.distinct() if is_distinct else stmt)
    return list(response.scalars().all())


def fetch_locations(search_term: str='') -> list[str]:
    ''' fetches all locations that start with the search term '''
    locations = []
    if not (conn:= create_connection()):
        return locations

    town_name, county_name = Customers.town_name, Counties.county_name

    stmt = (
        select(
            distinct(
                case(
                    (town_name.istartswith(search_term), town_name + ', ' + county_name),
                    (county_name.istartswith(search_term), county_name)
                ).label('location')
            )
        )
        .select_from(join(Customers, Counties, Customers.county_id == Counties.county_id))
        .filter(or_(town_name.istartswith(search_term), county_name.istartswith(search_term)))
    )

    with conn.begin():
        locations = conn.execute(stmt, {'search_term': search_term}).scalars().all()
    return locations
