""" In a simple measurement we don't change the PVM. """
import helstrom
from CPVM import CPVM
import math
import numpy as np
import logging

class CSimple:
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

        # c represents the angle between the states : <0|1> and it is an angle
        # betwen [0,pi/2] BUT in our case, because we are going to use Helstrom,
        # the angle is the half
        self.theta=math.acos(c)/2
        self.state_0=[math.cos(self.theta),  math.sin(self.theta)]
        self.state_1=[math.cos(self.theta), -math.sin(self.theta)]

    def performMeasurement(self, particle):
        """ Perform the measurement of a particle and do a guess based on our strategy.

        particle can be '0' or '1'
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
            if experiment['states'][self.step]=='0':
                if tmp_p_0<experiment['prob'][self.step]:
                    tmp_p_0 = experiment['prob'][self.step]
                tmp_p_0 += experiment['prob'][self.step]
            if experiment['states'][self.step]=='1':
                if tmp_p_1<experiment['prob'][self.step]:
                    tmp_p_1 = experiment['prob'][self.step]
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
        oPVM=CPVM([V_0, V_1])
        # my_result : 0 / 1
        my_result = oPVM.measure(self.state_0 if particle=='0' else self.state_1)

        # ------------------------------------------
        # Step 4 : update the priors
        # ------------------------------------------
        # Get the probability of getting that result  
        #     p_my_result = SUM_hypothesis { p(result|hypothesis) * p (hypothesis)
        # where:
        #     -  p(result|hypothesis) = p(result|PSI) OR p(result|PHI) depending on 
        #        the value of hypothesis in 'step' if it is PSI or PHI 
        p_my_result = 0.0
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            p_my_result += oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1) * experiment['prob'][self.step] 
        self.logger.debug("Prob(%d) : %f" % (my_result, p_my_result))
        
        # Now update the probability for every hypothesis using Bayesian
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            my_new_prior = oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1) * experiment['prob'][self.step] 
            experiment['prob'].append(my_new_prior/p_my_result)
        self.logger.debug (self.experiments)

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
