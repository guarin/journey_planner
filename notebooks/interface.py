import dummy_data
from journey_planner import JourneyPlanner, id_from_name
from journey_finder import JourneyFinder
from journey_visualization import JourneyVisualization
import pandas as pd

import panel as pn
pn.extension()

connections, footpaths, stations = dummy_data.load_zurich()
jp = JourneyPlanner(stations)
journey_planner = jp.interface
journey_finder = JourneyFinder(connections, footpaths)


def journeys():
    departure_station_id = id_from_name(stations, jp.departure_station_widget.value)
    arrival_station_id = id_from_name(stations, jp.arrival_station_widget.value)
    arrival_time = int(pd.to_datetime(jp.arrival_time_widget.value).timestamp())
    min_probability = jp.min_probability_widget.value
    journey_finder.find(departure_station_id, arrival_station_id, arrival_time, min_probability=min_probability)
    best_journeys = journey_finder.best_journeys()
    return JourneyVisualization(best_journeys, stations, arrival_time).interface