# -*- coding: utf-8 -*-

import argparse
import importlib
import logging
import math
import csv
from CSquareRoot import CSquareRoot

# - Help Multiline
# - Show default values
class MyArgumentFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
     pass

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
EXPERIMENTS=['11111','01111','00111','00011','00001']

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def _bayesian(p_c, p_global):
    from CBayesian import CBayesian

    pS=0
    totParticles=len(EXPERIMENTS[0])

    # Loop over all the experiments and for each of them compute its 
    # Probability of success taken into accout all the possible outcomes when
    # measuring
    for experiment in EXPERIMENTS:
        print ("[%f] experiment : %s" % (p_c,experiment))
        totResults=2**totParticles

        # Loop over all the possible outcomes and for each of them see which is
        # the probability of 'experiment'
        outputs={}
        for output_int in range(1,totResults):
            # eg. output_int = 4 => output_str = 00100
            output_str=format(output_int, '0%db' % (totParticles))
            outputs[output_str] = { 'probOK' : None, 'probOutput':1.0 }

            #print ("  outcome : %s" % (output_str))

            o_measurement=CBayesian(EXPERIMENTS, p_c)
            # Loop over all the possible individual outcomes and perform a 
            # Bayesian 
            for step,particle in enumerate(output_str):
                measurement=o_measurement.performMeasurement(particle, True)
                outputs[output_str]['probOutput']*=o_measurement.getProb(particle, experiment[step])
                if not p_global and measurement==1:  break
            outputs[output_str]['probOK']=o_measurement.getPS(experiment)
            # for my_exp in EXPERIMENTS:
            #     tot+=o_measurement.getPS(my_exp)
            #     print("    P(%s|%s) : %f" % (my_exp, output_str, o_measurement.getPS(my_exp)))
            # print("    ---- tot : %f, prob (%s) : %f" % (tot, output_str, prob_output))
            # print(prob_output)

        # Experiment done
        # Now let's compute taking into acount the normalizations
        pMyExperiment=0.0
        tot=0.0
        for output_str, item in outputs.items():
            tot+=item['probOutput']
        for output_str, item in outputs.items():
            pMyExperiment+=(item['probOutput']/tot)*item['probOK']

        for output_str, item in outputs.items():
            print ("[%s] Prob combination : %e, Prob OK : %e => %e" % 
                    (output_str, item['probOutput'], item['probOK'], (item['probOutput']/tot)*item['probOK']))

        print("P(%s) : %e" % (experiment, pMyExperiment))
        pS+=pMyExperiment/len(EXPERIMENTS)
        
    print (">>>>> c:%f, pS:%f" % (p_c, pS))

    return pS

def _sqrt(p_c,p_n):
    obj=CSquareRoot(p_c)
    lowerBoundP, upperBoundP = obj.computeProbBounds(p_n)

    #return upperBoundP
    return lowerBoundP


# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------
def doAllComputation(min_c, max_c, totC, p_className, p_csv, p_global):
    with open(p_csv, mode='w', newline='') as fCsv:
        csv_writer = csv.writer(fCsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        min_c=0.001
        max_c=0.999
        for ind in range(totC):
            c=min_c + ind*((max_c-min_c)/(args.totC-1))
            ps=doComputation(p_className, c, p_global)
            csv_writer.writerow([c, ps])

        print("File %s created!" % (p_csv))

def doComputation(p_class, p_c, p_global):
    if p_class=="CBayesianTheory":
        return _bayesian(p_c, p_global)
    elif p_class=="CSquareRoot":
        return _sqrt(p_c,5)
    else:
        raise Exception("Unknown class %s!" % (p_class))

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="In this we compute the theoretical values of some hypotesis that can not be computed analytical with a formula")
    parser = argparse.ArgumentParser(formatter_class=MyArgumentFormatter,
        description="""
Compute the theoretical values for some strategies.

This is used when it does not exist an analytical formula and the main difference
with the class 'experiments.py' is of course that here no experimewnt is done.

TODO : it has some similar code to experiments.py but put there some of the 
logic that is performed here was "forced" and make it unclear so the best was
to split even some code is repeated. Maybe some abstraction can be done with
the duplicacted code between experiments.py and theory.py.""")

    # Actions

    # Required

    # Optional
    parser.add_argument('--className',  default='CBayesianTheory', help='The class with the measurement strategy')
    parser.add_argument('--c',          type=float, help='Overlap betwwen the states 0 and 1')
    parser.add_argument('--totC',       default=10, type=int, help='Number of values of c used')
    parser.add_argument('--glob',       default=0, type=int, help='0=local (stop at first 1), 1=global (do all measurements)')
    parser.add_argument('--csv',        default="results.csv", help='Number of values of c used')

    args = parser.parse_args()

    # Check parameters

    # Run
    #logging.config.fileConfig('logging.conf')
    #logger = logging.getLogger('MainLogger')

    if args.c:
        doComputation(args.className, args.c, True if args.glob==1 else False)
    else:
        doAllComputation(0.001, 0.999, args.totC, args.className, args.csv, True if args.glob==1 else False)
