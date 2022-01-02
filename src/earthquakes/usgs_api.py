####################################################
#       Author: Houssam Halaby
#       Date:   16-12-2021
####################################################
# import from standard library
import copy
import urllib.parse
import urllib.request
from io import BytesIO
# import from installed packages
import pandas as pd
import asyncio
import aiohttp
# import from project

# TODO: refactor API params in separate file and use them in tests
END_DATE_PARAM = 'endtime'
END_DATE_ARG = 'end_date'
START_DATE_PARAM = 'starttime'
START_DATE_ARG = 'start_date'
LATITUDE_PARAM = 'latitude'
LATITUDE_ARG = 'latitude'
LONGITUDE_PARAM = 'longitude'
LONGITUDE_ARG = 'longitude'
MIN_MAGNITUDE_PARAM = 'minmagnitude'
MIN_MAGNITUDE_ARG = 'minimum_magnitude'
MAX_RADIUS_KM_PARAM = 'maxradiuskm'
MAX_RADIUS_KM_ARG = 'radius'
EVENT_PARAM = 'eventtype'
EVENT_ARG = 'event_type'
FORMAT_PARAM = 'format'
FORMAT_ARG = 'format'

# List the valid methods for the USGS API
VALID_METHODS = ['application.json', 'application.wadl', 'catalogs', 'contributors', 'count', 'query', 'version']
VALID_FORMATS = ["quakeml", "geojson", "csv", "kml", "kmlraw", "xml", "text", "cap"]
VALID_PARAMS = [EVENT_PARAM, FORMAT_PARAM, LATITUDE_PARAM, LONGITUDE_PARAM, END_DATE_PARAM, START_DATE_PARAM,
                MIN_MAGNITUDE_PARAM, MAX_RADIUS_KM_PARAM]
VALID_ARGS = [EVENT_ARG, FORMAT_ARG, LATITUDE_ARG, LONGITUDE_ARG, END_DATE_ARG, START_DATE_ARG,
              MIN_MAGNITUDE_ARG, MAX_RADIUS_KM_ARG]

# Base API URL
BASE_API_URL = r'https://earthquake.usgs.gov/fdsnws/event/1/'


def format_api_parameters(arguments_dict):
    """
    Function to format input arguments into proper USGS API parameters

    :param arguments_dict: dictionary containing arguments passed by the user to the API
    :return: a dict containing parameters properly formatted for the USGS API
    """
    # Initialize parameters dict
    parameters = {}
    # Deep copy provided arguments dict to avoid editing the same variable which can cause errors
    arguments_dict = copy.deepcopy(arguments_dict)

    if FORMAT_ARG in arguments_dict:
        parameters[FORMAT_PARAM] = arguments_dict.pop(FORMAT_ARG)

    if START_DATE_ARG in arguments_dict:
        # Set start_date
        start_date = arguments_dict.pop(START_DATE_ARG)
        # format start time correctly
        parameters[START_DATE_PARAM] = f'{start_date.year}-{start_date.month:02}-{start_date.day:02}'

    # check if end_date is provided in args
    if END_DATE_ARG in arguments_dict:
        # Set end_date
        end_date = arguments_dict.pop(END_DATE_ARG)
        # format end time correctly
        parameters[END_DATE_PARAM] = f'{end_date.year}-{end_date.month:02}-{end_date.day:02}'

    if LATITUDE_ARG in arguments_dict:
        parameters[LATITUDE_PARAM] = arguments_dict.pop(LATITUDE_ARG)

    if LONGITUDE_ARG in arguments_dict:
        parameters[LONGITUDE_PARAM] = arguments_dict.pop(LONGITUDE_ARG)

    if MAX_RADIUS_KM_ARG in arguments_dict:
        parameters[MAX_RADIUS_KM_PARAM] = arguments_dict.pop(MAX_RADIUS_KM_ARG)

    if MIN_MAGNITUDE_ARG in arguments_dict:
        parameters[MIN_MAGNITUDE_PARAM] = arguments_dict.pop(MIN_MAGNITUDE_ARG)

    if EVENT_ARG in arguments_dict:
        parameters[EVENT_PARAM] = arguments_dict.pop(EVENT_ARG)

    # if dict is not empty, then some arguments haven't been formatted.
    if arguments_dict:
        raise AttributeError("Not all provided arguments have been formatted as parameters. "
                             "Make sure each provided argument is supported.")

    return parameters


