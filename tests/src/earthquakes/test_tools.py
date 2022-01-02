# import from standard library
# import from installed packages
import pytest
import numpy as np
import pandas as pd
# import from project
from earthquakes.tools import get_haversine_distance, compute_payouts, compute_burning_cost
from earthquakes.tools import TIME_COLUMN, DISTANCE_COLUMN, LATITUDE_COLUMN, MAGNITUDE_COLUMN, \
    LONGITUDE_COLUMN, CONTRIBUTOR_ID_COLUMN, GAP_COLUMN, DEPTH_COLUMN, DEPTH_ERROR_COLUMN, MAGNITUDE_ERROR_COLUMN, \
    PLACE_COLUMN, STATUS_COLUMN, EVENT_TYPE_COLUMN, MAGNITUDE_TYPE_COLUMN, MAGNITUDE_SOURCE_COLUMN, \
    LOCATION_SOURCE_COLUMN, NUMBER_SEISMIC_STATIONS_LOCATION_COLUMN, NUMBER_SEISMIC_STATIONS_MAGNITUDE_COLUMN, \
    TIME_UPDATED_COLUMN, TRAVEL_TIME_RESIDUAL_COLUMN, EVENT_IDENTIFIER_COLUMN, HORIZONTAL_ERROR_COLUMN, \
    MIN_DISTANCE_EPICENTER_STATION_COLUMN


@pytest.fixture
def sample_locations():
    asset = (35.2, 25.1)
    eq_lat = [35.2, 37.32, -75, 45]
    eq_long = [25.1, 23, 30, -20]
    distances = [0, 302.01, 12272.40, 3936.99]
    return asset, eq_lat, eq_long, distances


@pytest.fixture
def sample_earthquake_data_with_payouts():
    earthquake_data = pd.DataFrame([
        ["2021-10-12T09:24:05.099Z", 35.1691, 26.2152, 20.0, 6.4, "mww", np.nan, 19.0, 0.860, 0.46, "us",
         "us6000ftxu", "2021-12-18T19:58:57.040Z", "4 km SW of Palekastro, Greece", "earthquake", 6.1, 1.8,
         0.048, 42.0, "reviewed", "us", "us", 44.198651],
        ["2021-10-03T14:31:27.622Z", 35.1442, 25.2375, 10.0, 4.6, "mb", np.nan, 119.0, 0.318, 0.64, "us",
         "us6000fsp1", "2021-12-10T21:14:19.040Z", "2 km W of Arkalochóri, Greece", "earthquake", 5.0, 1.9,
         0.165, 13.0, "reviewed", "us", "us", 49.673412],
        ["2021-09-29T11:54:48.885Z", 35.0268, 25.1561, 10.0, 4.6, "mb", np.nan, 69.0, 0.339, 0.83, "us",
         "us6000fq3y", "2021-12-04T14:27:58.040Z", "2 km N of Pýrgos, Greece", "earthquake", 5.1, 1.3,
         0.068, 64.0, "reviewed", "us", "us", 55.323314],
        ["2020-09-28T15:13:16.867Z", 35.2054, 25.2791, 10.0, 4.7, "mb", np.nan, 58.0, 0.329, 0.70, "us",
         "us7000ff84", "2021-12-04T14:30:09.040Z", "1 km N of Thrapsanón, Greece", "earthquake", 6.9, 1.8,
         0.067, 73.0, "reviewed", "us", "us", 48.422808],
        ["2016-09-28T04:48:08.650Z", 35.0817, 25.2018, 10.0, 7, "mww", np.nan, 43.0, 0.328, 0.94, "us",
         "us7000ff36", "2021-12-04T14:30:04.040Z", "9 km SW of Arkalochóri, Greece", "earthquake", 4.5, 1.7,
         0.046, 45.0, "reviewed", "us", "us", 8.527937],
    ],
        columns=[TIME_COLUMN, LATITUDE_COLUMN, LONGITUDE_COLUMN, DEPTH_COLUMN, MAGNITUDE_COLUMN, MAGNITUDE_TYPE_COLUMN,
                 NUMBER_SEISMIC_STATIONS_LOCATION_COLUMN, GAP_COLUMN, MIN_DISTANCE_EPICENTER_STATION_COLUMN,
                 TRAVEL_TIME_RESIDUAL_COLUMN, CONTRIBUTOR_ID_COLUMN, EVENT_IDENTIFIER_COLUMN, TIME_UPDATED_COLUMN,
                 PLACE_COLUMN, EVENT_TYPE_COLUMN, HORIZONTAL_ERROR_COLUMN, DEPTH_ERROR_COLUMN, MAGNITUDE_ERROR_COLUMN,
                 NUMBER_SEISMIC_STATIONS_MAGNITUDE_COLUMN, STATUS_COLUMN, LOCATION_SOURCE_COLUMN,
                 MAGNITUDE_SOURCE_COLUMN,
                 DISTANCE_COLUMN]
    )
    payouts_structure = [[10, 4.5, 100], [50, 5.5, 75], [200, 6.5, 50]]
    payouts = {2021: 75, 2020: 0, 2016: 100, 2017: 0, 2018: 0, 2019: 0}

    return earthquake_data, payouts_structure, payouts


