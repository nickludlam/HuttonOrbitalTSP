import sys
import time
import json
import random
import operator
from enum import Enum
from collections import OrderedDict

import pygame
import networkx as nx

from networkx.algorithms.tournament import hamiltonian_path
from networkx.algorithms import tournament
import matplotlib.pyplot as plt

from nose.tools import assert_equal
from nose.tools import assert_false
from nose.tools import assert_true

class StarSystem:
    def __init__(self, system_name, position_dict):
        self.name = system_name
        self.position = pygame.Vector3(position_dict['x'], position_dict['y'], position_dict['z'])
        self.distances = {}
    def add_distance(self, star_system, distance):
        self.distances[star_system] = distance
    def add_distances(self, distances_dictionary):
        self.distances = distances_dictionary
    def distance_to(self, target_system):
        return self.distances[target_system]
    def ordered_distances(self):
        #print(f"ordered_distances has {len(self.distances)} elements")
        sorted_pairs = sorted(self.distances.items(), key=operator.itemgetter(1))
        #print(sorted_pairs)
        return sorted_pairs

with open('stars.json') as f:
  data = json.load(f, object_pairs_hook=OrderedDict)

# We use a global because this is a hacky script that I made up as I went
all_systems = []


for idx, systemDetails in data.items():
    name = systemDetails['name']
    new_star_system = StarSystem(name, systemDetails)
    all_systems.append(new_star_system)

all_systems_len = len(all_systems)

for idx, system in enumerate(all_systems):
    print(f"{idx} : {system.name}")

# Test vector maths
#s0 = all_systems[0]
#s1 = all_systems[1]
#relative_position = s1.position - s0.position
# print(f"relative_position.magnitude={relative_position.magnitude()}")


# Generate our distance cache inside the all_systems data structure
for start_star_system in all_systems:
    #print(f"----- {start_star_system.name} -----")
    for end_star_system in all_systems:
        #print(f"Evaluating: {start_star_system.name} -> {end_star_system.name}")
        if end_star_system != start_star_system: # different systems
            distance = (end_star_system.position - start_star_system.position).magnitude()
            start_star_system.add_distance(end_star_system, distance)

print(f"Total systems imported: {len(all_systems)}")

    # next_system = None
    # best_distance = 1000000
    # for end_star_system in all_systems:
    #     if end_star_system != starter_system:
    #         # existing_edge = G[end_star_system][start_star_system]
    #         # print(existing_edge)
    #         print(f"checking {starter_system.name} for distance to {end_star_system.name}")
    #         inter_system_distance = starter_system.distance_to(end_star_system)
    #         if inter_system_distance < best_distance:
    #             next_system = end_star_system
    #             best_distance = inter_system_distance
    # print(f"Best distance from {starter_system} -> {next_system} is {best_distance}")
    # return next_system

