import pandas as pd
import numpy as np
from bokeh.models import HoverTool
from bokeh.models import DatetimeTickFormatter
import holoviews as hv
import geoviews as gv
import panel as pn
import itertools


class JourneyVisualization:

    def __init__(self, solutions, stations, stop_time):
        self.solutions = format_solutions(solutions, stations)
        self.stations = stations
        self.stop_time = stop_time
        
        self.line_aggregate = aggregate_lines(self.solutions)
        self.journey_aggregate = aggregate_journey(self.solutions)
        
        self.timetable_hover = HoverTool(tooltips=[('Line', '@line_id')])
        self.timetable_tap_stream = self._timetable_tap_stream()
        self._timetable = hv.DynamicMap(self._timetable, streams=[self.timetable_tap_stream])
        self.timetable = pn.pane.HoloViews(self._timetable)
        
        self.map_path_data = map_path_data(self.solutions)
        self.map_station_hover = HoverTool(tooltips=[('', '@station_name')])
        self.map_edge_hover = HoverTool(tooltips=[('Departure', '@departure'), ('Arrival', '@arrival')])
        
        self.map_tiles = gv.tile_sources.CartoLight()
        # TODO: show points
        # self.map_points = gv.Points(self.stations, ['Longitude', 'Latitude'], ['station_name'])
        self.map = pn.pane.HoloViews(hv.DynamicMap(self._map, streams=self._timetable.streams))
        self.interface = pn.Row(self.timetable, self.map)
         
            
    def _timetable_tap_stream(self):
        return hv.streams.SingleTap(x=0, y=0)
            
        
    def _timetable(self, x, y):
        stop_time = self.stop_time * 10**3
        time_delta = stop_time - self.solutions['start_time'].min()
        boxes_opts = {
            'color': 'color',
            'line_width': 0,
            'tools': [HoverTool(tooltips=[
                ('From', '@station_name'),
                ('To', '@station_name_stop'),
                ('Departure Time', '@departure'), 
                ('Arrival Time', '@arrival'),
                ('Travel Type', '@transport_type'),
                ('Line', '@line_id')])],
        }
        opts = {
            'height': int(self.solutions['path'].max() + 3) * 50,
            'width': 600,
            'ylim': (-1, self.solutions['path'].max() + 2),
            'xlim': (self.solutions['start_time'].min() - time_delta * 0.1, stop_time + time_delta * 0.1),
            'hooks': [datetime_ticks],
            'yaxis': None,
            'show_frame': False,
            'xlabel': '',
            'toolbar': None,
            'active_tools': []
        }
        boxes = hv.Rectangles(
            self.line_aggregate, 
            ['start_time', 'y_min', 'stop_time', 'y_max'], 
            ['color', 'station_name', 'station_name_stop', 'departure', 'arrival', 'transport_type', 'line_id']
        ).opts(**boxes_opts)
        text = self._timetable_text()
        stop_line = hv.VLine(stop_time).opts(line_width=1, line_color='red')
        return (boxes * text * stop_line).opts(**opts)

    
    def _timetable_text(self):
        fontsize = 8
        texts = []
        for _, connection in self.line_aggregate.iterrows():
            start_time = connection['start_time']
            y = connection['y_min']
            icon = transport_icons[connection['transport_type']]
            # TODO print real short names
            if connection['transport_type'] != 'foot':
                short_line = int(connection['line_id'].split(':')[-1])
            else:
                short_line = ''
            texts.append(hv.Text(x=start_time, y=y - 0.15, text=f'{icon}{short_line}', halign='left', valign='top', fontsize=fontsize))
        
        for _, journey in self.journey_aggregate.iterrows():
            arrival_text = journey['travel_time_str'] + ' - ' + journey['arrival']
            probability_text = f" {journey['probability']:6.3%}"
            texts.extend([
                hv.Text(x=journey['start_time'], y=journey['y_max'], text=journey['departure'], halign='left', valign='bottom', fontsize=fontsize),
                hv.Text(x=journey['stop_time'], y=journey['y_max'], text=arrival_text, halign='right', valign='bottom', fontsize=fontsize),
                hv.Text(x=self.stop_time * 10**3, y=journey['path'], text=probability_text, halign='left', valign='bottom', fontsize=fontsize)
            ])
        return hv.Overlay(texts)
    
    
    def _map(self, x, y):
        opts = {
            'line_width': 5,
            'xaxis': None,
            'yaxis': None,
            'line_join': 'bevel',
            'line_cap': 'round',
            'show_frame': False,
            
        }
        selected_path = int(np.clip(np.round(y), 0, self.journey_aggregate['path'].max()))
        color_path = gv.Path(self.map_path_data, ['lat', 'lon'], ['color', 'path']).opts(color='color', **opts)
        hover_path = gv.Path(self.map_path_data, ['lat', 'lon'], ['line_id']).opts(line_alpha=0, tools=['hover'], **opts)
        return self.map_tiles * (color_path * hover_path).select(path=selected_path)
    
    def _stations(self, selected_path):
        pass
    

