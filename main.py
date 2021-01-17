# -*- coding: utf-8 -*-
""" Template script """
import argparse
import numpy as np
from numpy import linalg as LA
import matplotlib.pyplot as plt
import math


# -----------------------------------------------------------------------------
# Global Variables
# -----------------------------------------------------------------------------
VERBOSE=True

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def trace(line):
    """ Trace function. """
    if VERBOSE:
        print (line)

def sqrtM(M):
    """ Calculate the square root of a matrix using spectral theorem.

    Every diagonalizable matrix M can be descomposed as

    M = P * D * P^-1

    where:
    - P is the matrix where column-k is the eigenvector-k
    - D is a diagonal matrix where in the column-k has the eigenvalue-k
    - P^-1 is the inverse of P
    """
    # w,v = LA.eig(M)
    #
    # w(..., M) array
    #   The eigenvalues, each repeated according to its multiplicity. 
    #   The eigenvalues are not necessarily ordered. The resulting array will 
    #   be of complex type, unless the imaginary part is zero in which case 
    #   it will be cast to a real type. When a is real the resulting 
    #   eigenvalues will be real (0 imaginary part) or occur in conjugate pairs
    #
    # v(..., M, M) array
    #   The normalized (unit “length”) eigenvectors, such that the column 
    #   v[:,i] is the eigenvector corresponding to the eigenvalue w[i].
    eigenValues, eigenVectors = LA.eig(M)
    # trace (eigenValues)
    # trace (eigenVectors)

    P=eigenVectors
    D=np.multiply(eigenValues, np.identity(len(eigenValues)))
    PInv=LA.inv(P)
    # trace(">>> P")
    # trace(P)
    # trace(">>> D")
    # trace(D)
    # trace(">>> sqrt(D)")
    # trace(np.sqrt(D))
    # trace(">>> P^-1")
    # trace(LA.inv(P))
    # trace(">>> P * P^-1 = I")
    # trace(np.matmul(P,LA.inv(P)))

    # trace(">>> M")
    # trace(M)
    # trace(">>> PDP^-1 = M")
    # trace(np.matmul(np.matmul(P,D), LA.inv(P)))

    # Compute P * sqrt(D) * P^-1
    sqrtM=np.matmul(np.matmul(P,np.sqrt(D)), PInv)
    # trace(">>> M")
    # trace(M)
    # trace(">>> sqrt(M)")
    # trace(sqrtM)
    # trace(">>> sqrt(M) * sqrt(M) = M")
    # trace(np.matmul(sqrtM, sqrtM))

    return sqrtM

# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------
def graphFixedN(n, minC, maxC, stepC, fOut=None):
    """ Draw the graph for bounds probability.

    In this case N is fixed and we analize how it changes with the 
    distance c"""

    fig, ax = plt.subplots()
    x_values = []
    lower = []
    upper = []

    c=minC
    while c<maxC:
        p=computeProbBounds(c,n)
        print (">>> n : {n}, c : {c}".format(**locals()))
        x_values.append(math.sqrt(c))
        lower.append(p[0])
        upper.append(p[1])
        c+=stepC

    print (lower)
    print (upper)
    ax.plot(x_values, upper, label='upper')
    ax.plot(x_values, lower, label='lower')

    ax.set_ylabel('Probability')
    ax.set_xlabel('Value c^2')
    ax.set_title('Probablities for N = %d' % (n))
    ax.legend()

    if fOut:
        plt.savefig(fOut)
        trace("Image saved in %s." % (fOut))
    else:
        plt.show()

def graphFixedC(c, minN, maxN, stepN, fOut=None):
    """ Draw the graph for bounds probability.

    In this case c is fixed and we analize how it changes with the 
    number por particles"""

    fig, ax = plt.subplots()
    x_values = []
    lower = []
    upper = []
    # We could use range but let's put it like graphFixedN
    n=minN
    while n<=maxX:
        p=computeProbBounds(c,n)
        print (">>> n : {n}, c : {c}".format(**locals()))
        x_values.append(n)
        lower.append(p[0])
        upper.append(p[1])
        n+=stepN

    ax.plot(x_values, upper, label='upper')
    ax.plot(x_values, lower, label='lower')

    ax.set_ylabel('Probability')
    ax.set_xlabel('Number of particles')
    ax.set_title('Probablities for c = %f' % (c))
    ax.legend()

    if fOut:
        plt.savefig(fOut)
        trace("Image saved in %s." % (fOut))
    else:
        plt.show()

