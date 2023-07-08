import sys
from utils import get_millenium_data, get_empire_data, read_from_db,\
    Graph, get_best_possible_route

def get_the_odds(empire_file, falcon_file="static/files/millennium-falcon.json"):
    """Calculates the odds and path of reaching destination

    Parameters
    ----------
    empire_file : str
        Path of the empire.json file
    falcon_file : str, optional
        Path of the millennium-falcon.json file

    Returns
    -------
    float : representing odds to reach destination between 0 and 100
    str : best route with days information
    """

    # Read Json files and get relevant data
    autonomy, departure, arrival, routes_db = get_millenium_data(falcon_file)
    countdown, bounty_hunters = get_empire_data(empire_file)

    # Get rows from database as edges(origin, destination, travel time)
    edges = read_from_db(routes_db)

    # Make a graph with read edges
    graph = Graph()
    planet_list = []
    for edge in edges:
        graph.add_edge(*edge)
        for i in range(len(edge)-1):
            planet_list.append(edge[i])

    # Initialize all vertices of graph (planets) as not visited
    visited_planets = dict(zip(planet_list, [False] * len(planet_list)))

    ''' Get all possible routes & corresponding distance information 
        from source to destination planet, considers autonomy and refueling '''
    routes, distance_info_routes = graph.getAllPaths(departure, arrival, autonomy, visited_planets)

    best_success_probability, best_route_with_day_info = get_best_possible_route(routes, distance_info_routes, countdown, bounty_hunters)

    return best_success_probability * 100, best_route_with_day_info

if __name__ == '__main__':
    falcon_file = sys.argv[1]
    empire_file = sys.argv[2]
    best_odds, best_route_with_day_info = get_the_odds(empire_file, falcon_file)
    print(str(best_odds) + "%")
