import helstrom
from CPVM import CPVM
from math import sqrt, acos, sin, cos
import numpy as np
import logging
from qiskit import QuantumCircuit, transpile 
import argparse

class CPOVM:
    def __init__(self, experiments, c):
        self.logger=logging.getLogger("MainLogger")

        # Indicates in which step we are, it has influence when we compute
        # our POVM
        self.step=0
        self.experiments=experiments

        # c represents the angle between the states : <0|1> and it is an angle
        self.c=c
        self.theta=acos(c)
        self.state_0=[1,0]
        self.state_1=[cos(self.theta), sin(self.theta)]

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

        # Possible values
        # - self.step = 1 => Particle in first position : 11111
        # - self.step = 2 => Particle in first position : 01111
        # - self.step = 3 => Particle in first position : 00111
        # - self.step = 4 => Particle in first position : 00011
        # - self.step = 5 => Particle in first position : 00001
        # eg. if self.step=1 thet means we have stop then because we encouter
        winner="".ljust(self.step-1,'0').ljust(self.totSteps,'1')

        self.logger.debug("[step : %d/%d] MyHypotheis : %s" % (self.step, self.totSteps, winner))

        return winner

    def getCircuit(self, p_eta0, p_eta1):
        deno=sqrt(1-self.c**2)
        U = [[sqrt(1-sqrt(p_eta0*p_eta1)*self.c)/deno, 0, 0, -sqrt(p_eta0*p_eta1*self.c)/deno],
              [0                                     , 1, 0, 0                           ],
              [0                                     , 0, 1, 0                           ],
              [sqrt(p_eta0*p_eta1*self.c)/deno       , 0, 0, sqrt(1-sqrt(p_eta0*p_eta1)*self.c)/deno]]
        # U = [[1,0,0,0],
        #       [0,0,0,1],
        #       [0,1,0,0],
        #       [0,0,1,0]]
        qc = QuantumCircuit(2)
        qc.unitary(U, [0,1]) 
        qc.draw(output='mpl')
        print (qc)
        trans_qc = transpile(qc, basis_gates=['cx', 'u3'])
        print (trans_qc)

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions
    # parser.add_argument('--action', action="store_true", help='<Help>')

    # Required

    # Optional
    parser.add_argument('--eta0',  default=0.5, type=float, help='<Help>')
    parser.add_argument('--eta1',  default=0.5, type=float, help='<Help>')
    parser.add_argument('--c',     default=0.5, type=float, help='<Help>')

    args = parser.parse_args()

    # Check parameters


    # Run
    obj=CPOVM(None, args.c)
    obj.getCircuit(args.eta0, args.eta1)
