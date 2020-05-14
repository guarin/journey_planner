import pandas as pd
import numpy as np
import networkx as nx
import datetime as dt
import pickle

def datetime_from_str(series, format="%d.%m.%Y %H:%M"):
    """Converts string to datetime"""
    return pd.to_datetime(series, format=format)

def timestamp_from_datetime(series):
    """Converts datetime to timestamp in seconds"""
    
    ts = (series.astype(np.int64) // (10 ** 9)).astype(np.int32)
    ts.loc[ts < 0] = np.int32(2 ** 31 - 1)
    return ts

def datetime_from_timestamp(series):
    """Converts timestamp in seconds to datetime"""
    dt = pd.to_datetime(series.astype(np.int64) * (10 ** 9))
    dt.loc[series == 2 ** 31 - 1] = pd.NaT
    return dt

def distance(ser1, ser2):
    return np.sqrt(np.sum((ser1.values - ser2.values)**2, axis=1)) / 360 * 42000

def expected_times(connections, stations, start_id, stop_id):
    start_point = stations.loc[stations['station_id'] == start_id, ['lat', 'lon']].iloc[0].values[np.newaxis, :]
    stop_point = stations.loc[stations['station_id'] == stop_id, ['lat', 'lon']].iloc[0].values[np.newaxis, :]
    conn = connections.join(stations.set_index('station_id'), 'start_id', how='inner').join(stations.set_index('station_id'), 'stop_id', rsuffix='_stop', how='inner')
    start_start_distance = distance(start_point, conn[['lat', 'lon']])
    stop_stop_distance = distance(stop_point, conn[['lat_stop', 'lon_stop']].rename({'lat_stop': 'lat', 'lon_stop': 'lon'}, axis=1))
    bus = conn['transport_type'] == 'bus'
    zug = conn['transport_type'] == 'zug'
    tram = conn['transport_type'] == 'tram'
    schiff = conn['transport_type'] == 'schiff'
    speed = bus * 20 + zug * 50 + tram * 20 + schiff * 5
    conn['expected_departure_time'] = (conn['start_time'] - start_start_distance / speed * 3600).astype(np.int32)
    conn['expected_arrival_time'] = (conn['stop_time'] + stop_stop_distance / speed * 3600).astype(np.int32)
    return conn


def load_connections():
    df = pd.read_csv('../data/2018-04-01istdaten.csv', sep=';', low_memory=False)

    df.columns = list(map(str.lower, df.columns))
    df['bpuic'] = df['bpuic'].astype(np.int32)
    df['ankunftszeit'] = datetime_from_str(df['ankunftszeit'])
    df['abfahrtszeit'] = datetime_from_str(df['abfahrtszeit'])
    df['produkt_id'] = df['produkt_id'].str.lower()
    df = df[(df['zusatzfahrt_tf'] == False) & (df['faellt_aus_tf'] == False) & (df['durchfahrt_tf'] == False)]
    df = df.rename({
        'bpuic': 'start_id', 
        'ankunftszeit': 'stop_time',
        'abfahrtszeit': 'start_time',
        'linien_id': 'line_id',
        'fahrt_bezeichner': 'trip_id',
        'produkt_id': 'transport_type'
    }, axis=1)

    df = df.sort_values(['line_id', 'trip_id', 'start_time']).reset_index(drop=True)
    df = df.loc[:, ['start_id', 'start_time', 'line_id', 'transport_type', 'stop_time']]
    df = df.drop_duplicates()

    df_ = df.iloc[:-1].copy()
    df_['stop_id'] = df['start_id'].values[1:]
    df_['stop_time'] = df['stop_time'].values[1:]
    df_['stop_line_id'] = df['line_id'].values[1:]
    connections = df_.loc[df_['start_time'].notna() & df_['stop_time'].notna() & (df_['line_id'] == df_['stop_line_id']), ['start_id', 'start_time', 'line_id', 'transport_type', 'stop_time', 'stop_id']].copy()
    connections['start_time'] = timestamp_from_datetime(connections['start_time'])
    connections['stop_time'] = timestamp_from_datetime(connections['stop_time'])
    return connections


def estimate_departure_arrival(connections, start_id, stop_id):
    edges = connections.loc[:, ['start_id', 'stop_id']]
    edges['time'] = connections['stop_time'] - connections['start_time']
    # TODO: no times should be negative
    edges = edges[edges['time'] >= 0]
    edges[edges['time'] == 0] += 15
    edges = edges.sort_values('time').drop_duplicates(['start_id', 'stop_id'])
    edges = edges.reset_index(drop=True)
    graph = nx.from_pandas_edgelist(edges, source='start_id', target='stop_id', edge_attr='time')
    from_start = nx.algorithms.shortest_path_length(graph, source=start_id, weight='time')
    to_stop = nx.algorithms.shortest_path_length(graph, target=stop_id, weight='time')
    from_start = pd.DataFrame(from_start.items(), columns=['station_id', 'time_from_start']).set_index('station_id')
    to_stop = pd.DataFrame(to_stop.items(), columns=['station_id', 'time_to_stop']).set_index('station_id')
    connections = connections.join(from_start, 'start_id').join(to_stop, 'stop_id')
    connections['expected_departure_time'] = connections['start_time'] - connections['time_from_start']
    connections['expected_arrival_time'] = connections['stop_time'] + connections['time_to_stop']
    # TODO: there should be no NA
    connections = connections.dropna()
    connections[['expected_departure_time', 'expected_arrival_time']] = connections[['expected_departure_time', 'expected_arrival_time']].astype(np.int32)
    return connections
    

def load(start_id, stop_id):

    connections = load_connections()
    stations = pd.read_csv('../data/station.csv')

    start_point = stations.loc[stations['station_id'] == start_id, ['lat', 'lon']].iloc[0].values[np.newaxis, :]
    stop_point = stations.loc[stations['station_id'] == stop_id, ['lat', 'lon']].iloc[0].values[np.newaxis, :]
    max_search_time = max(3600, int(distance(start_point, stop_point) / 50 * 3600 * 10))
    connections = expected_times(connections, stations, start_id, stop_id)
    stations = stations[['station_id', 'lat', 'lon', 'station_name']].copy()
    
    return connections, stations, max_search_time
    
    
def create_zurich_data():
    connections = load_connections()
    s = pd.read_csv('../data/station.csv')
    morning = dt.datetime(year=2018, month=4, day=1, hour=5) + dt.timedelta(hours=2)
    evening = dt.datetime(year=2018, month=4, day=1, hour=21) + dt.timedelta(hours=2)
    z = s[(s['lat'] >= 8.540192 - 0.1) & (s['lat'] <= 8.540192 + 0.1) & (s['lon'] >= 47.378177 - 0.1) & (s['lon'] <= 47.378177 + 0.1)]
    z = z.set_index('station_id', drop=False)
    z = z.sort_index()
    
    cz = connections[connections['start_id'].isin(z['station_id']) & connections['stop_id'].isin(z['station_id'])]
    cz = cz[(cz['stop_time'] >= morning.timestamp()) & (cz['stop_time'] <= evening.timestamp())]
    cz = cz[cz['stop_time'] >= cz['start_time']]
    cz['trip_index'] = np.arange(len(cz))
    # TODO: make sure this is done!
    # we need a number that tracks connection in trip
    cz = cz.sort_values(['stop_time', 'start_time', 'trip_index'], ascending=[False, False, True])
    cz = cz.drop(columns='trip_index')
    cz = cz.reset_index(drop=True)
    z = z[z['station_id'].isin(cz['start_id']) | z['station_id'].isin(cz['stop_id'])].copy()
    z['key'] = 0
    nearby = z.merge(z, on='key')
    nearby = nearby[distance(nearby[['lat_x', 'lon_x']], nearby[['lat_y', 'lon_y']]) <= 0.5]
    nearby = nearby[nearby['station_id_x'] != nearby['station_id_y']]
    nearby = nearby[['station_id_x', 'station_id_y']]
    nearby['distance'] = 5*60
    grouped = nearby.groupby('station_id_x').agg(list)
    footpaths = {station_id: list(zip(*row)) for station_id, row in grouped.iterrows()}
    
    with open('../data/connections_zurich.pickle', 'wb') as file:
        pickle.dump(cz, file)
        
    with open('../data/footpaths_zurich.pickle', 'wb') as file:
        pickle.dump(footpaths, file)
        
    with open('../data/stations_zurich.pickle', 'wb') as file:
        pickle.dump(z, file)
        
        
def load_zurich():
    with open('../data/connections_zurich.pickle', 'rb') as file:
        connections = pickle.load(file)
    with open('../data/footpaths_zurich.pickle', 'rb') as file:
        footpaths = pickle.load(file)
    with open('../data/stations_zurich.pickle', 'rb') as file:
        stations = pickle.load(file)
    return connections, footpaths, stations
    
    
    