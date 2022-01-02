# import from standard library
# import from installed packages
import numpy as np
import pandas as pd

# import from project

EARTH_RADIUS = 6378

TIME_COLUMN = "time"
PAYOUT_COLUMN = "payout"
MAGNITUDE_COLUMN = "mag"
DISTANCE_COLUMN = "distance"
LATITUDE_COLUMN = "latitude"
LONGITUDE_COLUMN = "longitude"
TIMEZONE = 'UTC'


def get_haversine_distance(latitude_list, longitude_list, point_latitude, point_longitude):
    """
    Function to calculate the haversine distances between the list of points [latitude_list, longitude_list] and the
    point of interest [point_latitude,point_longitude]

    :param latitude_list: list of latitudes for the points in decimal degrees
    :param longitude_list: list of longitudes for the points in decimal degrees
    :param point_latitude: latitude of the point of interest in decimal degrees
    :param point_longitude: longitude of the point of interest in decimal degrees
    :return:list of distances in kilometers
    """
    # Check if latitude and longitude lists are of equal length
    if len(latitude_list) != len(longitude_list):
        raise ValueError("latitude and longitude lists are not of equal length.")
    # Check if point coordinates are within limits
    if point_latitude > 90 or point_latitude < -90 or point_longitude > 180 or point_longitude < -180:
        raise ValueError("Point coordinates are outside latitude or longitude bounds.")
    # Convert lists to numpy arrays
    lat = np.array(point_latitude)
    lon = np.array(point_longitude)
    latl = np.array(latitude_list)
    lonl = np.array(longitude_list)
    # Check if coordinates are within limits
    if any(latl > 90) or any(latl < -90):
        raise ValueError("Latitudes list contains values outside latitude bounds")
    if any(lonl > 180) or any(lonl < -180):
        raise ValueError("Longitudes list contains values outside longitude bounds")

    # Convert decimal degrees to radians
    try:
        lat = np.deg2rad(point_latitude)
        lon = np.deg2rad(point_longitude)
        latl = np.deg2rad(latitude_list)
        lonl = np.deg2rad(longitude_list)
    # if types other than int or float are present in the lists
    except TypeError as e:
        print(e)
    d = np.sin((latl - lat) / 2) ** 2 + np.cos(lat) * np.cos(latl) * np.sin((lonl - lon) / 2) ** 2
    distances = 2 * EARTH_RADIUS * np.arcsin(np.sqrt(d))

    return distances


def compute_payouts(earthquake_data, payouts_structure, return_type='dict'):
    """
    Function to calculate payouts over the years according to earthquake data and a payout structure
    :param return_type: Specify function return type if Python Dictionary 'dict' or Pandas Series 'series'. Dict by
    default
    :param payouts_structure: the payouts structure that defines how much is paid per year. List of lists.
    :param earthquake_data: the historical earthquake data for the period of time of interest
    :return: a map of payout percentage per year. eg: 2010: 50 for a 50% payout in 2010.
    """
    if earthquake_data.empty:
        raise ValueError('Provided earthquake data is empty.')
    if not payouts_structure:
        raise ValueError('Provided payouts structure is empty.')
    valid_return_types = ['dict', 'series']
    return_type = return_type.lower()
    if return_type not in valid_return_types:
        raise TypeError("Specified return type is not supported.")
    # Convert the time column from string type to datetime
    earthquake_data[TIME_COLUMN] = pd.to_datetime(earthquake_data[TIME_COLUMN])
    # Get start year of data
    start_year = earthquake_data[TIME_COLUMN].min().year
    # Get end year of data
    end_year = earthquake_data[TIME_COLUMN].max().year
    # Create empty payouts dict
    payouts = {}
    # Loop over every year from start to end in earthquake data
    for year in range(start_year, end_year + 1):
        # Get earthquake data for current year
        timestamp_start = pd.Timestamp(year=year, month=1, day=1, tz=TIMEZONE)
        timestamp_end = pd.Timestamp(year=year + 1, month=1, day=1, tz=TIMEZONE)
        earthquake_data_year = earthquake_data[
            (earthquake_data[TIME_COLUMN] >= timestamp_start) & (earthquake_data[TIME_COLUMN] < timestamp_end)]
        # Set no payout as default
        payouts[year] = 0
        # Loop over every payout possibility
        for payout_struct in payouts_structure:
            # If magnitude and distance criteria are met,
            if any((earthquake_data_year[MAGNITUDE_COLUMN] >= payout_struct[1]) &
                   (earthquake_data_year[DISTANCE_COLUMN] <= payout_struct[0])):
                # specify corresponding payout
                # If no payout is recorded or if the current recorded payout is less, update payout
                if payouts[year] < payout_struct[2]:
                    payouts[year] = payout_struct[2]
    if return_type == 'dict':
        return payouts
    elif return_type == 'series':
        return pd.Series(payouts)
    else:
        raise TypeError("Specified return type is not supported.")


def compute_burning_cost(payouts, start_year, end_year):
    """
    Function to compute burning cost. The burning cost is the average of payouts over a time range.
    :param payouts: The payouts that have happened every year for a certain period
    :param start_year: First year to calculate burning cost
    :param end_year: Last year to calculate burning cost
    :return: burning cost value over the provided time range
    """
    # Check type of payouts argument
    if not isinstance(payouts, (pd.Series, dict)):
        raise TypeError('Payouts input argument type is not supported.')
    # Check if start year data is available, else raise error
    if start_year < min(payouts.keys()):
        raise AttributeError(f'The year {start_year} does not exist in payouts. '
                             f'Provide a more recent one.')
    # Check if end year data is available, else raise error
    if end_year > max(payouts.keys()):
        raise AttributeError(f'The year {end_year} does not exist in payouts. '
                             f'Provide a less recent one.')
    # Calculate number of years between start_year and end_year
    number_of_years = end_year - start_year + 1
    # Create a range object for the needed years
    years_range = range(start_year, end_year + 1)
    # Initialize the sum of payouts
    sum_payouts = 0
    # Loop over every year between start_year and end_year
    # This method works for both dicts and Series types and is faster than other methods
    for year in years_range:
        # Assume zero payout if year does not exist
        if year in payouts:
            # Add the year payout to the cumulative sum
            sum_payouts += payouts[year]
    # Divide the payouts sum by the number of years
    burning_cost = sum_payouts / number_of_years
    return burning_cost
