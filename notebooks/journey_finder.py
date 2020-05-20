import numpy as np
import pandas as pd
import collections
import math


EMPTY_DF = pd.DataFrame([], columns=['start_id', 'start_time', 'line_id', 'transport_type', 'stop_time', 'stop_id', 'delay_probability', 'delay_parameter', 'probability', 'transfers', 'path'])

Connection = collections.namedtuple('Connection', 'start_id start_time line_id transport_type stop_time stop_id delay_probability delay_parameter')

class JourneyFinder:
    """Optimal journey finder which holds results of found journeys

    This class is only used to store values and give easy access to the 
    journey finder functions.
    """
    
    def __init__(self, connections, footpaths):
        self.connections = [Connection(*row) for row in connections.values]
        self.footpaths = footpaths
        self._unique_stations = np.unique([(c.start_id, c.stop_id) for c in self.connections])
        self._stations = None
        self._departure_station_id = None
    
    def find(self, departure_station_id, arrival_station_id, arrival_time, 
             min_probability=0.9, max_probability=0.999999, transfer_time=120):
        """Finds journeys from `departure_station_id` to `arrival_station_id`
        
        Use `self.best_journeys()` to get the best journeys.
        """
        self._departure_station_id = departure_station_id
        self._stations = find(self.connections, self.footpaths, self._unique_stations, 
                              departure_station_id, arrival_station_id, arrival_time, 
                             min_probability, max_probability, transfer_time)
        
    def best_journeys(self):
        """Returns best journeys"""
        return best_journeys(self._stations, self._departure_station_id)

# Description of the journey find algorithm            
# =========================================        
# The find function maintains one datastructure and a couple of constraints
# 
# Data Structure
# ==============
# The data structure is a dictionary with station_ids as keys and a tuple as values.
# The value tuple is structured as follows: 
#   (highest_probability, latest_departure_time, [connection tuples])
#   - highest_probability: 
#       The arrival probability of the best connection leaving from the station
#   - latest_departure_time: 
#       The departure time of the latest connection leaving the station that 
#       reaches the arrival station with very high probability (p >= max_probability)
#   - connection tuple: 
#       Holds information on a connection leaving the station. values: 
#           (index, arrival_probability, connection)
#           - index: 
#               Holds the index of the follow up connection in the 
#               connections list of the stop_station for the this connection
#           - arrival_probability: 
#               Probability to arrive on time at arrival station if this 
#               connection is taken
#           - connection: a connection object
#
# Constraints
# ===========
# min_probability: 
#   Minimum probability to arrive at arrival_station, 
#   journeys are discarded as soon as arrival probability drops below mini
# max_probability:
#   Journeys with probability >= max_probability are considered to always
#   arrive at arrival station on time. This value should be close to 1.0.
#   Once the algorithm finds a journey that leaves departure_station and
#   arrives with probability >= max_probability at arrival_station it 
#   will discard any connections that leave before the departure time
#   of that journey.
# departure_min_time:
#   Holds the departure time of the latest departing journey from 
#   departure_station that arrives at arrival_station with 
#   probability >= max_probability
#
# Algorithm
# =========
# The algorithm scans connections in decreasing arrival time.
# For each connection it checks whether the stop_station of the
# connection contains follow up connections that could be taken
# (note that the arrival_station contains a fake connection to
# mark the end of the journey).
# If there are connections in the stop station then the following happens:
#   For each connection leaving the stop_station the algorithm
#   calculates the probability of arriving on time if that connection
#   is taken after the current one.
#   The follow up connection yielding the highest arrival probability is 
#   selected as the optimal choice (this is provably the best choice
#   by the initial ordering of the connections).
#   Then the found arrival probability and the connections departure time 
#   are compared to the last entry in the start stations list of connection
#   tuples. If the new arrival probability and connections departure time
#   are not strictly worse than the last entries probability and departure
#   time the connection is added to the start stations list. Otherwise it
#   is discarded. The connection is also discarded if the constraints are
#   no longer satisfied.
#   
#   If the connection was added to the start station connections list, then
#   all incoming footpaths to the start station are explored. For each
#   footpath the algorithm checks if taking the footpath and subsequently
#   taking the connection gives a new potential departure connection for 
#   the footpaths start station. If this is the case then a new 
#   footpath connection is added to the footpaths start station.
#
# The algorithm terminates once it scanned through all connections or
# stops early if a journey is found with very high arrival probability
# and there are only connections left that arrive before the optimal
# journey departs.


