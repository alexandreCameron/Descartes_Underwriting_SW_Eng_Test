# import from standard library
# import from installed packages
import pytest
import numpy as np
# import from project
from earthquakes.tools import get_haversine_distance


@pytest.fixture
def sample_locations():
    asset = (35.2, 25.1)
    eq_lat = [35.2, 37.32, -75, 45]
    eq_long = [25.1, 23, 30, -20]
    distances = [0, 301.68, 12258.95, 3932.67]
    return asset, eq_lat, eq_long, distances


class TestGetHaversineDistance:
    def test_sample_locations(self, sample_locations):
        asset, eq_lat, eq_long, distances = sample_locations
        haversine_distances = get_haversine_distance(latitude_list=eq_lat, longitude_list=eq_long,
                                                     point_latitude=asset[0], point_longitude=asset[1])
        assert np.allclose(distances, haversine_distances)

    def test_invalid_asset(self, sample_locations):
        _, eq_lat, eq_long, distances = sample_locations
        assets = [(35.2, 190), (-110, 35.2)]
        for asset in assets:
            with pytest.raises(ValueError):
                get_haversine_distance(latitude_list=eq_lat, longitude_list=eq_long,
                                       point_latitude=asset[0], point_longitude=asset[1])

    def test_incomplete_location_lat(self, sample_locations):
        asset, eq_lat, eq_long, distances = sample_locations
        del eq_lat[1]
        # Raise value error since we cannot be sure which location data is missing
        with pytest.raises(ValueError):
            get_haversine_distance(latitude_list=eq_lat, longitude_list=eq_long,
                                   point_latitude=asset[0], point_longitude=asset[1])

    def test_incomplete_location_long(self, sample_locations):
        asset, eq_lat, eq_long, distances = sample_locations
        del eq_long[1]
        # Raise value error since we cannot be sure which location data is missing
        with pytest.raises(ValueError):
            get_haversine_distance(latitude_list=eq_lat, longitude_list=eq_long,
                                   point_latitude=asset[0], point_longitude=asset[1])

    def test_invalid_location_lat(self, sample_locations):
        asset, eq_lat, eq_long, distances = sample_locations
        eq_lat[1] = 95
        with pytest.raises(ValueError):
            get_haversine_distance(latitude_list=eq_lat, longitude_list=eq_long,
                                   point_latitude=asset[0], point_longitude=asset[1])

    def test_invalid_location_long(self, sample_locations):
        asset, eq_lat, eq_long, distances = sample_locations
        eq_long[2] = -190
        with pytest.raises(ValueError):
            get_haversine_distance(latitude_list=eq_lat, longitude_list=eq_long,
                                   point_latitude=asset[0], point_longitude=asset[1])