# This first class encodes the concept of a route, which is an array of system indices
# stored in `visited_systems_indices` and a dictionary `visited_systems` which was used
# initially to boostrap the naive routes generated in `plot_basic_starting_route()`
class RouteFinder(object):
    def load_route_indices(self, route_indices):
        if (len(route_indices) != all_systems_len):
            print(f"Incorrect number of systems: {len(route_indices)} given but {all_systems_len} required")
            sys.exit(1)
        self.visited_systems_indices = route_indices.copy()
        
    def best_destination_from(self, starter_system):
        for (system, distance) in starter_system.ordered_distances():
            if system not in self.visited_systems:
                return system
            else:
                pass
                #print(f"Already visited {system.name}")
        return None

    # Dumb initial route generation approach. Start somewhere, and pick the closest nearby
    # systems you've not yet visited, and repeat
    def plot_basic_starting_route(self, starting_index=0):
        self.visited_systems_indices = []
        self.visited_systems = {}
        
        self.add_system(all_systems[starting_index])
        while len(self.visited_systems_indices) < all_systems_len:
            best_destination = self.best_destination_from(self.current_system)
            if best_destination == None:
                print(f"Next system for {self.current_system.name} is none")
                break
            else:
                self.add_system(best_destination)
        #print("Finished basic route plot!")
    
    def randomise_route(self):
        randomised_system_index_list = list(range(all_systems_len))
        random.shuffle(randomised_system_index_list)
        self.visited_systems_indices = randomised_system_index_list

    @property
    def current_system(self):
        return all_systems[self.visited_systems_indices[-1]]
        
    def add_system(self, star_system):
        self.visited_systems[star_system] = True
        star_system_index = all_systems.index(star_system)
        self.visited_systems_indices.append(star_system_index)
    
    def longest_hop(self):
        (longest_hop_distance, longest_hop_index) = self.longest_hop_with_index()
        return longest_hop_distance
    
    def longest_hop_index(self):
        (longest_hop_distance, longest_hop_index) = self.longest_hop_with_index()
        return longest_hop_index

    def longest_hop_with_index(self):
        longest_hop_index = -1
        longest_hop = 0

        my_current_system = all_systems[self.visited_systems_indices[0]]
        for index in self.visited_systems_indices[1:]:
            my_next_system = all_systems[index]
            distance = my_current_system.distance_to(my_next_system)
            if distance > longest_hop:
                longest_hop = distance
                longest_hop_index = index
        return (longest_hop, longest_hop_index)


    def distance_for_current_path(self):
        total_distance = 0
        my_current_system = all_systems[self.visited_systems_indices[0]]
        for index in self.visited_systems_indices[1:]:
            my_next_system = all_systems[index]
            total_distance += my_current_system.distance_to(my_next_system)
            #print(f" {system_count} {my_current_system.name} -> {my_next_system.name}")
            my_current_system = my_next_system
        #print(f"distance for {len(self.visited_systems_indices)} systems is {total_distance}")
        return total_distance
    
    def print_route(self):
        total_distance = 0
        longest_hop = 0

        my_current_system = all_systems[self.visited_systems_indices[0]]
        for index in self.visited_systems_indices[1:]:
            my_next_system = all_systems[index]
            distance = my_current_system.distance_to(my_next_system)
            print(f"{index:02d} {my_current_system.name} -> {my_next_system.name}  ({distance:.1f}ly)")
            total_distance += distance
            if distance > longest_hop:
                longest_hop = distance
            my_current_system = my_next_system

        print(f"\nTotal distance {total_distance:.1f} ly")
        print(f"Longest hop distance {longest_hop:.1f} ly")
        print(f"Compact route {self.visited_systems_indices}")
        route = ', '.join([all_systems[i].name for i in self.visited_systems_indices])
        print(f"Route names: " + route)

    def init_from_route_finder(self, other):
        self.visited_systems_indices = other.visited_systems_indices.copy()
        #self.visited_systems = other.visited_systems.copy()


# Simple RouteFinder usage tests
# route_finder = RouteFinder()
# route_finder.simple_plot_route()
# print("distance", route_finder.distance_for_current_path())



# Don't know why I can't have this inside RouteComparator
class RouteComparatorFunction(Enum):
    FITNESS_SELECTOR_SHORTEST_TOTAL = 0
    FITNESS_SELECTOR_SHORTEST_HOP = 1 # NOTE THAT THIS COMPARATOR IS BROKEN RIGHT NOW!