def datetime_ticks(plot, element):
    plot.handles['xaxis'].formatter = DatetimeTickFormatter(minutes='%H:%M', hours='%H:%M')


def format_solutions(solutions, stations):
    solutions = add_datetime(solutions)
    solutions = add_station_info(solutions, stations)
    solutions = add_color(solutions)
    solutions = add_departure_arrival(solutions)
    solutions = add_yaxis(solutions)
    return solutions


def add_datetime(solutions):
    time_columns = [col for col in solutions.columns if 'time' in col]
    solutions[[col + '_dt' for col in time_columns]] = (solutions[time_columns] * 10**9).astype('datetime64[ns]')
    solutions[time_columns] = solutions[time_columns] * 10**3
    return solutions


def add_station_info(solutions, stations):
    joined = (
        solutions
        .join(stations.set_index('station_id'), 'start_id')
        .join(stations.set_index('station_id'), 'stop_id', rsuffix='_stop')
    )
    joined.columns = [col.lower() for col in joined.columns]
    return joined


def add_color(solutions, colormap='Category20'):
    def line_category(line_id):
        if line_id.startswith('foot'):
            return 'foot'
        else:
            return line_id
    categories = {line_category(line_id) for line_id in solutions['line_id'].unique()}
    color_dict = {category: color for category, color in zip(categories, itertools.cycle(hv.Cycle(colormap).values))}
    solutions['color'] = solutions['line_id'].map(lambda k: color_dict[line_category(k)])
    return solutions


def add_departure_arrival(solutions):
    solutions['departure'] = solutions['start_time_dt'].dt.strftime('%H:%M')
    solutions['arrival'] = solutions['stop_time_dt'].dt.strftime('%H:%M')
    return solutions


def add_yaxis(solutions):
    solutions['y_min'] = solutions['path'] - 0.1
    solutions['y_max'] = solutions['path'] + 0.1
    return solutions


def aggregate_lines(solutions):
    """Aggregates sequential connections on the same line to a single connection"""
    aggregated = (
        solutions
        .groupby(['path', 'line_id'])
        .agg({
            'start_id': 'first',
            'start_time': 'first',
            'start_time_dt': 'first',
            'line_id': 'first', 
            'transport_type': 'first',
            'probability': 'last',
            'stop_time': 'last',
            'stop_time_dt': 'last',
            'stop_id': 'last',
            'transfers': 'first',
            'path': 'first',
            'departure': 'first',
            'arrival': 'last',
            'color': 'first',
            'y_min': 'first',
            'y_max': 'first',
            'station_name': 'first',
            'station_name_stop': 'last'
        })
        .reset_index(drop=True)
        .sort_values(['path', 'start_time'])
        
    )
    return aggregated


def aggregate_journey(solutions):
    aggregated = (
        solutions
        .groupby('path')
        .agg({
            'path': 'first',
            'start_time': 'first',
            'stop_time': 'last',
            'departure': 'first',
            'arrival': 'last',
            'y_min': 'first',
            'y_max': 'first',
            'probability': 'first'
        })
    )
    travel_time = (aggregated['stop_time'] - aggregated['start_time'])
    hours = ((travel_time // 3600_000) % 24).astype(str)
    hours.loc[hours != '0'] += 'h '
    hours.loc[hours == '0'] = ''
    minutes = ((travel_time // 60_000) % 60).astype(str)
    minutes.loc[minutes != '0'] += 'm'
    minutes.loc[minutes == '0'] = ''
    aggregated['travel_time_str'] = hours + minutes
    return aggregated



def map_path_data(solutions):
    aggregated = (
        solutions
        .groupby(['path', 'line_id'])
        .agg({
            'lat': list,
            'lon': list,
            'lat_stop': 'last',
            'lon_stop': 'last',
            'station_name': 'first',
            'station_name_stop': 'last',
            'start_time': 'first',
            'stop_time': 'last',
            'color': 'first'
        })
        .reset_index()
    )
    edge_paths = []
    for i, row in aggregated.iterrows():
        row_dict = row.to_dict()
        row_dict['lat'] = [*row['lat'], row['lat_stop']]
        row_dict['lon'] = [*row['lon'], row['lon_stop']]
        edge_paths.append(row_dict)
    return edge_paths


transport_icons = {
    'zug': u'\U0001f686',
    'tram': u'\U0001f68a',
    'bus': u'\U0001f68d',
    'schiff': u'\U000026f4',
    'foot': u'\U0001f45f'
}