# -*- coding: utf-8 -*-
""" Measurement utilities. """

import argparse
import math
import numpy as np
from numpy import linalg as LA

PSI="Psi"
PHI="Phi"

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def getProb(op_measurement, state):
    """ Get the probability of an measurement for a certain state """
    
    return np.vdot(op_measurement, state)**2

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    pass
