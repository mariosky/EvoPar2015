#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.




import random
import time
import ppeaks
import diversity

from deap import base
from deap import creator
from deap import tools

experiment = "%d-p%d" % (512,512)
experiment_id = experiment + "-%d" % round(time.time(),0)
datafile = open(experiment_id+".dat","a")


def evalPeaks(individual):
    return ppeaks.p_peaks(individual, pks),

pks = ppeaks.get_peaks(number=512,bits=256,seed=64)




creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Attribute generator
toolbox.register("attr_bool", random.randint, 0, 1)
# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_bool, 256)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


# Operator registering
toolbox.register("evaluate", evalPeaks)
toolbox.register("mate", tools.cxTwoPoints)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.02)
toolbox.register("select", tools.selTournament, tournsize=4)

def main(i):
    start = time.time()
    pop = toolbox.population(n=100)
    CXPB, MUTPB, NGEN = 0.85, 0.5, 2000

    print "Start of evolution"

    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop)


    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    evaluated = len(pop)

    print "Evaluated %i individuals" % evaluated

    diversity_by_gen = []

    # Begin the evolution
    for g in range(NGEN):
        print "-- Generation %i --" % g


        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = map(toolbox.clone, offspring)

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        diversity_by_gen.append([diversity.diversity_hamming(pop),diversity.entropy([ int(f[0]*100) for f in fitnesses])])


        print "  Evaluated %i individuals" % len(invalid_ind)
        evaluated+=len(invalid_ind)
        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        #length = len(pop)
        #mean = sum(fits) / length
        #sum2 = sum(x*x for x in fits)
        #std = abs(sum2 / length - mean**2)**0.5

        print "  Min %s" % min(fits)
        print "  Max %s" % max(fits)
        #print "  Avg %s" % mean
        #print "  Std %s" % std

        if max(fits) >= 1:
            datafile.write( "%d,%d,%d,%d" % (i,g, time.time()-start, evaluated))
            break

    import numpy as np
    import matplotlib.pyplot as plt

    div_  = np.array(diversity_by_gen)

    fig, (ax0, ax1) = plt.subplots(nrows=2)



    ax0.plot( range(len(diversity_by_gen)) ,div_[:,0] , 'b-', linewidth=2)
    ax1.plot( range(len(diversity_by_gen)) ,div_[:,1] , 'r-', linewidth=2)

    plt.show()


if __name__ == "__main__":
    for i in range(1):
        main(i)