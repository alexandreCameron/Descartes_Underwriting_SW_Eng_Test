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

