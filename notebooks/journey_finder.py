import numpy as np
import pandas as pd
import collections


Connection = collections.namedtuple('Connection', 'start_id start_time line_id transport_type stop_time stop_id delay_probability delay_parameter')

class JourneyFinder:
    
    def __init__(self, connections, footpaths):
        self.connections = [Connection(*row) for row in connections.values]
        self.footpaths = footpaths
        self._unique_stations = np.unique([(c.start_id, c.stop_id) for c in self.connections])
        self._stations = None
        self._departure_station_id = None
    
    def find(self, departure_station_id, arrival_station_id, arrival_time, 
             min_probability=0.9, max_probability=0.999999, transfer_time=120):
        self._departure_station_id = departure_station_id
        self._stations = find(self.connections, self.footpaths, self._unique_stations, 
                              departure_station_id, arrival_station_id, arrival_time, 
                             min_probability, max_probability, transfer_time)
        
    def best_journeys(self):
        return best_journeys(self._stations, self._departure_station_id)
        
        
        
def find(connections, footpaths, unique_stations, departure_station_id, arrival_station_id, arrival_time, 
             min_probability, max_probability, transfer_time):
    
    stations = {station_id: (0.0, -1, []) for station_id in unique_stations}
    stations[arrival_station_id] = (1.0, arrival_time, [(None, 1.0, Connection(arrival_station_id, arrival_time, None, None, None, None, None, None))])
    departure_min_time = -1
    start_index = np.argmax(np.array([c.stop_time for c in connections]) <= arrival_time)
    foot_counter = 0
    for c in connections[start_index:]:
        if c.stop_time < departure_min_time:
            break

        stop_p, _, stop_connections = stations[c.stop_id]
        if stop_p >= min_probability:
            start_p, start_min_time, start_connections = stations[c.start_id]
            if c.start_time >= start_min_time:
                # calculate best probability to catch any of the connections departing from stop
                probabilities = [(index, p * (1 - (stop.line_id != c.line_id)*c.delay_probability*np.exp(-c.delay_parameter * (stop.start_time - c.stop_time - transfer_time)))) for index, (_, p, stop) in enumerate(stop_connections) if (((stop.line_id == c.line_id) and (stop.start_time >= c.stop_time)) or (stop.start_time >= c.stop_time + transfer_time))]
                if probabilities:
                    index, p = max(probabilities, key=lambda x: x[1])

                    if p >= min_probability:
                        if start_connections:
                            start = start_connections[-1]                        

                        if not start_connections or not ((start[1] > p) and (start[2].start_time > c.start_time)):
                            start_connections.append((index, p, c))
                            max_p = max(p, start_p)
                            if max_p >= max_probability:
                                start_min_time = c.start_time
                                if c.start_id == departure_station_id:
                                    departure_min_time = start_min_time
                            stations[c.start_id] = (max_p, start_min_time, start_connections)

                            index = len(start_connections) - 1
                            for previous_id, walk_time in footpaths.get(c.start_id, []):
                                previous_departure_time = c.start_time - walk_time - transfer_time
                                previous_p, previous_min_time, previous_connections = stations[previous_id]
                                if previous_departure_time >= previous_min_time:
                                    if previous_connections:
                                        previous = previous_connections[-1]

                                    if not previous_connections or not ((previous[1] > p) and (previous[2].start_time > previous_departure_time)):
                                        previous_connections.append((index, p, Connection(previous_id, previous_departure_time, f'foot:{foot_counter}', 'foot', previous_departure_time + walk_time, c.start_id, 0, 0)))
                                        foot_counter += 1
                                        max_p = max(p, previous_p)
                                        if max_p >= max_probability:
                                            previous_min_time = previous_departure_time
                                        stations[previous_id] = (max_p, previous_min_time, previous_connections)

    return stations


def concatenate(solutions):
    """Concatenates a list of unpivoted solutions dataframes"""
    i = 0
    for solution in solutions:
        solution['path'] += i
        i = solution['path'].max() + 1
    return pd.concat(solutions)


def to_df(journey):
    values = []
    transfers = set()
    for p, c in journey:
        transfers.add(c.line_id)
        values.append([*c, p, len(transfers), 0])
    df = pd.DataFrame(values, columns=['start_id', 'start_time', 'line_id', 'transport_type', 'stop_time', 'stop_id', 'delay_probability', 'delay_parameter', 'probability', 'transfers', 'path'])
    df['transfers'] = len(transfers)
    return df



def best_journeys(stations, departure_station_id, max_journeys=8):
    probability = 0.0
    journeys = []
    # sort departures in descending order of departure time
    departures = sorted(stations[departure_station_id][-1], key=lambda x: (x[2].start_time, x[1]), reverse=True)
    for i, (next_index, p, c) in enumerate(departures):
        if probability >= 0.999:
            break
        if p > probability:
            probability = p
            journey = []
            station_id = c.stop_id
            journey.append((p, c))
            while True:
                next_index, p, c = stations[station_id][-1][next_index]
                if c.stop_id is None:
                    break
                journey.append((p, c))
                station_id = c.stop_id
            journeys.append(to_df(journey))
    
    return concatenate(journeys[:max_journeys])