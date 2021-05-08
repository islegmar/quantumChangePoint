import helstrom
from CPVM import CPVM
import math
import numpy as np
import logging
import utils

class CBasic:
    def __init__(self, experiments, c):
        self.logger=logging.getLogger("MainLogger")

        # Indicates in which step we are, it has influence when we compute
        # our PVM
        self.step=0
        self.experiments=experiments
        self.totSteps=len(self.experiments[0])

        # c represents the angle between the states : <0|1> and it is an angle
        self.theta=math.acos(c)
        self.state_0=[1,0]
        self.state_1=[math.cos(self.theta), math.sin(self.theta)]

    def performMeasurement(self, particle):
        self.logger.debug("[step : %d] Particle : %s" % (self.step, particle))

        V_0=[1,0]
        V_1=[0,1]
        oPVM=CPVM([V_0, V_1])
        # my_result : 0 / 1
        my_result = oPVM.measure(self.state_0 if particle=='0' else self.state_1)

        self.step+=1

        # Return the my_result
        return my_result

    def getHypothesis(self):
        """ Get our guess at this moment. """

        winner=utils.getHypothesis(self.step, self.totSteps)

        self.logger.debug("[step : %d/%d] MyHypotheis : %s" % (self.step, self.totSteps, winner))

        return winner
