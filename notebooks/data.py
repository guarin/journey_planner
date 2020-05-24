import pickle


def load_data():
    with open('../data/connections.pickle', 'rb') as file:
        connections = pickle.load(file)
        
    with open('../data/footpaths.pickle', 'rb') as file:
        footpaths = pickle.load(file)
        
    with open('../data/stations.pickle', 'rb') as file:
        stations = pickle.load(file)
        
    return connections, footpaths, stations