# A class to mutate and check two routes against each other. The backbone of our GA
class RouteComparator(object):
    def __init__(self, skip_duplicate_mutations=False, fitness_selector=RouteComparatorFunction.FITNESS_SELECTOR_SHORTEST_TOTAL):
        self.total_mutation_count = 0
        self.fitness_selector = fitness_selector
        
        if self.fitness_selector == RouteComparatorFunction.FITNESS_SELECTOR_SHORTEST_HOP:
            print("Shortest hop optimisation is currently unsupported. It needs a better way to target the source of the largest hop and ensure that each mutation tries to address it")
            sys.exit(1)
        
        self.skip_duplicate_mutations = skip_duplicate_mutations
        self.existing_mutations_set = set()
        self.successful_mutations = 0

    def basic_init(self, completely_randomise_starting_route=False):
        current_best_route = RouteFinder()
        if completely_randomise_starting_route:
            current_best_route.randomise_route()
            self.assign_best_route(current_best_route)
        else:
            current_best_route.plot_basic_starting_route()

        current_best_route_distance = current_best_route.distance_for_current_path()

        starting_index = 1
        
        if not completely_randomise_starting_route:
            while starting_index < all_systems_len:
                alternative_route = RouteFinder()
                alternative_route.plot_basic_starting_route(starting_index)
                alternative_route_distance = alternative_route.distance_for_current_path()
                #print(f"comparing {alternative_route_distance} with {current_best_route_distance}")
                if alternative_route_distance < current_best_route_distance:
                    current_best_route = alternative_route
                    current_best_route_distance = alternative_route_distance
                    print(f"New starter system gave a best route distance of {alternative_route_distance} for {current_best_route.visited_systems_indices}")
                starting_index += 1
        
            self.assign_best_route(current_best_route)
    
    def load_route_indices(self, route_indices):
        route = RouteFinder()
        route.load_route_indices(route_indices)
        self.assign_best_route(route)
    
    def assign_best_route(self, best_route):
        self.best_route = best_route
        if self.fitness_selector == RouteComparatorFunction.FITNESS_SELECTOR_SHORTEST_TOTAL:
            self.best_route_fitness_value = best_route.distance_for_current_path()
        elif self.fitness_selector == RouteComparatorFunction.FITNESS_SELECTOR_SHORTEST_HOP:
            self.best_route_fitness_value = best_route.longest_hop()
        self.existing_mutations_set = set()

    def do_mutations(self, desired_count, max_mutation_count=1, allowed_mutation_distance=1):
        print(f"Doing {desired_count} mutations")
        mutation_count = 0
        self.successful_mutations = 0
        
        prior_mutation_cache_hits = 0
        last_printout_time = time.time()

        iterations_per_output = 500000

        while mutation_count < desired_count:
            #print(f"On mutation {mutation_count} and {self.successful_mutations} have been successful")
            
            #random_mutation_count = random.randint(1, 3)
            
            if self.mutate_route_random(max_mutation_count, allowed_mutation_distance):
                mutation_count += 1
                self.total_mutation_count += 1
                if self.total_mutation_count % iterations_per_output == 0:
                    current_printout_time = time.time()
                    rate = iterations_per_output / (current_printout_time - last_printout_time)
                    percent_complete = (self.total_mutation_count / desired_count) * 100.0
                    print(f"On mutation {self.total_mutation_count} ({percent_complete:.1f}%) at {rate:.0f} tests/s. {prior_mutation_cache_hits} prior mutations skipped, {self.successful_mutations} successful. Best dist {self.best_route.distance_for_current_path()}")
                    last_printout_time = current_printout_time
            else:
                prior_mutation_cache_hits += 1
                
        print(f"Finished doing {mutation_count} mutations and {self.successful_mutations} were successful")
        
        #print("\n\nNew best route:")
        #self.best_route.print_route()
        #print(f"Distance: {self.best_route.distance_for_current_path()}")

    def fitness_score_for_route(self, route):
        if self.fitness_selector == RouteComparatorFunction.FITNESS_SELECTOR_SHORTEST_TOTAL:
            return route.distance_for_current_path()
        elif self.fitness_selector == RouteComparatorFunction.FITNESS_SELECTOR_SHORTEST_HOP:
            return route.longest_hop()
            
    def new_route_is_fitter(self, new_route):
        if self.fitness_selector == RouteComparatorFunction.FITNESS_SELECTOR_SHORTEST_TOTAL:
            return self.new_route_is_fitter_by_total_distance(new_route)
        elif self.fitness_selector == RouteComparatorFunction.FITNESS_SELECTOR_SHORTEST_HOP:
            return self.new_route_is_fitter_by_longest_hop_distance(new_route)

    def new_route_is_fitter_by_longest_hop_distance(self, new_route):
        existing_route_longest_hop = self.best_route_fitness_value
        new_route_longest_hop = new_route.longest_hop()
        #print(f"Existing longest hop {existing_route_longest_hop:.1f} vs new longest hop {new_route_longest_hop:.1f}")
        return new_route_longest_hop < existing_route_longest_hop
        
    def new_route_is_fitter_by_total_distance(self, new_route):
        existing_route_distance = self.best_route_fitness_value
        new_route_distance = new_route.distance_for_current_path()
        # print(f"Existing route distance {existing_route_distance:.1f} vs new route distance {new_route_distance:.1f}")
        return new_route_distance < existing_route_distance
    
    def mutate_route_random(self, upper_mutation_count=1, upper_mutation_distance=1):
        mutated_route = RouteFinder()
        mutated_route.init_from_route_finder(self.best_route)

        mutated_route_distance = mutated_route.distance_for_current_path()
        
        required_mutation_count = random.randint(1, upper_mutation_count)
        mutation_count = 0
        
        mutation_string = ""
        
        while mutation_count < required_mutation_count:
            random_index_source = random.randint(0, all_systems_len - 1)
            
            swap_direction = random.choice([1, -1])
            if random_index_source == 0:
                swap_direction = 1
            elif random_index_source == all_systems_len - 1:
                swap_direction = -1

            max_possible_swap_distance = 1
            if swap_direction == -1:
                max_possible_swap_distance = random_index_source
            else:
                max_possible_swap_distance = all_systems_len - 1 - random_index_source
            
            swap_distance = random.randint(1, min(upper_mutation_distance, max_possible_swap_distance))

            random_index_dest = random_index_source + (swap_direction * swap_distance)
                        
            mutated_route.visited_systems_indices[random_index_source], mutated_route.visited_systems_indices[random_index_dest] = mutated_route.visited_systems_indices[random_index_dest], mutated_route.visited_systems_indices[random_index_source]
    
            mutation_string += f"{random_index_source}-{random_index_dest}:"
            # print(f"  Mutating iteration {self.total_mutation_count} by swapping index {random_index_source} and {random_index_dest} (max {upper_mutation_distance})")
            mutation_count += 1

        # print(f"Dist: {self.fitness_score_for_route(mutated_route)} / Mutations: {mutation_string}")
        if self.skip_duplicate_mutations and mutation_string in self.existing_mutations_set:
            # print(f"Skipping {mutation_string} as we've tried it already")
            return False
        else:
            if self.new_route_is_fitter(mutated_route):
                mutated_route.print_route()
                self.assign_best_route(mutated_route)
                self.successful_mutations += 1
            # print(f"Inserting mutation_string {mutation_string}")
            if self.skip_duplicate_mutations:
                self.existing_mutations_set.add(mutation_string)
            return True

    def mutate_route(self, required_mutation_count=1, allowed_mutation_distance=1):
        mutated_route = RouteFinder()
        mutated_route.init_from_route_finder(self.best_route)
        
        mutated_route_distance = mutated_route.distance_for_current_path()
        #print(f"Before mutation, dist = {mutated_route_distance}")
        #print(f"Before mutation, route = {mutated_route.visited_systems_indices}")
        
        mutation_count = 0
        while mutation_count < required_mutation_count:
            # randint has both args inclusive in the output
            random_index_source = random.randint(0, all_systems_len - 1)
            
            # Focus on the longest hop if we're selecting for that
            if self.fitness_selector == RouteComparatorFunction.FITNESS_SELECTOR_SHORTEST_HOP:
                random_index_source = mutated_route.longest_hop_index()

            # do we swap up or down the list?
            swap_direction = random.choice([1, -1])
            swap_distance = 1
            if (allowed_mutation_distance > 1):
                swap_distance = random.randint(1, allowed_mutation_distance)

            random_index_dest = random_index_source + (swap_direction * swap_distance)

            # clamp so we don't try to swap outside the range
            random_index_dest = max(0, min(random_index_dest, all_systems_len-1))
            
            if (random_index_dest == random_index_source):
                continue
            
            print(f"Testing mutation {self.total_mutation_count} by swapping index {random_index_source} and {random_index_dest}")
            
            # Classic swap
            mutated_route.visited_systems_indices[random_index_source], mutated_route.visited_systems_indices[random_index_dest] = mutated_route.visited_systems_indices[random_index_dest], mutated_route.visited_systems_indices[random_index_source]
            mutation_count += 1
        
        if self.new_route_is_fitter(mutated_route):
            self.assign_best_route(mutated_route)
            return True
        else:
            #print(f"Mutated distance {mutated_route_distance} not better than best {self.best_route_distance}")
            return False


