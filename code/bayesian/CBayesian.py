import helstrom
from CPVM import CPVM
import math
import numpy as np
import logging
import argparse
import json

class CBayesian:
    def __init__(self, experiments, c):
        self.logger=logging.getLogger("MainLogger")

        # Indicates in which step we are, it has influence when we compute
        # our PVM
        self.step=0
        self.experiments=[]
        for experiment in experiments:
            # All the experiments have same prior (in the beginning)
            self.experiments.append({
                'states' : experiment,
                'prob' : [1/len(experiments)]
            })
        # The CPVM at the current step
        self.oPVM=None

        # Info about the outcomes (eg. the probabilities at every step)
        self.outcomes={
            '0' : { 'probs' : [] },
            '1' : { 'probs' : [] }
        }

        # c represents the angle between the states : <0|1> and it is an angle
        # betwen [0,pi/2] BUT in our case, because we are going to use Helstrom,
        # the angle is the half
        self.theta=math.acos(c)/2
        self.state_0=[math.cos(self.theta),  math.sin(self.theta)]
        self.state_1=[math.cos(self.theta), -math.sin(self.theta)]

        self.logger.debug("c=%e, theta=%e" % (c, self.theta))

    def performMeasurement(self, particle, computeTheoretical=False):
        """ Perform the measurement of a particle and do a guess based on our strategy.

        - particle can be '0' or '1'
        - If computeTheoretical=True we are computing the theorecical values and
          that means that NO simulation is done.
        """
        self.logger.debug("[step : %d] Particle : %s" % (self.step, particle))

        # ------------------------------------------
        # Step 1 : compute the p_0 and p_1 based
        #          on the probability of every experiment and
        #          We apply a Greedy Strategy (experiment with higher probability)
        # ------------------------------------------
        tmp_p_0=0.0
        tmp_p_1=0.0
        for experiment in self.experiments:
            self.logger.debug("P(%s) : %f" % (experiment, experiment['prob'][self.step]))
            # In the theoretical computation we set a greedy strategy where 
            # we take as p_X the higher probability of the hypothesis that that
            # if this step the value of 'particle'
            if computeTheoretical:
                if experiment['states'][self.step]=='0':
                    if tmp_p_0<experiment['prob'][self.step]:
                        tmp_p_0 = experiment['prob'][self.step]
                if experiment['states'][self.step]=='1':
                    if tmp_p_1<experiment['prob'][self.step]:
                        tmp_p_1 = experiment['prob'][self.step]
            # If the experimental one, we campute p_X properly :-)
            else:
                if experiment['states'][self.step]=='0':
                    tmp_p_0 += experiment['prob'][self.step]
                if experiment['states'][self.step]=='1':
                    tmp_p_1 += experiment['prob'][self.step]

        self.logger.debug("Tmp P(0) : %f" % (tmp_p_0))
        self.logger.debug("Tmp P(1) : %f" % (tmp_p_1))

        # Normalize so it is a good probability
        p_0=tmp_p_0/(tmp_p_0+tmp_p_1)
        p_1=tmp_p_1/(tmp_p_0+tmp_p_1)

        self.logger.debug("P(0) : %f" % (p_0))
        self.logger.debug("P(1) : %f" % (p_1))

        # ------------------------------------------
        # Step 2 : get the Heltrom's PVM
        # ------------------------------------------
        V_0, V_1 = helstrom.getPVM(p_0, p_1, self.theta)
        self.logger.debug (">>> PVM")
        self.logger.debug (V_0)
        self.logger.debug (V_1)

        # ------------------------------------------
        # Step 3 : perform the measurement
        # TODO : maybe this part can go out of this class to make it more generic
        # ------------------------------------------
        self.oPVM=CPVM([V_0, V_1])
        # my_result : 0 / 1
        my_result=int(particle) if computeTheoretical else self.oPVM.measure(self.state_0 if particle=='0' else self.state_1)

        self.logger.debug("Prob(0|0) : %e" % (self.oPVM.getProb(0, self.state_0)))
        self.logger.debug("Prob(0|1) : %e" % (self.oPVM.getProb(0, self.state_1)))
        self.logger.debug("Prob(1|0) : %e" % (self.oPVM.getProb(1, self.state_0)))
        self.logger.debug("Prob(1|1) : %e" % (self.oPVM.getProb(1, self.state_1)))

        # ------------------------------------------
        # Comptue the probability of any result
        # ------------------------------------------
        for outcome, item in self.outcomes.items(): 
            item['probs'].append(0)
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            for outcome, item in self.outcomes.items(): 
                item['probs'][-1] += self.oPVM.getProb(int(outcome), self.state_0 if state=='0' else self.state_1) * experiment['prob'][self.step] 

        # ------------------------------------------
        # Step 4 : update the priors
        # ------------------------------------------
        # Get the probability of getting that result  
        #     p_my_result = SUM_hypothesis { p(result|hypothesis) * p (hypothesis) }
        # where:
        #     -  p(result|hypothesis) = p(result|PSI) OR p(result|PHI) depending on 
        #        the value of hypothesis in 'step' if it is PSI or PHI 
        p_my_result = 0.0
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            tmp = self.oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1) * experiment['prob'][self.step] 
            p_my_result += tmp
            self.logger.debug("Prob(%d|%s=%s)*%e : %e" % (my_result, state, experiment['states'], experiment['prob'][self.step], tmp))
        self.logger.debug("Prob(%d) : %f" % (my_result, p_my_result))
        
        # Now update the probability for every hypothesis using Bayesian
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            my_new_prior = self.oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1) * experiment['prob'][self.step] 
            # print(experiment['states'])
            # print(self.oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1), experiment['prob'][self.step],  p_my_result, my_new_prior/p_my_result)
            # print(experiment['prob'][self.step],  p_my_result, my_new_prior/p_my_result)
            # print(p_my_result, my_new_prior/p_my_result)
            # print(my_new_prior/p_my_result)

            if p_my_result>1e-10:
                experiment['prob'].append(my_new_prior/p_my_result)
                self.logger.debug("New Prior (%s) %f * %f / %f : %f" % (experiment['states'], self.oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1), experiment['prob'][self.step],  p_my_result, my_new_prior/p_my_result))
            else:
                self.logger.debug("No update priors (p_my_result=%f)" % (p_my_result))
        self.logger.debug (json.dumps(self.experiments, indent=2))

        self.step+=1

        # Return the my_result
        return my_result

    def getHypothesis(self):
        """ Get our guess at this moment. """

        # Find the most probable
        winner=None
        p_higher=None
        for experiment in self.experiments:
            my_prob=experiment['prob'][-1]
            self.logger.debug ("P(%s) : %f" % (experiment['states'], my_prob))
            if p_higher is None or my_prob > p_higher:
                winner=experiment
                p_higher=my_prob
        self.logger.debug ("Winner : %s" % (winner['states']))

        return winner['states']

    def getPS(self, p_experiment):
        """ Get the probability of a certain experiment. """

        pS=None
        for item in self.experiments:
            if item['states']==p_experiment:
                pS=item['prob'][-1]
                break

        return pS

    def getMaxPS(self):
        """ Get the probability of a certain experiment. """

        pS=None
        for item in self.experiments:
            if item['states']==p_experiment:
                pS=item['prob'][-1]
                break

        return pS

    def dump(self):
        print (json.dumps(self.experiments, indent=2))

    def getProbOutcomes(self, outcomes):
        """Get the probability of a sequence like 01100."""

        prob=1.0
        self.logger.debug(json.dumps(self.outcomes, indent=2))
        for step, outcome in enumerate(outcomes):
            prob *= self.outcomes[outcome]['probs'][step]
        self.logger.debug("P(%s) : %e" % (outcomes, prob))

        return prob

    def getMaxLikelihood(self):
        """Return the max. likelihood that is the higest probability."""

        prob=0.0
        for item in self.experiments:
            if item['prob'][-1]>prob:
                prob=item['prob'][-1]

        return prob

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('MainLogger')

    # - Help Multiline
    # - Show default values
    class MyArgumentFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawTextHelpFormatter):
         pass

    parser = argparse.ArgumentParser(formatter_class=MyArgumentFormatter, description='')

    # Actions
    # parser.add_argument('--action', action="store_true", help='<Help>')

    # Required
    parser.add_argument('--theta',    default="0.04", help='<Help>')
    parser.add_argument('--c',        help='<Help>')
    parser.add_argument('--outcome',  default="01110", help='<Help>')
    parser.add_argument('--experiments',  default=['11111','01111','00111','00011','00001'], help='List of possible experiements')

    # Optional

    args = parser.parse_args()

    # Check parameters
    c=args.c if args.c else math.cos(2*float(args.theta))

    # Run
    #EXPERIMENTS=['11111','01111','00111','00011','00001']
    obj=CBayesian(args.experiments, c)
    for value in args.outcome:
        print(value)
        result=obj.performMeasurement(int(value), True)

    # obj.dump()

    for experiment in args.experiments:
        print("P(%s) : %e" % (experiment, obj.getPS(experiment)))
