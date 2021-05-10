# -*- coding: utf-8 -*-
""" Template script """

import argparse
import importlib
from CBayesian import CBayesian
from CBasic import CBasic
from CHelstrom import CHelstrom
import logging
import csv

# -----------------------------------------------------------------------------
# Variables
# -----------------------------------------------------------------------------
EXPERIMENTS=['11111','01111','00111','00011','00001']

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------
def doAllExperiments(min_c, max_c, totC, p_csv, p_global):
    with open(p_csv, mode='w', newline='') as fCsv:
        csv_writer = csv.writer(fCsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        min_c=0.001
        max_c=0.999
        for ind in range(totC):
            c=min_c + ind*((max_c-min_c)/(args.totC-1))
            ps=doExperiments(args.className, args.tot, c, p_global)
            csv_writer.writerow([c, ps])

        logger.info("File %s created!" % (p_csv))

def doExperiments(p_class, p_tot, p_c, p_global):
    totOK=0
    totKO=0
    for experiment in EXPERIMENTS:
        logger.info("[c=%f] Experiment %s ..." % (p_c, experiment))
        expOK=0
        expKO=0
        for ind in range(p_tot):
            logger.debug("Execution %d of %d" % (ind, p_tot))
            # TODO : do it dynamically
            # The generic class (Interface) is
            # - <init>(Experiments, c)
            # - performMeasurement(particle) : class applies its strategy => TODO : change per getPVM()
            # - getHypothesis                : class get its guess
            o_measurement=None
            if p_class=="CBayesian":
                o_measurement=CBayesian(EXPERIMENTS, p_c)
            elif p_class=="CBasic":
                o_measurement=CBasic(EXPERIMENTS, p_c)
            elif p_class=="CHelstrom":
                o_measurement=CHelstrom(EXPERIMENTS, p_c)
            else:
                raise Exception("Unknown class %s." % (p_class))

            for particle in experiment:
                measurement=o_measurement.performMeasurement(particle)
                logger.debug("par(%s) : mea(%s)" % (particle, measurement))
                if not p_global and measurement==1:  break
            
            if o_measurement.getHypothesis()==experiment:
                expOK+=1
            else:
                expKO+=1
        # End all executions for that experiment
        logger.info("... ok = %d, ko = %d" % (expOK, expKO))
        totOK+=expOK    
        totKO+=expKO    

    # End all experiments
    logger.info("c=%f : Ps=%f (ok=%d, ko:%d)" % (p_c, 100.0 * totOK/(totOK+totKO), totOK, totKO))

    return totOK/(totOK+totKO)

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print ("RUN")
    print(logging)
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('MainLogger')

    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions

    # Required

    # Optional
    parser.add_argument('--className',  default='CBayesian', help='The class with the measurement strategy')
    parser.add_argument('--tot',        default=20, type=int, help='Number of times every experiment is executed')
    parser.add_argument('--c',          type=float, help='Overlap betwwen the states 0 and 1')
    parser.add_argument('--totC',       default=10, type=int, help='Number of values of c used')
    parser.add_argument('--glob',       default=0, type=int, help='0=local (stop at first 1), 1=global (do all measurements)')
    parser.add_argument('--csv',        default="results.csv", help='Number of values of c used')

    args = parser.parse_args()

    # Check parameters


    # Run
    print ("RUN")
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('MainLogger')

    if args.c:
        doExperiments(args.className, args.tot, args.c, True if args.glob==1 else False)
    else:
        doAllExperiments(0.001, 0.999, args.totC, args.csv, True if args.glob==1 else False)
