# -*- coding: utf-8 -*-
""" Template script """

import argparse
import importlib
from CBayesian import CBayesian
import logging

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
def doExperiments(p_class, p_tot, p_c):

    totOK=0
    totKO=0
    for experiment in EXPERIMENTS:
        for ind in range(p_tot):
            # TODO : do it dynamically
            # The generic class (Interface) is
            # - <init>(Experiments, c)
            # - performMeasurement(particle) : class applies its strategy => TODO : change per getPVM()
            # - getHypothesis                : class get its guess
            o_measurement=None
            if p_class=="CBayesian":
                o_measurement=CBayesian(EXPERIMENTS, p_c)
            else:
                raise Exception("Unknown class %s." % (p_class))

            for particle in experiment:
                measurement=o_measurement.performMeasurement(particle)
                logger.debug("exp (%s) : par(%s) : mea(%s)" % (experiment, particle, measurement))
                if measurement=='1': break
            
            if o_measurement.getHypothesis()==experiment:
                totOK+=1
            else:
                totKO+=1

    logger.info("c=%f : Ps=%f (ok=%d, ko:%d)" % (p_c, 100.0 * totOK/(totOK+totKO), totOK, totKO))

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions
    # parser.add_argument('--action', action="store_true", help='<Help>')

    # Required

    # Optional
    parser.add_argument('--className',  default='CBayesian', help='The class with the measurement strategy')
    parser.add_argument('--tot',        default=1, type=int, help='Number of times every experiment is executed')
    parser.add_argument('--c',          default=0.5, type=float, help='Overlap betwwen the states 0 and 1')
    parser.add_argument('--log',        default="./message.log", help='File with logs');

    args = parser.parse_args()

    # Check parameters


    # Run
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('MainLogger')

    for ind in range(3,20):
        doExperiments(args.className, args.tot, ind/20)
