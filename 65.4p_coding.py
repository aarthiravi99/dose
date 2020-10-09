'''
Example 24: This is a basic template for simulating the evolution of 
de novo origins of sequences.

In this simulation,
    - 1 population of 100 organisms
    - each organism will have 1 chromosome of only 27 possible genes 
    (A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, 
    W, X, Y, Z, 0) where A to M are the 13 beneficial genes, N to Z 
    are the 13 detrimental genes and 0 is the neutral gene.
    - each genome will be 20x repeat of "ABCDEFGHIJKLMABCD000000000NOPQRSTUVWXYZNOPQ000000000", totally 1040 gene space with 32.7% 
       beneficial genes, 32.7% detrimental genes (13 each of beneficial and detrimental genes, 17 copies each of beneficial and detrimental genes) and 34.6% empty gene space.
    - 1% background point mutation on chromosome
    - fitness is calculated as the number beneficial genes divided by 
    the number of detrimental genes
    - the lowest decile of the organisms (by fitness) will be removed 
    if there are more than 50% population remaining after removal; or 
    else, a random selection of 10 organisms will be removed.
    - a random selection of remaining organisms after removal will be 
    replicated to top up the population to 100 organisms
    - 2000 generations to be simulated
    - entire population will be deployed in one eco-cell (0, 0, 0)
    - no organism movement throughout the simulation

'''
# needed to run this example without prior
# installation of DOSE into Python site-packages
try: 
	import run_examples_without_installation
except ImportError: pass

import copy
import random

from difflib import SequenceMatcher

# Example codes starts from here
import dose

beneficial_gene = [gene for gene in "ABCDEFGHIJKLM"]

detrimental_gene = [gene for gene in "NOPQRSTUVWXYZ"]

initial_chromosome = \
    "ABCDEFGHIJKLMABCD000000000NOPQRSTUVWXYZNOPQ000000000" * 20
initial_chromosome = [gene for gene in initial_chromosome]

geneList = [gene for gene in "ABCDEFGHIJKLM0000000000000NOPQRSTUVWXYZ"]

number_of_organisms_to_eliminate = 10

parameters = {# Part 1: Simulation metadata
              "simulation_name": "50 percent codings",
              "population_names": ['pop_01'],

              # Part 2: World settings
              "world_x": 1,
              "world_y": 1,
              "world_z": 1,
              "population_locations": [[(0,0,0)]],
              "eco_cell_capacity": 1000,
              "deployment_code": 1,

              # Part 3: Population settings
              "population_size": 100,

              # Part 4: Genetics settings
              "genome_size": 1,
              "chromosome_size": 2000,
              "chromosome_bases": geneList,
              "initial_chromosome": initial_chromosome,

              # Part 5: Mutation settings
              "background_mutation": 0.01,
              "additional_mutation": 0,
              "mutation_type": 'point',
              
              # Part 6: Metabolic settings
              "interpreter": 'ragaraja',
              "instruction_size": 3,
              "ragaraja_version": 0,
              "base_converter": None,
              "ragaraja_instructions": [],
              "max_tape_length": 50,
              "interpret_chromosome": False,
              "clean_cell": False,
              "max_codon": 2000,

              # Part 7: Simulation settings
              "goal": 0,
              "maximum_generations": 2000,
              "eco_buried_frequency": 100,
              "fossilized_ratio": 0.01,
              "fossilized_frequency": 20,
              
              # Part 8: Simulation report settings
              "print_frequency": 10,
              "database_file": "simulation.db",
              "database_logging_frequency": 1
             }

class simulation_functions(dose.dose_functions):

    def organism_movement(self, Populations, pop_name, World): pass

    def organism_location(self, Populations, pop_name, World): pass

    def ecoregulate(self, World): pass

    def update_ecology(self, World, x, y, z): pass

    def update_local(self, World, x, y, z): pass

    def report(self, World): pass

    def fitness(self, Populations, pop_name):
        agents = Populations[pop_name].agents
        for index in range(len(agents)):
            organism = agents[index]
            beneficial_count = 0
            detrimental_count = 0
            chromosome = organism.genome[0].sequence
            for gene in chromosome:
                if gene in beneficial_gene: 
                    beneficial_count = beneficial_count + 1
                elif gene in detrimental_gene: 
                    detrimental_count = detrimental_count + 1
            fitness_score = beneficial_count / detrimental_count
            agents[index].status['fitness'] = [beneficial_count, 
                                               detrimental_count,
                                               fitness_score]

    def mutation_scheme(self, organism): 
        organism.genome[0].rmutate(parameters["mutation_type"],
                                   parameters["additional_mutation"])

    def prepopulation_control(self, Populations, pop_name): 
        agents = Populations[pop_name].agents
        # gen_count = agents[0].status["generation"]
        status = [(index, agents[index].status['fitness'])
                   for index in range(len(agents))]
        eliminate = [x[1][2] for x in status]
        eliminate.sort()
        ethreshold = eliminate[number_of_organisms_to_eliminate - 1]
        if len([x for x in eliminate if x > ethreshold]) > 50:
            Populations[pop_name].agents = \
                [agents[i] for i in range(len(agents))
                if agents[i].status['fitness'][2] > ethreshold]
        else:
            eliminate = [x[0] for x in status]
            eliminate = [random.choice(eliminate) for x in range(10)]
            Populations[pop_name].agents = \
                [agents[i] for i in range(len(agents))
                    if i not in eliminate]
        print("Population size after elimination: " + \
            str(len(Populations[pop_name].agents)))

    def mating(self, Populations, pop_name):
        agents = Populations[pop_name].agents
        while len(agents) < 100:
            chosen_agent = random.choice(agents)
            new_agent = copy.deepcopy(chosen_agent)
            agents.append(new_agent)

    def postpopulation_control(self, Populations, pop_name): pass

    def generation_events(self, Populations, pop_name): pass

    def population_report(self, Populations, pop_name):
        agents = Populations[pop_name].agents
        # sequences = [''.join(org.genome[0].sequence) for org in agents]
        identities = [org.status['identity'] for org in agents]
        fitness = [org.status['fitness'] for org in agents]
        gen_count = agents[0].status["generation"]
        for index in range(len(agents)):
            print('%s | %s | %s | %s | %s' % \
                (str(gen_count), str(identities[index]), 
                 fitness[index][0], fitness[index][1], fitness[index][2]))

    def database_report(self, con, cur, start_time, 
                        Populations, World, generation_count):
        try: dose.database_report_populations(con, cur, start_time, 
                                    Populations, generation_count)
        except: pass
        try: dose.database_report_world(con, cur, start_time, 
                                        World, generation_count)
        except: pass

    def deployment_scheme(self, Populations, pop_name, World): pass

dose.simulate(parameters, simulation_functions)
