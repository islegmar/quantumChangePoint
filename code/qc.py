# -*- coding: utf-8 -*-
""" Quantum circuits. """

import argparse
import math
import numpy as np
from numpy import linalg as LA
from numpy import pi
import utils
from utils import (
  trace,
  LOG_LEVEL_NO,
  LOG_LEVEL_INFO,
  LOG_LEVEL_DEBUG,
  LOG_LEVEL_LOW_DEBUG,
  CURR_LOG_LEVEL
)

from qiskit import(
  QuantumCircuit,
  QuantumRegister,
  ClassicalRegister,
  execute,
  Aer
)

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def getAngle(v):
    return pi/2 if v[0]==0.0 else math.atan(v[1]/v[0])

def getU3(state):
    """ Return the three angles for U3 to transform U3|0> = a|0> + b|1> (state)

    TODO : it has some limitations:
    - a and b are real
    - a >0
    - angle between a and b [0,pi/2]

    So it is for vectors like:
    - sin(theta)|0> + sin(theta)|1>
    - sin(theta)|0> - sin(theta)|1>
    """

    # TODO : do the verifictions of the above constraints

    theta=2*math.acos(state[0])
    phi=0
    lam=0

    if state[1]<0: theta = -theta

    # U3=np.array([
    #     [math.cos(theta/2)               , np.exp(-1j*lam)*math.sin(theta/2)], 
    #     [np.exp(1j*phi)*math.sin(theta/2), np.exp(1j*(phi+lam))*math.cos(theta/2)]
    # ])
    # print (U3)
    # print (U3@np.array([[1],[0]]))

    return [theta, phi, lam]

def measureOneParticle(state, V):
    """ Perform a measurement in a state defined by theta:
    
    - state : Psi / Phi
    - |Psi> : cos(theta)|0> + sin(theta)|1>
    - |Phi> : cos(theta)|0> - sin(theta)|1>
    
    and we measure with the operator v_psi

    https://qiskit.org/documentation/stubs/qiskit.circuit.library.U3Gate.html
    """
    simulator = Aer.get_backend('qasm_simulator')
    
    qreg_q = QuantumRegister(1, 'q')
    creg_c = ClassicalRegister(1, 'c')
    circuit = QuantumCircuit(qreg_q, creg_c)
 
    # theta, phi, lam=getU3(state)
    circuit.u(2*getAngle(state), 0, 0, qreg_q[0])
    
    # Now perform a U3 rotation to measure in the basis by V
    # Not sure about that but I would do a rotation with the inverse angle of v_psi so in that case:
    # - Psi => |0>
    # - Phi => |1>
    circuit.u(-2*getAngle(V),0,0,qreg_q[0])
    
    # Map the quantum measurement to the classical bits
    circuit.measure(qreg_q, creg_c)
            
    job = execute(circuit, simulator, shots=100)
    result = job.result()
    counts = result.get_counts(circuit)

    print (counts)
    
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
    state_plus  = [1/math.sqrt(2),  1/math.sqrt(2)]
    state_minus = [1/math.sqrt(2), -1/math.sqrt(2)]
    V_plus      = [1/math.sqrt(2),  1/math.sqrt(2)]

    # Returns 0 => |+>
    print (measureOneParticle(state_plus,  V_plus))

    # Returns 1 => |->
    print (measureOneParticle(state_minus, V_plus))
