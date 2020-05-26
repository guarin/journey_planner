import numpy as np
import pandas as pd
import datetime

import holoviews as hv
import geoviews as gv
import panel as pn

from bokeh.models import HoverTool


def id_from_name(stations, name):
    return stations.loc[stations['station_name'] == name, 'station_id'].values[0]


def closest_station(stations, lat, lon):
    distances = np.sum((stations[['lat', 'lon']] - np.array([lat, lon])) ** 2, axis=1)
    closest = np.argmin(distances)
    return stations.iloc[closest]['station_id']


def set_to_closest_station(stations, widget, lat, lon):
    station_id = closest_station(stations, lat, lon)
    station_name = stations.loc[station_id, 'station_name']
    if widget.value != station_name:
        widget.value = station_name

        
class JourneyPlanner:
    
    def __init__(self, stations):
        self.default_departure_station = 'Zürich HB'
        self.default_arrival_station = 'Zürich, Auzelg'
        self.default_departure_id = id_from_name(stations, self.default_departure_station)
        self.default_arrival_id = id_from_name(stations, self.default_arrival_station)
        zurich = stations.loc[self.default_departure_id]
        self.stations = stations
        self.station_names = list(self.stations['station_name'])
        
        self.default_arrival_time = datetime.datetime.fromisoformat('2019-05-06 12:30:00')
        self.default_min_success_probability = 0
        self.tiles = gv.tile_sources.CartoLight()
        self.unselected_hover = HoverTool(tooltips=[('', '@station_name')])
        self.departure_hover = HoverTool(tooltips=[('Departure Station', '@station_name')])
        self.arrival_hover = HoverTool(tooltips=[('Arrival Station', '@station_name')])
        
        self.departure_station_widget = pn.widgets.AutocompleteInput(
            name='Departure Station',
            value=self.default_departure_station,
            options=self.station_names
        )
        self.arrival_station_widget = pn.widgets.AutocompleteInput(
            name='Arrival Station',
            value=self.default_arrival_station,
            options=self.station_names
        )
        self.arrival_time_widget = pn.widgets.DatetimeInput(
            name='Arrival Time', 
            value=self.default_arrival_time
        )
        self.min_probability_widget = pn.widgets.FloatSlider(
            name='Minium Success Probability', 
            start=0.0, 
            end=1.0,
            value=self.default_min_success_probability
        )
        
        self.departure_tap_stream = hv.streams.SingleTap(
            x=stations.loc[self.default_departure_id, 'lat'], 
            y=stations.loc[self.default_departure_id, 'lon']
        ).rename(x='departure_lat', y='departure_lon')
        
        self.arrival_tap_stream = hv.streams.DoubleTap(
            x=stations.loc[self.default_arrival_id, 'lat'], 
            y=stations.loc[self.default_arrival_id, 'lon']
        ).rename(x='arrival_lat', y='arrival_lon')
        
        self.departure_tap_stream.add_subscriber(lambda departure_lat, departure_lon: set_to_closest_station(self.stations, self.departure_station_widget, departure_lat, departure_lon))
        self.arrival_tap_stream.add_subscriber(lambda arrival_lat, arrival_lon: set_to_closest_station(self.stations, self.arrival_station_widget, arrival_lat, arrival_lon))
        self.departure_station_widget.link(self.departure_tap_stream, callbacks={'value': self._update_stream})
        self.arrival_station_widget.link(self.arrival_tap_stream, callbacks={'value': self._update_stream})
        
        self.station_map = gv.DynamicMap(
            self._station_map(), 
            streams=[
                self.departure_tap_stream, 
                self.arrival_tap_stream
            ]
        )
        self.widgets = pn.Column(
            self.departure_station_widget, 
            self.arrival_station_widget, 
            self.arrival_time_widget, 
            self.min_probability_widget
        )
        
        self.interface = pn.Row(
            pn.Spacer(height=600),
            pn.Column(self.widgets, max_width=400),
            self.station_map
        )

    
    def _station_map(self):
        def inner(departure_lat, departure_lon, arrival_lat, arrival_lon):
            opts = {
                'xaxis': None,
                'yaxis': None,
                'responsive': True,
                'active_tools': ['wheel_zoom']
            }
            departure_station_id = closest_station(self.stations, departure_lat, departure_lon)
            arrival_station_id = closest_station(self.stations, arrival_lat, arrival_lon)
            unselected_stations = self.stations.loc[~self.stations['station_id'].isin([departure_station_id, arrival_station_id])]
            departure_station = self.stations.loc[[departure_station_id]]
            arrival_station = self.stations.loc[[arrival_station_id]]
            unselected = gv.Points(unselected_stations, ['lat', 'lon'], ['station_name']).opts(tools=[self.unselected_hover])
            departure = gv.Points(departure_station, ['lat', 'lon'], ['station_name']).opts(tools=[self.departure_hover], size=5, color='black')
            arrival = gv.Points(arrival_station, ['lat', 'lon'], ['station_name']).opts(tools=[self.arrival_hover], size=5, color='red')
            return (self.tiles * unselected * departure * arrival).opts(**opts)
        return inner
    
    
    def _update_stream(self, stream, event):
        station_name = event.new
        station_id = id_from_name(self.stations, station_name) 
        lat = self.stations.loc[station_id]['lat']
        lon = self.stations.loc[station_id]['lon']
        if (stream.x != lat) or (stream.y != lon):
            stream.event(x=lat, y=lon)
    
    
    
    