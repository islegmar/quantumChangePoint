import helstrom
from CPVM import CPVM
import math
import numpy as np
import logging

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

        # c represents the angle between the states : <0|1> and it is an angle
        # betwen [0,pi/2] BUT in our case, because we are going to use Helstrom,
        # the angle is the half
        self.theta=math.acos(c)/2
        self.state_0=[math.cos(self.theta),  math.sin(self.theta)]
        self.state_1=[math.cos(self.theta), -math.sin(self.theta)]

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
            if  False and computeTheoretical:
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
            p_my_result += self.oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1) * experiment['prob'][self.step] 
        self.logger.debug("Prob(%d) : %f" % (my_result, p_my_result))
        
        # Now update the probability for every hypothesis using Bayesian
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            my_new_prior = self.oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1) * experiment['prob'][self.step] 
            experiment['prob'].append(0.0 if p_my_result<1e-20 else my_new_prior/p_my_result)
        self.logger.debug (self.experiments)

        self.step+=1

        # Return the my_result
        return my_result

    def getProb(self, result, state):
        """Return the probability of a certain result. """

        #print ("[%d] getProb(%s,%s) : %f" % (self.step, result, state, self.oPVM.getProb(int(result), self.state_0 if state=='0' else self.state_1)))
        return self.oPVM.getProb(int(result), self.state_0 if state=='0' else self.state_1)

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
