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
        # Maximum of steps
        self.totSteps=None
        self.experiments=[]
        for experiment in experiments:
            self.experiments.append({
                'states' : experiment,
                'prob' : [1/len(experiments)]
            })
            # TODO : check all the experiments have the same number of steps
            if self.totSteps is None: self.totSteps=len(experiment)

        # c represents the angle between the states : <0|1> and it is an angle
        # betwen [0,pi/2] BUT in our case, bacause we are going to use Helstrom,
        # the angle is the half
        self.theta=math.acos(c)/2
        self.state_0=[math.cos(self.theta),  math.sin(self.theta)]
        self.state_1=[math.cos(self.theta), -math.sin(self.theta)]

    def getProb(self, op_measurement, state):
        """ Get the probability of an measurement for a certain state """
        
        return np.vdot(op_measurement, state)**2

    def performMeasurement(self, particle):
        """ Perform the measurement of a particle and do a guess based on our strategy.

        """

        # ------------------------------------------
        # Step 1 : compute the p_psi and p_phi based
        #          on the probability of every experiment and
        #          We apply a Greedy Strategy (experiment with higher probability)
        # ------------------------------------------
        tmp_p_psi=0.0
        tmp_p_phi=0.0
        for experiment in self.experiments:
            self.logger.debug("P(%s) : %f" % (experiment, experiment['prob'][self.step]))
            if experiment['states'][self.step]=='0' and tmp_p_psi< experiment['prob'][self.step]:
                tmp_p_psi = experiment['prob'][self.step]
            if experiment['states'][self.step]=='1' and tmp_p_phi< experiment['prob'][self.step]:
                tmp_p_phi = experiment['prob'][self.step]

        self.logger.debug("Tmp P(0) : %f" % (tmp_p_psi))
        self.logger.debug("Tmp P(1) : %f" % (tmp_p_phi))
        # Normalize so it is a good probability
        p_psi=tmp_p_psi/(tmp_p_psi+tmp_p_phi)
        p_phi=tmp_p_phi/(tmp_p_psi+tmp_p_phi)

        self.logger.debug("P(0) : %f" % (p_psi))
        self.logger.debug("P(1) : %f" % (p_phi))
        # ------------------------------------------
        # Step 2 : get the Heltrom's PVM
        # ------------------------------------------
        V_Psi, V_Phi = helstrom.getPVM(p_psi, p_phi, self.theta)
        self.logger.debug (">>> PVM")
        self.logger.debug (V_Psi)
        self.logger.debug (V_Phi)

        # ------------------------------------------
        # Step 3 : perform the measurement
        # TODO : maybe this part can go out of this class to make it more generic
        # ------------------------------------------
        state=self.state_0 if particle=='0' else self.state_1
        oPvm=CPVM([V_Psi, V_Phi])
        measurement = oPvm.measure(state)

        # ------------------------------------------
        # Step 4 : update the priors
        # ------------------------------------------
        my_operator = V_Psi if measurement=='0' else V_Phi

        # Get the probability of getting that result  
        #     p_my_result = SUM_hypothesis { p(result|hypothesis) * p (hypothesis)
        # where:
        #     -  p(result|hypothesis) = p(result|PSI) OR p(result|PHI) depending on 
        #        the value of hypothesis in 'step' if it is PSI or PHI 
        p_my_result = 0.0
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            if state=='0':
                p_my_result += experiment['prob'][self.step] * self.getProb(my_operator, self.state_0)
            else:
                p_my_result += experiment['prob'][self.step] * self.getProb(my_operator, self.state_1)
        self.logger.debug("Prob(%s) : %f" % (measurement, p_my_result))
        
        # Now update the probability for every hypothesis using Bayesian
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            if state=='0': 
                experiment['prob'].append((experiment['prob'][self.step]*self.getProb(my_operator, self.state_0)) / p_my_result)
            if state=='1': 
                experiment['prob'].append((experiment['prob'][self.step]*self.getProb(my_operator, self.state_1)) / p_my_result)
        self.logger.debug (self.experiments)

        self.step+=1
        # Return the measurement
        return measurement


    def getHypothesis(self):
        """ Get our guess at this moment. """

        # Find the most probable
        winner=None
        p_higher=None
        for experiment in self.experiments:
            my_prob=experiment['prob'][-1]
            if p_higher is None or my_prob > p_higher:
                winner=experiment
                p_higher=my_prob

        return winner['states']
