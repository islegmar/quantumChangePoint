# -*- coding: utf-8 -*-
""" Helstrom measurement. """

import argparse
import math
import numpy as np
from numpy import linalg as LA
from numpy import pi
import logging

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def getPVM(p_psi, p_phi, theta):
    """ Return the PVM for Helstrom. """
    
    gamma=np.array([
        [ (p_psi-p_phi)*(math.cos(theta))**2, (1/2)*math.sin(2*theta)        ],
        [ (1/2)*math.sin(2*theta)           , (p_psi-p_phi)*(math.sin(theta))**2]
    ])
    W, V = LA.eig(gamma)
    
    # Obtain the measurement operator for Psi and Phi
    # - Psi : The eigenvector with the positive eigenvalue
    # - Phi : The eigenvector with the negative eigenvalue 
    V_Psi=V[:,0] if W[0] > W[1] else V[:,1]
    V_Phi=V[:,0] if W[0] < W[1] else V[:,1]

    return V_Psi, V_Phi

    
# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions
    # parser.add_argument('--action', action="store_true", help='<Help>')

    # Required
    parser.add_argument('--pPsi',   default="0.5", help='<Help>')
    parser.add_argument('--pPhi',   default="0.5", help='<Help>')
    parser.add_argument('--theta',  default="0.5", help='<Help>')

    # Optional

    args = parser.parse_args()

    # Check parameters
    pPsi=float(args.pPsi)
    pPhi=float(args.pPhi)
    theta=float(args.theta)

    # Run
    v_psi, v_phi=getPVM(pPsi, pPhi, theta)
    print (v_psi)
    print (v_phi)
    print (quantumMeasurement(PSI, theta, v_psi))
