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
    # check if end_date is provided in args
    if END_DATE_ARG in arguments_dict:
        # Set end_date
        end_date = arguments_dict.pop(END_DATE_ARG)
        # format end time correctly
        parameters[END_DATE_PARAM] = f'{end_date.year}-{end_date.month}-{end_date.day}'

    if START_DATE_ARG in arguments_dict:
        # Set end_date
        start_date = arguments_dict.pop(START_DATE_ARG)
        # format start time correctly
        parameters[START_DATE_PARAM] = f'{start_date.year}-{start_date.month}-{start_date.day}'

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

    if FORMAT_ARG in arguments_dict:
        parameters[FORMAT_PARAM] = arguments_dict.pop(FORMAT_ARG)
    # if dict is not empty, then some arguments haven't been formatted.
    if arguments_dict:
        raise AttributeError("Not all provided arguments have been formatted as parameters. "
                             "Make sure each provided arguments is supported.")

    return parameters


def build_api_url(method, parameters):
    """
    Function to build an api url using the given method and parameters

    :param method: desired method for the api request
    :param parameters:  necessary parameters corresponding to the given method
    :return: returns a correctly formatted url for the APIhttps://earthquake.usgs.gov/fdsnws/event/1/
    """

    # check if empty parameters
    if not parameters:
        raise ValueError("empty parameters input")
    # Check that format parameter exist and exists
    if FORMAT_PARAM not in parameters:
        raise ValueError("format parameter was not provided")
    # Check that format parameter exist and exists
    if parameters[FORMAT_PARAM] not in VALID_FORMATS:
        raise ValueError("provided format parameter does not seem to be valid")
    # Check that method is valid
    if method not in VALID_METHODS:
        raise ValueError("provided method does not seem to be valid")
    # Append the chosen method to the base url
    api_url_method = BASE_API_URL + method + '?'
    # Append every input parameter to api url
    url_values = urllib.parse.urlencode(parameters)
    api_url = api_url_method + url_values
    return api_url