if __name__ == "__main__":

    start_time = time.time()

    seed = int(sys.argv[1]) if len(sys.argv) >= 2 else 1
    iteration_count = int(sys.argv[2]) if len(sys.argv) >= 3 else 100000

    random.seed(seed) # Required for repeatability

    route_comparator = RouteComparator(skip_duplicate_mutations=False)

    # Use this if you're not loading an existing route like we are below
    completely_randomise_starting_route = True
    route_comparator.basic_init(completely_randomise_starting_route)

    # Start from the beginning
    #dumb_route = range(len(all_systems))
    #route_comparator.load_route_indices([*dumb_route])
    
    # Current route
    #route_comparator.load_route_indices([12, 4, 15, 28, 5, 25, 26, 29, 22, 21, 20, 30, 31, 17, 27, 0, 13, 7, 11, 1, 18, 10, 3, 32, 24, 6, 23, 2, 9, 8, 14, 16, 19])
    
    # Load in the previous best route I found from a previous iteration
    #route_comparator.load_route_indices([7,14,15,8,16,18,25,6,10,1,21,24,17,22,13,19,12,20,2,4,0,5,9,23,11,3])
    route_comparator.best_route.print_route()

    print("Starting mutations")

    #route_comparator.do_mutations(1000000)
    #route_comparator.do_mutations(100000, 1, 2)
    #route_comparator.do_mutations(100000, 2, 2)

    # I'm just playing with these numbers currently
    route_comparator.do_mutations(iteration_count, 1, 40)

    print("\n-------------\nFinal route:\n")
    
    route_comparator.best_route.print_route()
    
    elapsed_time = time.time() - start_time
    print(f"Duration: {elapsed_time}")
    
    sys.exit(0)
    