def find(connections, footpaths, unique_stations, departure_station_id, arrival_station_id, arrival_time, 
             min_probability, max_probability, transfer_time):
    """Finds best journeys using the given connections and footpaths"""
    
    # create intial stations dictionary
    # probability of arrival is set to 0 and time of departure set to -1
    # the list of departing connections is empty
    stations = {station_id: (0.0, -1, []) for station_id in unique_stations}
    
    # add dummy connection to the arrival station
    stations[arrival_station_id] = (1.0, arrival_time, [(None, 1.0, Connection(arrival_station_id, arrival_time, '', None, None, None, None, None))])
    
    # departure_min_time is unconstrained until a journey
    # from departure_station to arrival_station is found
    departure_min_time = -1

    # find index of the first connection in the connections list
    # that arrives before/at the arrival_time (all later connections
    # are ignored)
    start_index = np.argmax(np.array([c.stop_time for c in connections]) <= arrival_time)

    # increases by 1 for every footpath connection that is added
    # is used to generate a unique trip_id for every footpath
    foot_counter = 0


    for c in connections[start_index:]:
        if c.stop_time < departure_min_time:
            # no more connections left that could improve optimal journey
            break

        stop_p, _, stop_connections = stations[c.stop_id]

        # check if there is a connection leaving the stop_station that can reach arrival_station in time
        if stop_p >= min_probability:
            start_p, start_min_time, start_connections = stations[c.start_id]

            # check if connection can improve the latest departure time of a 100% succeeding journey leaving start_station
            if c.start_time >= start_min_time:

                # calculate probabilities to catch connections at stop_station
                probabilities = [(0, 0.0)] * len(stop_connections)
                for i, (_, p, stop) in enumerate(stop_connections):
                    if stop.start_time >= c.stop_time:
                        if c.line_id == stop.line_id:
                            probabilities[i] = (i, p)
                        elif len(stop.line_id) == 0:
                            probabilities[i] = (i, p-p*c.delay_probability*math.exp(-c.delay_parameter * (stop.start_time - c.stop_time)))
                        elif stop.start_time >= c.stop_time + transfer_time:
                            probabilities[i] = (i, p-p*c.delay_probability*math.exp(-c.delay_parameter * (stop.start_time - c.stop_time - transfer_time)))
                
                if probabilities:
                    # select follow up connection with highest probability
                    index, p = max(probabilities, key=lambda x: x[1])

                    # stop if probability is too low
                    if p >= min_probability:
                        if start_connections:
                            # take last connection added to start_station
                            start = start_connections[-1]                        

                        # check if the current connection is not strictly worse than the last connection added to start_station
                        if not start_connections or not ((start[1] > p) and (start[2].start_time > c.start_time)):
                            start_connections.append((index, p, c))


                            # check if connection should be considered to arrive for sure
                            if p >= max_probability:
                                start_min_time = c.start_time
                                if c.start_id == departure_station_id:
                                    # set global constraint if a connection departing from departure_station
                                    # is found that arrives for sure
                                    departure_min_time = start_min_time

                            # update entry of start_station
                            max_p = max(p, start_p)
                            stations[c.start_id] = (max_p, start_min_time, start_connections)

                            # new footpath connections should point to the current connection
                            # that was just added to the connections list of start_station
                            index = len(start_connections) - 1

                            # explore footpaths
                            for previous_id, walk_time in footpaths.get(c.start_id, []):
                                previous_departure_time = c.start_time - walk_time - transfer_time
                                previous_p, previous_min_time, previous_connections = stations[previous_id]

                                # check if we can find a better connection leaving the start_station of the footpath
                                if previous_departure_time >= previous_min_time:
                                    if previous_connections:
                                        # take last connection added to start_station of footpath
                                        previous = previous_connections[-1]

                                    # check if taking footpath and then current connection is not strictly worse than
                                    # the last connection added to the start_station of the footpath
                                    if not previous_connections or not ((previous[1] > p) and (previous[2].start_time > previous_departure_time)):
                                        # add new connection to start_station of footpath
                                        previous_connections.append((index, p, Connection(previous_id, previous_departure_time, f'foot:{foot_counter}', 'foot', previous_departure_time + walk_time, c.start_id, 0, 0)))
                                        foot_counter += 1
                                        
                                        # check if footpath followed by connection should be considered to arrive for sure
                                        if p >= max_probability:
                                            previous_min_time = previous_departure_time
                                            if previous_id == departure_station_id:
                                                # update global constraint if footpaths leaves departure_station
                                                # and arrives for sure
                                                departure_min_time = max(departure_min_time, previous_departure_time)

                                        # update entry of footpaths start_station
                                        max_p = max(p, previous_p)
                                        stations[previous_id] = (max_p, previous_min_time, previous_connections)

    return stations


def concatenate(solutions):
    """Concatenates a list of unpivoted solutions dataframes"""
    i = 0
    for solution in solutions:
        solution['path'] += i
        i = solution['path'].max() + 1
    if solutions:
        return pd.concat(solutions)
    return None


def to_df(journey):
    """Converts a list of connections into a dataframe"""
    values = []
    transfers = set()
    for p, c in journey:
        transfers.add(c.line_id)
        values.append([*c, p, len(transfers), 0])
    df = pd.DataFrame(values, columns=['start_id', 'start_time', 'line_id', 'transport_type', 'stop_time', 'stop_id', 'delay_probability', 'delay_parameter', 'probability', 'transfers', 'path'])
    df['transfers'] = len(transfers)
    return df



def best_journeys(stations, departure_station_id, max_journeys=8, max_probability=0.999):
    """Selects best journeys by traversing the stations dictionary created by `find`

    The best journey is considered to be the journey that leaves as late as possible
    while still satisfying the `min_probability` constraint.

    The second best journey is a journey that leaves before the best journey and that
    improves the arrival probability of the best journey.

    Third, fourth, ... best journeys have to improve the previous journey.

    The scan is stopped once a journey is found that arrives with `max_probability` or
    the list is exhausted.
    """

    probability = 0.0
    journeys = []
    # sort departures in descending order of departure time
    departures = sorted(stations[departure_station_id][-1], key=lambda x: (x[2].start_time, x[1]), reverse=True)
    for i, (next_index, p, c) in enumerate(departures):
        if probability >= max_probability:
            break

        # check if journey has higher probability than previous best journey
        if p > probability:
            probability = p
            journey = []
            station_id = c.stop_id
            journey.append((p, c))

            # traverse the stations/connections by following the previous
            # connections station_id and the index
            while True:
                next_index, p, c = stations[station_id][-1][next_index]
                if c.stop_id is None:
                    break
                journey.append((p, c))
                station_id = c.stop_id
            journeys.append(to_df(journey))

    # return dataframe of all journeys
    if journeys:
        return concatenate(journeys[:max_journeys])
    else:
        return EMPTY_DF