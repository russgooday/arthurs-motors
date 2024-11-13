''' route handlers for treasures api '''
from typing import Dict
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from ..dependencies import ROOT_PATH
from ..models.model_motors import fetch_locations

router = APIRouter()
templates = Jinja2Templates(directory=f'{ROOT_PATH}/views')


# Homepage and search form
@router.get('/', response_class=HTMLResponse)
def homepage(request: Request) -> HTMLResponse:
    ''' return the home page '''
    return templates.TemplateResponse(
        request, name='index.html'
    )


# Initial healthcheck
@router.get('/api/healthcheck')
def get_healthcheck() -> Dict:
    ''' Check that we are all up and running! '''
    return {'message': 'application is healthy'}


# Fetch all treasures
# Returns an datalist of all matching locations
@router.get('/api/locations', response_class=HTMLResponse)
def get_treasures(request: Request, search_term:str = '') -> HTMLResponse:
    ''' return all treasures and their shop details '''
    locations = []

    if search_term:
        locations = fetch_locations(search_term)

    return templates.TemplateResponse(
        request, name='partials/locations_datalist.html', context={'locations': locations}
    )