def build_api_url(method, arguments):
    """
    Function to build an api url using the given method and parameters

    :param method: desired method for the api request
    :param arguments:  necessary parameters corresponding to the given method
    :return: returns a correctly formatted url for the APIhttps://earthquake.usgs.gov/fdsnws/event/1/
    """

    # check if empty parameters
    if not arguments:
        raise ValueError("empty parameters input")
    # check if provided arguments are valid
    for arg in arguments:
        if arg not in VALID_ARGS:
            raise ValueError(f"Provided argument is not supported. Arg: {arg}")
    # Check if required arguments are missing:
    if LATITUDE_ARG in arguments and LONGITUDE_ARG not in arguments:
        raise AssertionError("Latitude argument is provided without a Longitude argument")
    if LATITUDE_ARG not in arguments and LONGITUDE_ARG in arguments:
        raise AssertionError("Longitude argument is provided without a Latitude argument")
    if MAX_RADIUS_KM_ARG in arguments and( LATITUDE_ARG not in arguments or LONGITUDE_ARG not in arguments):
        raise AssertionError("Radius argument is given without Latitude or Longitude argument")
    # format arguments into API parameters
    params = format_api_parameters(arguments)
    # Check that returned parameters are valid
    for param in params:
        if param not in VALID_PARAMS:
            raise ValueError(f"provided parameter does not seem to be valid. Param: {param}")
    # Check that format parameter exists
    if FORMAT_PARAM not in params:
        raise ValueError("format parameter was not provided")
    # Check that format parameter is valid
    if params[FORMAT_PARAM] not in VALID_FORMATS:
        raise ValueError("provided format parameter does not seem to be valid")
    # Check that method is valid
    if method not in VALID_METHODS:
        raise ValueError("provided method does not seem to be valid")
    # Append the chosen method to the base url
    api_url_method = BASE_API_URL + method + '?'
    # Append every input parameter to api url
    url_values = urllib.parse.urlencode(params)
    api_url = api_url_method + url_values
    return api_url


def get_earthquake_data(**kwargs):
    """
    function to get earthquake data from API

    :key latitude: latitude in degrees of the desired geographic point:
    :key longitude: longitude in degrees of the desired geographic point
    :key radius: Limit events to a maximum number of kilometers away from the desired geographic point
    :key minimum_magnitude: Limit to events with a magnitude larger than the specified minimum.
    :key end_date: Limit to events on or before the specified end time.
    :key format: Specify the format of the API response. By default, Earthquakes are chosen
    :key event_type: Limit to specific event types. By default, CSV is chosen
    :return: Returns a dataframe of the requested earthquake events if the API request is successful,
    and none otherwise
    """
    # If an end date is provided, set the start date with an offset
    if END_DATE_ARG in kwargs:
        # Set number of years to go back from end_date
        offset_years = 200
        # Set start_date by subtracting the number of offset years from the end date
        kwargs[START_DATE_ARG] = kwargs[END_DATE_ARG] - pd.DateOffset(years=offset_years)
    # If the event type is not specified, add it
    if EVENT_ARG not in kwargs:
        kwargs[EVENT_ARG] = 'earthquake'
    # If the format type is not specified, add it
    if FORMAT_ARG not in kwargs:
        kwargs[FORMAT_ARG] = 'csv'
    # set the correct method for the API
    method = 'query'
    # build the api url with the correct method and desired parameters
    api_url = build_api_url(method=method, arguments=kwargs)
    # open api url and save response
    response = urllib.request.urlopen(api_url)
    # if HTTP response code is 200 (meaning success) then save dataframe
    if response.status == 200:
        response_df = pd.read_csv(BytesIO(response.read()))
    # else set return to None
    else:
        response_df = None
        print(f'No dataframe was returned. HTTP Response Code: {response.status}')

    return response_df


async def get_earthquake_data_for_multiple_locations(assets, **kwargs):
    # If an end date is provided, set the start date with an offset
    if END_DATE_ARG in kwargs:
        # Set number of years to go back from end_date
        offset_years = 200
        # Set start_date by subtracting the number of offset years from the end date
        kwargs[START_DATE_ARG] = kwargs[END_DATE_ARG] - pd.DateOffset(years=offset_years)
    # If the event type is not specified, add it
    if EVENT_ARG not in kwargs:
        kwargs[EVENT_ARG] = 'earthquake'
    # If the format type is not specified, add it
    if FORMAT_ARG not in kwargs:
        kwargs[FORMAT_ARG] = 'csv'

    async with aiohttp.ClientSession() as session:
        tasks = []
        for asset in assets:
            # Add latitude and longitude to kwargs
            kwargs[LATITUDE_ARG] = asset[0]
            kwargs[LONGITUDE_ARG] = asset[1]
            # set the correct method for the API
            method = 'query'
            # build the api url with the correct method and desired parameters
            api_url = build_api_url(method=method, arguments=kwargs)
            tasks.append(asyncio.ensure_future(get_earthquake_data_async(session=session,
                                                                         url=api_url)))
        earthquake_data_assets_list = await asyncio.gather(*tasks)
        earthquake_data_assets = pd.concat(earthquake_data_assets_list, ignore_index=True).drop_duplicates()
    return earthquake_data_assets


async def get_earthquake_data_async(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            response_csv = await response.read()
            response_df = pd.read_csv(BytesIO(response_csv))
        else:
            response_df = None
        return response_df
