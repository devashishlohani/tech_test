from collections import defaultdict
import os, json, sqlite3, copy, itertools

class Graph():
    def __init__(self):
        """
        self.edges is a dict of all possible next nodes (planets)
        e.g. {'X': ['A', 'B', 'C', 'E'], ...}
        self.weights has all the weights (distance) between two nodes,
        with the two nodes as a tuple as the key
        e.g. {('X', 'A'): 7, ('X', 'B'): 2, ...}
        """
        self.edges = defaultdict(list)
        self.weights = {}
        self.paths = []
        self.dists = []
        self.dist = []

    def add_edge(self, u, v, weight):
        # Note: assumes edges are bi-directional
        self.edges[u].append(v)
        self.edges[v].append(u)
        self.weights[(u, v)] = weight
        self.weights[(v, u)] = weight

    def getAllPathsUtil(self, u, d, visited, path, dist, paths, dists, autonomy_list):
        visited[u] = True
        path.append(u)
        if u == d:
            paths.append(path.copy())
            dists.append([0] + dist.copy())
        else:
            for i in self.edges[u]:
                if visited[i] == False:
                    distance = self.weights[(u, i)]
                    fuel_after_travel = autonomy_list[-1] - distance
                    if(fuel_after_travel > 0):
                        dist.append(distance)
                        autonomy_list.append(fuel_after_travel)
                    elif(fuel_after_travel == 0):
                        dist.append([distance,1])
                        autonomy_list.append(autonomy_list[0]) # Refueling
                    self.getAllPathsUtil(i, d, visited, path, dist, paths, dists, autonomy_list)
        path.pop()
        if (dist!=[]):
            dist.pop()
        autonomy_list.pop()
        visited[u] = False

    def getAllPaths(self, source, destination, autonomy, visited):
        """Get all paths(routes) & distances from source to destination, considers autonomy & refueling"""

        path = []
        dist = []
        paths = []
        dists = []
        autonomy_list = [autonomy]
        self.getAllPathsUtil(source, destination, visited, path, dist, paths, dists, autonomy_list)
        return paths, dists

def dist_to_day(route):
    tmp = 0
    day_info = []
    for r in route:
        if type(r) is list:
            tmp_l = []
            for l in r:
                tmp += l
                tmp_l.append(tmp)
            day_info.append(tmp_l)
        else:
            tmp += r
            day_info.append(tmp)
    return day_info

def calc_time_to_dest(dist_info):
    total = 0
    for i in dist_info:
        if type(i) is list:
            total += sum(i)
        else:
            total += i
    return total

def calc_capturing_odds(num_days):
    prob = 0
    for i in range(num_days):
        prob += pow(9, i) / pow(10, i+1)
    return prob

def calc_survival_odds(planets, arrival_info, bounty_hunters):
    bounty_attacks = 0
    for key, pair in bounty_hunters.items():
        if key in planets:
            attack_days = ensure_list_type(pair)
            arrival_days = ensure_list_type(arrival_info[planets.index(key)])
            bounty_attacks += len(set(attack_days) & set(arrival_days))
    #print(bounty_attacks)
    return 1 - calc_capturing_odds(bounty_attacks)

def ensure_list_type(a):
    return [a] if not isinstance(a, list) else a

def update_later_values(values, to_add):
    new_values = []
    for i in range(len(values)):
        if type(values[i]) is list:
            new_values.append([v + to_add for v in values[i]])
        else:
            new_values.append(values[i] + to_add)
    return new_values

def updating_arrival(day_propo, arrival_information):
    for i in range(len(day_propo)):
        if day_propo[i] != 0:
            #print(i, day_propo[i])
            tmp = arrival_information[i]
            if type(tmp) is not list:
                tmp = [tmp]
            tmp.append(tmp[-1 ]+ day_propo[i])
            arrival_information[i] = tmp
            arrival_information[i+1:] = update_later_values(arrival_information[i+1:], day_propo[i])
    return arrival_information

def rearrange_bounty_data(bounty_hunters):
    x = {}
    for attack in bounty_hunters:
        attacked_planet = attack['planet']
        attacked_day = attack['day']
        if attacked_planet not in x.keys():
            x[attacked_planet] = [attacked_day]
        else:
            x[attacked_planet].append(attacked_day)
    return x

def read_from_db(db):
    """Read routes database and get all data from the table"""

    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('SELECT * FROM routes')
    data = c.fetchall()
    c.close()
    conn.close()
    return data

def get_millenium_data(file):
    """Reads falcon json file and retrieves relevant data"""

    f = open(file)
    data = json.load(f)
    autonomy = data['autonomy']
    departure = data['departure']
    arrival = data['arrival']
    routes_db = os.path.dirname(file) + "/" + data['routes_db']
    f.close()
    return autonomy, departure, arrival, routes_db

def get_empire_data(file):
    f = open(file)
    data = json.load(f)
    countdown = data['countdown']
    bounty_hunters = rearrange_bounty_data(data['bounty_hunters'])
    f.close()
    return countdown, bounty_hunters


def get_best_possible_route(routes, distance_info_routes, countdown, bounty_hunters):
    """Given all possibles routes, distance info, countdown & bounty attacks info,
       calculates best possible route along with its success probability

    Parameters
    ----------
    routes : list
        list of all possible routes, where each element is a list of planets
    distance_info_routes : list
        distance among planets corresponding to routes variable
    countdown : int
        maximum number of days to reach the destination
    bounty_hunters: dict
        dictionary with to be attacked planets as keys and days of attack as values
    Returns
    -------
    float : representing odds to reach destination between 0 and 1
    str : best route with days information
    """

    best_success_probability = 0
    best_route_planets = []
    best_route_day_info = []
    for i in range(len(routes)):

        # calculate number of days to reach the destination following current route
        days_to_destination = calc_time_to_dest(distance_info_routes[i])
        extra_days = countdown - days_to_destination
        arrival_info = dist_to_day(distance_info_routes[i])  # convert distance information to arrival days
        if extra_days == 0:
            """Case when length of route is exactly same as countdown"""
            success_probability = calc_survival_odds(routes[i], arrival_info, bounty_hunters)
            if (success_probability > best_success_probability):
                best_success_probability = success_probability
                best_route_planets = routes[i]
                best_route_day_info = arrival_info
        elif extra_days > 0:
            """Case when length of route is shorter than countdown, so extra days should be spent wisely"""
            num_candidate_planets = len(arrival_info[:-1])  # extra days can be spent in all planets except destination

            # Find all possible combinations to spend extra days in different planets
            days_to_spend = list(range(extra_days + 1))
            days_spend_propositions = [p for p in itertools.product(days_to_spend, repeat=num_candidate_planets) if
                                       0 < sum(p) <= extra_days]

            for j in range(len(days_spend_propositions)):

                # Update arrrival information in each planet according to day spending proposition
                day_propo = days_spend_propositions[j]
                updated_arrival = updating_arrival(day_propo, copy.deepcopy(arrival_info))

                success_probability = calc_survival_odds(routes[i], updated_arrival, bounty_hunters)
                if (success_probability > best_success_probability):
                    best_success_probability = success_probability
                    best_route_planets = routes[i]
                    best_route_day_info = updated_arrival

    # Merging best route with planets and days spent information into a lisible string
    best_route_with_day_info = "-".join([best_route_planets[i] + "(" + str(best_route_day_info[i]) + ")"
                                         for i in range(len(best_route_planets))])

    return best_success_probability, best_route_with_day_info