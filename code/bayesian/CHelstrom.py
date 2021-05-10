import helstrom
from CPVM import CPVM
import math
import numpy as np
import logging
import utils

class CHelstrom:
    """ The difference with Bayesian is that we keep the same measurement all the time. 

    It is cambination of CBayesian and CBasic."""

    def __init__(self, experiments, c):
        self.logger=logging.getLogger("MainLogger")

        # Indicates in which step we are, it has influence when we compute
        # our PVM
        self.step=0
        self.experiments=experiments
        self.totSteps=len(self.experiments[0])

        # c represents the angle between the states : <0|1> and it is an angle
        # betwen [0,pi/2] BUT in our case, because we are going to use Helstrom,
        # the angle is the half
        self.theta=math.acos(c)/2
        self.state_0=[math.cos(self.theta),  math.sin(self.theta)]
        self.state_1=[math.cos(self.theta), -math.sin(self.theta)]

    def performMeasurement(self, particle):
        """ Perform the measurement of a particle. In this case we keep the same measurment
        """
        self.logger.debug("[step : %d] Particle : %s" % (self.step, particle))

        # ------------------------------------------
        # Step 1 : compute the p_0 and p_1 based on
        # the number of states each experiment has for both states
        # The main difference with the Bayesian is that in this case we
        # don't have into account the priors for each experiment.
        # ------------------------------------------
        tmp_p_0=0.0
        tmp_p_1=0.0
        for experiment in self.experiments:
            if experiment[self.step]=='0':
                tmp_p_0 += 1
            if experiment[self.step]=='1':
                tmp_p_1 += 1

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

        # Return the my_result
        self.step+=1
        return my_result

    def getHypothesis(self):
        """ Get our guess at this moment. 

        In this case the hypotehsis is given by the step we are, so when we have detected the change, like the Basic"""

        winner=utils.getHypothesis(self.step, self.totSteps)

        self.logger.debug("[step : %d/%d] MyHypotheis : %s" % (self.step, self.totSteps, winner))

        return winner