def computeProbBounds(distance0_Phi, numberParticles):
    """ Compute the bound probabilities for set of partticles. """
    
    # c that is the distance between |0> and |Phi> is a number between
    # 0 and 1
    c=distance0_Phi
    N=numberParticles

    trace (">>>> c")
    trace(c)
    trace (">>>> N")
    trace(N)

    # Compute the Gramm Matrix
    rows=[]
    for indR in range(N):
        row=[]
        for indC in range(N):
            # In the diagonal elements, when c=0 we have to evaluate
            # 0^0 that is ind. but we know we want to put a 1 always
            # in the diagonal
            row.append(1.0 if indC==indR else c ** abs(indR-indC))
        rows.append(row)

    G=np.array(rows)

    trace (">>>> G")
    trace (G)

    sqrtG=sqrtM(G)
    traceSqrtG=np.trace(sqrtG)
    trace (">>>> SQRT(G)")
    trace(sqrtG)

    trace (">>>> SQRT(G) * SQRT(G)")
    trace(np.matmul(sqrtG,sqrtG))

    # lambdaMax = maximum eigenvalue of G
    eigenValuesG, eigerVectorsG = LA.eig(G)
    lambdaMax=np.max(eigenValuesG)
    print(">>> Lambda Max")
    print(lambdaMax)

    # Probability distribution
    # Vector q => qK=(sqrt(G)kk/tr(sqrt(G)))
    vQ=np.empty([N])
    for i in range(N):
        vQ[i]=sqrtG[i,i]/traceSqrtG
    print(">>> q")
    print(vQ)
    print(">>> Sum(q)=1")
    print(np.sum(vQ))

    # Uniform disrtibution
    # Vector u = 1/N
    vU=np.empty([N])
    for i in range(N):
        vU[i]=1.0/N
    print(">>> u")
    print(vU)
    print(">>> Sum(u)=1")
    print(np.sum(vU))

    # Trace norm between (q,u) = Sum(abs(qk-uk))
    traceNormQU=0.0
    for i in range(N):
      traceNormQU += abs(vQ.item(i)-vU.item(i))
    print(">>> traceNorm(q,u)")
    print(traceNormQU)

    lowerBoundP=(traceSqrtG/N)**2
    upperBoundP=lowerBoundP + math.sqrt(lambdaMax) * traceNormQU

    print("""
===============================================================================
Matrix G for value of c={c}

{G}

For it, the Pmax is bounded with the limits

[{lowerBoundP}, {upperBoundP}]

""".format(**locals()))

    return [lowerBoundP, upperBoundP]


# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions
    parser.add_argument('--graph', action="store_true", help='<Help>')

    # Required

    # Optional
    parser.add_argument('--c',  default=0.0, type=float, help='Distance between |0> and |Phi> as a value between 0 and 1')
    parser.add_argument('--N',  default=5, type=int, help='Number of particles')
    parser.add_argument('--minC', default=None, type=float, help='If graph : minC with a certain N')
    parser.add_argument('--maxC', default=None, type=float, help='If graph : maxC with a certain N')
    parser.add_argument('--stepC', default=0.1, type=float, help='If graph : step C')
    parser.add_argument('--minN', default=None, type=int, help='If graph : minN with a certain c')
    parser.add_argument('--maxN', default=None, type=int, help='If graph : maxN with a certain c')
    parser.add_argument('--stepN', default=1, type=int, help='If graph : step N')
    parser.add_argument('--image', help='If spefified, safe the image in file instead showing it')

    args = parser.parse_args()

    # Check parameters

    # Run
    if args.graph:
        if args.minC is not None and args.maxC is not None:
            graphFixedN(args.N, args.minC, args.maxC, args.stepC, args.image)
        else:
            graphFixedC(args.c, args.minN, args.maxN, args.stepN, args.image)
    else:
        computeProbBounds(args.c, args.N)

