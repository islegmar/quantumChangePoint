""" Implements a PVM: """
import logging
import math
import numpy as np
from qiskit import(
  QuantumCircuit,
  QuantumRegister,
  ClassicalRegister,
  execute,
  Aer
)
import logging

class CPVM:
    def __init__(self, pvm):
        self.logger=logging.getLogger("MainLogger")

        """ pvm is an array with the PVMs. """
        self.pvm=pvm

        # Test it is unitary
        res = None
        for item in self.pvm:
            if res is None:
                res  = np.outer(item, item)
            else:
                res += np.outer(item, item)

        # TODO : check it is identity taking into account we're dealing with floats
        # self.logger.debug (res)

    # TODO : static, private
    def getAngle(self, v):
        if  v[0]==0.0 and v[1]<0:
            return -math.pi/2
        elif v[0]==0.0 and v[1]>0:
            return math.pi/2
        else:
            return math.atan(v[1]/v[0])

    def measure(self, state):
        """ Perform a measurement in a state defined by theta:
        
        - state : 0 / 1
        - '0' (=Psi) : cos(theta)|0> + sin(theta)|1>
        - '1' (=Phi) : cos(theta)|0> - sin(theta)|1>
        
        and we measure with the operator v_psi
        """
        simulator = Aer.get_backend('qasm_simulator')
        
        qreg_q = QuantumRegister(1, 'q')
        creg_c = ClassicalRegister(1, 'c')
        circuit = QuantumCircuit(qreg_q, creg_c)
     
        # Rotate 0 to get the state
        theta=self.getAngle(state)
        circuit.u(2*theta,0,0,qreg_q[0])
        
        # Rotate to do a projection over the PVM
        alpha=self.getAngle(self.pvm[0])
        circuit.u(-2*alpha,0,0,qreg_q[0])
        
        # Map the quantum measurement to the classical bits
        circuit.measure(qreg_q, creg_c)
                
        job = execute(circuit, simulator, shots=100)
        result = job.result()
        counts = result.get_counts(circuit)

        self.logger.debug(counts)
        
        if '0' not in counts:
            return '1'
        elif '1' not in counts:
            return '0'
        else:
            return '0' if counts['0'] > counts['1'] else '1'

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    pvms=[
        {
            'desc' : '+/-',
            'vectors' : [
                [1/math.sqrt(2),  1/math.sqrt(2)],
                [1/math.sqrt(2),  -1/math.sqrt(2)]
            ]
        },
        {
            'desc' : '0/1',
            'vectors' : [
                [1, 0],
                [0, 1]
            ]
         }
    ]
    states=[
            {'vector' : [1/math.sqrt(2),   1/math.sqrt(2)], 'desc' : '+'},
            {'vector' : [1/math.sqrt(2),  -1/math.sqrt(2)], 'desc' : '-'},
            {'vector' : [1, 0]                            , 'desc' : '0'},
            {'vector' : [0, 1]                            , 'desc' : '1'}
    ]

    for pvm in pvms:
        self.logger.debug(">>>>>> PVM : %s" % (pvm['desc']))
        obj=CPVM(pvm['vectors'])
        for state in states:
            self.logger.debug ("\tState  : %s" % (state['desc']))
            self.logger.debug ("\tResult : %s" % (obj.measure(state['vector'])))
