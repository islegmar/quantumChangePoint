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
def _bayesian(p_c, p_global, p_csv=None, p_outcome=None):
    from CBayesian import CBayesian

    logger=logging.getLogger("MainLogger")

    pS=0
    totParticles=len(EXPERIMENTS[0])
    totResults=2**totParticles

    # Loop over all the possible outcomes
    outcomes={}
    for output_int in range(0,totResults):
        # eg. output_int = 4 => output_str = 00100
        output_str=format(output_int, '0%db' % (totParticles))
        if p_outcome and p_outcome!=output_str: continue
        logger.info("OUTPUT : %s" % (output_str))

        outcomes[output_str]={
            'prob' : 1.0,
            'likelihood' : None,
            'steps' : []
        }

        o_measurement=CBayesian(EXPERIMENTS, p_c)
        my_real_outcome=""   # my_real_outcome are the REAL measurament that has taken place
        for step,particle in enumerate(output_str):
            my_real_outcome="%s%s" % (my_real_outcome, particle)
            measurement=o_measurement.performMeasurement(particle, True)
            outcomes[output_str]['steps'].append({
                'outcome'    : my_real_outcome,
                'prob'       : o_measurement.getProbOutcomes(my_real_outcome),
                'likelihood' : o_measurement.getMaxLikelihood()
            })
            if not p_global and measurement==1:  break

        outcomes[output_str]['prob']       = o_measurement.getProbOutcomes(my_real_outcome)
        outcomes[output_str]['likelihood'] = o_measurement.getMaxLikelihood()

        # Ok, now for this outcome let's compute the Ps
        logger.info("Prob(%s[%s as real_outcome]) : %f, MaxLikelihood : %f" % (output_str,  my_real_outcome, outcomes[output_str]['prob'], outcomes[output_str]['likelihood']))

    # Normalize the probabilities for every outcome
    ptot=0.0
    for output_str, item in outcomes.items():
        ptot+=item['prob']

    logger.info("c=%e, ptot=%e" % (p_c, ptot))
    # Loop over all the outcomes to compute the probability of success that is
    # the probability of its max. likelihood * probability of this outcome
    pS=0.0
    for output_str, item in outcomes.items():
        logger.debug("[%s] Prob : %f (=%f/%f), Likelihood : %f" % (output_str, (item['prob']/ptot),item['prob'],ptot,item['likelihood']))
        pS+=(item['prob']/ptot)*item['likelihood']
        #pS+=item['prob']*item['likelihood']
        #pS+=item['likelihood']/totResults
        #pS+=item['likelihood']
        
    logger.info("RESULT : PS(c=%f) : %f" % (p_c, pS))
    if p_c== 0.5262631578947369:
        logger.info("RESULT EXPERIMENTAL : PS(c=%f) : %f" % (p_c, 0.8452))
    
    if p_csv:
        with open(p_csv, mode='w', newline='') as fCsv:
            csv_writer = csv.writer(fCsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            header=['Outome', 'Prob Outcome (no normalized)', 'Prob outcome (normalized)', 'Max Likelihood', 'Probability of Success']
            for ind in range(5):
                header.extend([
                        'Step %d : outcome' % (ind), 
                        'Step %d : probability' % (ind), 
                        'Step %d : max likelihood' % (ind)
                ])
            csv_writer.writerow(header)

            PS               = 0.0
            P_Outcome_NoNorm = 0.0
            P_Outcome_Norm   = 0.0
            for output_int in range(0,totResults):
                output_str=format(output_int, '0%db' % (totParticles))
                row=[]
                row.append(output_str)

                item=outcomes[output_str]
                row.append(item['prob'])
                row.append(item['prob']/ptot)
                row.append(item['likelihood'])
                row.append((item['prob']/ptot)*item['likelihood'])

                for ind in range(5):
                    if ind<len(item['steps']):
                        row.extend([
                            item['steps'][ind]['outcome'],
                            item['steps'][ind]['prob'],
                            item['steps'][ind]['likelihood']
                        ])
                    else:
                        row.extend([
                                '',
                                '',
                                ''
                        ])
                csv_writer.writerow(row)

                # Acum for totals
                P_Outcome_NoNorm += item['prob']
                P_Outcome_Norm   += item['prob']/ptot
                PS               += (item['prob']/ptot)*item['likelihood']


            # TOTALS
            csv_writer.writerow([
                'TOTAL',
                P_Outcome_NoNorm,
                P_Outcome_Norm,
                '',
                PS
            ])


            print("File %s created!" % (p_csv))

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
            if ps:
                csv_writer.writerow([c, ps])

        print("File %s created!" % (p_csv))

def doComputation(p_class, p_c, p_global,p_file_csv, p_outcome=None):
    if p_class=="CBayesianTheory":
        return _bayesian(p_c, p_global, p_file_csv, p_outcome)
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
    parser.add_argument('--outcome',    help='If specified compute for only one outome (degugging)')
    parser.add_argument('--c',          type=float, help='Overlap betwwen the states 0 and 1')
    parser.add_argument('--totC',       default=10, type=int, help='Number of values of c used')
    parser.add_argument('--glob',       default=0, type=int, help='0=local (stop at first 1), 1=global (do all measurements)')
    parser.add_argument('--csv',        default="results.csv", help='Number of values of c used')

    args = parser.parse_args()

    # Check parameters

    # Run
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('MainLogger')

    if args.c:
        doComputation(args.className, args.c, True if args.glob==1 else False, args.csv, args.outcome)
    else:
        doAllComputation(0.001, 0.999, args.totC, args.className, args.csv, True if args.glob==1 else False)
