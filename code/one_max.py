__author__ = 'mariosky'


EC2_INSTANCE = 'ec2-54-172-224-4.compute-1.amazonaws.com'
BROKER_URL = 'redis://%s:6379/0' % EC2_INSTANCE

from celery import Celery

app = Celery('one_max', broker=BROKER_URL, backend=BROKER_URL)
app.conf.CELERY_TASK_SERIALIZER = 'json'



import random
import time



from deap import base
from deap import creator
from deap import tools

import jsonrpclib


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

def evalOneMax(individual):
    return sum(individual),


def getToolBox(config):
    toolbox = base.Toolbox()
    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, config["CHROMOSOME_LENGTH"])
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evalOneMax)
    return toolbox

@app.task
def initialize(config):
    pop = getToolBox(config).population(n=config["POPULATION_SIZE"])
    server = jsonrpclib.Server(config["SERVER"])
    server.initialize(None)

    sample = [{"chromosome":ind[:], "id":None, "fitness":{"DefaultContext":0.0}} for ind in pop]
    init_pop = {'sample_id': 'None' , 'sample':   sample}

    server.putSample(init_pop)


def get_sample(config):
    for attempts in range(3):
        try:
            server = jsonrpclib.Server(config["SERVER"])
            sample = server.getSample(config["SAMPLE_SIZE"])
            return sample
        except jsonrpclib.ProtocolError as err:
            print "Error %s" % err




def put_sample(config,sample):
    for attempts in range(3):
        try:
            server = jsonrpclib.Server(config["SERVER"])
            server.putSample(sample)
            break
        except jsonrpclib.ProtocolError as err:
            print "Error %s" % err


def evolve(sample_num, config):
    #random.seed(64)

    toolbox = getToolBox(config)

    start= time.time()
    evospace_sample = get_sample(config)
    tGetSample= time.time()-start

    startEvol = time.time()
    pop = [ creator.Individual( cs['chromosome']) for cs in evospace_sample['sample']]

    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop)
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    sample_id = evospace_sample['sample_id']

    total_evals = len(pop)
    best_first   = None
    best_individual = None
    # Begin the evolution

    for g in range(config["WORKER_GENERATIONS"]):

        if best_individual:
            pop[0] = best_individual
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = map(toolbox.clone, offspring)

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < config["CXPB"]:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < config["MUTPB"]:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        total_evals+=len(invalid_ind)
        #print "  Evaluated %i individuals" % len(invalid_ind),

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        #length = len(pop)


        #mean = sum(fits) / length
        #sum2 = sum(x*x for x in fits)
        #std = abs(sum2 / length - mean**2)**0.5

        best = max(fits)
        if not best_first:
            best_first = best

        best_individual = tools.selBest(pop, 1)[0]
        if best ==  config["CHROMOSOME_LENGTH"]:
            #print best_individual
            break


            #print  "  Min %s" % min(fits) + "  Max %s" % max(fits)+ "  Avg %s" % mean + "  Std %s" % std

    #print "-- End of (successful) evolution --"

    sample = [ {"chromosome":ind[:],"id":None,
                "fitness":{"DefaultContext":ind.fitness.values[0]} }
               for ind in pop]
    evospace_sample['sample'] = sample
    tEvol = time.time()-startEvol


    startPutback =  time.time()
    if random.random() < config["RETURN_RATE"]:
        put_sample(config, evospace_sample)
        was_returned= "RETURNED"
    else:
         was_returned= "LOST"
    tPutBack = time.time() - startPutback

    return best ==  config["CHROMOSOME_LENGTH"], \
           [config["CHROMOSOME_LENGTH"],best, sample_num, round(time.time() - start, 2),
            round(tGetSample,2) , round( tEvol,2), round(tPutBack, 2), total_evals, best_first,was_returned,
             config["MUTPB"], config["CXPB"], config["SAMPLE_SIZE"],config["WORKER_GENERATIONS"],sample_id]

@app.task
def work(params):
    worker_id = params[0]
    config = params[1]
    results = []
    for sample_num in range(config["MAX_SAMPLES"]):
        server = jsonrpclib.Server(config["SERVER"]) #Create every time to prevent timeouts
        if int(server.found(None)):
            break
        else:
            gen_data = evolve(sample_num, config)
            if gen_data[0]:
                server.found_it(None)
                print "FOUND"
            results.append([worker_id] + gen_data[1])
            #print [worker_id] + gen_data[1]
    return results


if __name__ == '__main__':
    pass
