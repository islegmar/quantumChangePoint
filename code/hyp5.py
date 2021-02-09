# -*- coding: utf-8 -*-
""" Template script """

import argparse
import random

# We have:
# - 2 hypothesys
# - 2 outputs
# - A probability distribution P(Out|Hyp)

# The estimator function returns the state given a result
# extimatro[<result>] = <state>
estimator = [0, 1]

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def _trace(line):
    """ Trace function. """
    print (line)

def _equal(array1, array2):
    """ Check the equality for two arrays. """

    if len(array1)!=len(array2):
        return False

    equal=True
    for ind, val1 in enumerate(array1):
        if val!=array2[ind]:
            equal=False
            break

    return equal

def _getProbDistribution(c):
    """ [<state>][<out>] = given '<state>' probability of getting '<out>' """

    return [[1   , 0],
            [c**2, 1-c**2]]

def _getResultForState(state, prob):
    """ Given a certain state and a probability distribution, ger a possible output """
    value=random.uniform(0,1)

    # print ("value : %f, state : %d" % (value, state))
    # print (prob[state])

    output=None
    for ind,prob in enumerate(prob[state]):
        value-=prob
        if value<=0:
            output=ind
            break

    #print ("outout : %d" % (output))
    return output

def _buildExperiment(distribution):
    """ Build an experiment given a certain distribution.

    distribution is an array where the value [n] is the number of times the
    state 'n' appears. For example [1,4] will generate [0,1,1,1,1]."""

    experiment=[]
    for ind, val in enumerate(distribution):
        experiment+=[ind]*val

    return experiment

def _getResultsForExperiment(experiment, prob):
    """ Given an experiment, the the possible results. """
    results=[None] * len(experiment)

    for ind, state in enumerate(experiment):
        results[ind] = _getResultForState(state, prob)

    return results

def _getHypothesysForResults(results, estimator):
    """ Given a list of results, build an hypothesis using the estimator. """
    hypothesis=[None] * len(results)

    for ind, result in enumerate(results):
        hypothesis[ind] = estimator[result]

    return hypothesis
     
# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------

# Generates a random string 
def computeSuccess(num_states_per_experiment, num_iterations_per_experiment, prob):

    tot=0
    totOk=0
    # If num_states_per_experiment = 5 we generates experiment of the form:
    # - 0 0 0 0 0
    # - 0 0 0 0 1
    # - 0 0 0 1 1
    # - 0 0 1 1 1
    # - 0 1 1 1 1
    # And every experiment is generated 'num_iterations_per_experiment' times
    # n is the number of states '
    for n in range(num_states_per_experiment):
        experiment=_buildExperiment([num_states_per_experiment-n,n])
        print (experiment)
        myOk=0
        myTot=0
        for k in range(num_iterations_per_experiment):
            results=_getResultsForExperiment(experiment, prob)
            hypothesis=_getHypothesysForResults(results, estimator)
            tot += 1
            myTot += 1
            if _equal(experiment, hypothesis):
                totOk += 1
                myOk += 1
        print ("Success : %f %%" % ( (myOk * 100.0) / myTot))

    return (totOk * 100.0) / tot



# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions
    # parser.add_argument('--action', action="store_true", help='<Help>')

    # Required

    # Optional
    parser.add_argument('-c',  default=0, type=float, help='Arg c')
    parser.add_argument('-n',  default=5, type=int, help='Number states per expermient')
    parser.add_argument('-i',  default=100, type=int, help='Number iterations per expermient')

    args = parser.parse_args()

    # Check parameters


    # Run
    print (computeSuccess(args.n, args.i, _getProbDistribution(args.c)))
    d=(1-args.c**2)
    p=100.0 * ((1-d**args.n)/(1-d))/args.n
    print ("Theoretical value : %f " % p)