#############################################################
# unused graph work - not worth it in the end

# # https://gist.github.com/mikkelam/ab7966e7ab1c441f947b
# def some_random_hamilton(G):
#     F = [(G,[list(G.nodes())[0]])]
#     n = G.number_of_nodes()
#     while F:
#         graph,path = F.pop()
#         confs = []
#         neighbors = (node for node in graph.neighbors(path[-1]) 
#                      if node != path[-1]) #exclude self loops
#         for neighbor in neighbors:
#             conf_p = path[:]
#             conf_p.append(neighbor)
#             conf_g = nx.Graph(graph)
#             conf_g.remove_node(path[-1])
#             confs.append((conf_g,conf_p))
#         for g,p in confs:
#             if len(p)==n:
#                 return p
#             else:
#                 F.append((g,p))
#     return None


# G = nx.DiGraph()
# G.add_nodes_from(all_systems)
# flip_weights = False


# for start_star_system in all_systems:
#     for end_star_system in all_systems:
#         if end_star_system != start_star_system: # different systems
#             distance = (end_star_system.position - start_star_system.position).magnitude()
#             try:
#                 exising_edge = G[end_star_system][start_star_system]
#                 # Do nothing if we have the link
#                 #print("... Skipped (existing)")
#             except KeyError:
#                 #wt_i = - distance if flip_weights else distance
#                 G.add_edge(start_star_system, end_star_system, attr_dict={'distance': distance})
#                 #print(f"... Added!")
#         else:
#                 pass
#                 #print(f"... Skipped (same systems)")

# all_names_map = {s:s.name for s in all_systems}

# nx.relabel_nodes(G, all_names_map, copy=False)
# nx.draw(G, None, with_labels=True, arrows=True, node_size=700)
# plt.savefig("path_graph1.png")
# plt.show()

# sys.exit(0)

# # We should have (total-1) connections for each node
# print("------")
# print('Number of nodes: {}'.format(len(G.nodes())))
# print('Number of edges: {}'.format(len(G.edges())))
# print()
# for node in G.nodes():
#     print(node.name, G.degree(node))
# print("------")

# total_distance = 0

# assert_true(tournament.is_tournament(G))

# path = hamiltonian_path(G)

# assert_equal(len(path), 26)
# assert_true(all(v in G[u] for u, v in zip(path, path[1:])))

# current_system = path[0]
# for next_system in path[1:]:
#     distance = (next_system.position - current_system.position).magnitude()
#     print(current_system.name, " -> ", next_system.name, " @ ", distance, "ly")
#     current_system = next_system
#     total_distance += distance
    
# print("Total distance", total_distance)