@pytest.fixture
def sample_burning_cost():
    payouts = {2000: 100, 2005: 50, 2006: 0, 2012: 50}
    burning_costs = [[2000, 2012, 15.3846154], [2000, 2006, 21.428571], [2006, 2012, 7.1428571]]
    return payouts, burning_costs


class TestGetHaversineDistance:
    def test_sample_locations(self, sample_locations):
        asset, eq_lat, eq_long, distances = sample_locations
        haversine_distances = get_haversine_distance(latitude_list=eq_lat, longitude_list=eq_long,
                                                     point_latitude=asset[0], point_longitude=asset[1])
        assert np.allclose(distances, haversine_distances)

    def test_return_size(self, sample_locations):
        asset, eq_lat, eq_long, distances = sample_locations
        haversine_distances = get_haversine_distance(latitude_list=eq_lat, longitude_list=eq_long,
                                                     point_latitude=asset[0], point_longitude=asset[1])
        assert len(haversine_distances) == len(distances)

    def test_return_type(self, sample_locations):
        asset, eq_lat, eq_long, distances = sample_locations
        haversine_distances = get_haversine_distance(latitude_list=eq_lat, longitude_list=eq_long,
                                                     point_latitude=asset[0], point_longitude=asset[1])
        assert isinstance(haversine_distances, (np.ndarray, list))

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


class TestComputePayouts:
    def test_sample_payout(self, sample_earthquake_data_with_payouts):
        earthquake_data, payouts_structure, payouts = sample_earthquake_data_with_payouts
        payouts_test = compute_payouts(earthquake_data=earthquake_data, payouts_structure=payouts_structure)
        assert payouts_test == payouts

    def test_empty_data(self, sample_earthquake_data_with_payouts):
        _, payouts_structure, _ = sample_earthquake_data_with_payouts
        earthquake_data = pd.DataFrame()
        with pytest.raises(ValueError):
            compute_payouts(earthquake_data=earthquake_data, payouts_structure=payouts_structure)

    def test_empty_payouts_structure(self, sample_earthquake_data_with_payouts):
        earthquake_data, _, _ = sample_earthquake_data_with_payouts
        payouts_structure = []
        with pytest.raises(ValueError):
            compute_payouts(earthquake_data=earthquake_data, payouts_structure=payouts_structure)

    def test_invalid_return_type(self, sample_earthquake_data_with_payouts):
        earthquake_data, payouts_structure, _ = sample_earthquake_data_with_payouts
        with pytest.raises(TypeError):
            compute_payouts(earthquake_data=earthquake_data, payouts_structure=payouts_structure, return_type='')

    def test_return_dict(self, sample_earthquake_data_with_payouts):
        earthquake_data, payouts_structure, _ = sample_earthquake_data_with_payouts
        payouts_test = compute_payouts(earthquake_data=earthquake_data, payouts_structure=payouts_structure,
                                       return_type='dict')
        assert isinstance(payouts_test, dict)

    def test_return_series(self, sample_earthquake_data_with_payouts):
        earthquake_data, payouts_structure, _ = sample_earthquake_data_with_payouts
        payouts_test = compute_payouts(earthquake_data=earthquake_data, payouts_structure=payouts_structure,
                                       return_type='series')
        assert isinstance(payouts_test, pd.Series)


class TestComputeBurningCost:
    def test_sample_burning_cost(self, sample_burning_cost):
        payouts, burning_costs = sample_burning_cost
        for item in burning_costs:
            burning_cost = compute_burning_cost(payouts=payouts, start_year=item[0], end_year=item[1])
            assert np.allclose(burning_cost, item[2])

    def test_empty_payouts_dict(self):
        with pytest.raises(ValueError):
            compute_burning_cost({}, 2000, 2012)

    def test_empty_payouts_series(self):
        with pytest.raises(ValueError):
            compute_burning_cost(pd.Series(dtype=float), 2000, 2012)

    def test_years_outside_bounds(self, sample_burning_cost):
        payouts, burning_costs = sample_burning_cost
        with pytest.raises(AttributeError):
            compute_burning_cost(payouts=payouts, start_year=2000, end_year=2013)
        with pytest.raises(AttributeError):
            compute_burning_cost(payouts=payouts, start_year=1999, end_year=2010)
