# -*- coding: utf-8 -*-
""" Template script """
import argparse
import numpy as np
from numpy import linalg as LA
import logging
import logging.config
import math


class CSquareRoot:
    def __init__(self, p_c):
        self.logger=logging.getLogger("MainLogger")
        self.c=p_c

    # This can be an static method
    def sqrtM(self,M):
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
        self.logger.debug(">>> P")
        self.logger.debug(P)
        self.logger.debug(">>> D")
        self.logger.debug(D)
        self.logger.debug(">>> sqrt(D)")
        self.logger.debug(np.sqrt(D))
        self.logger.debug(">>> P^-1")
        self.logger.debug(LA.inv(P))
        self.logger.debug(">>> P * P^-1 = I")
        self.logger.debug(np.matmul(P,LA.inv(P)))
    
        self.logger.debug(">>> M")
        self.logger.debug(M)
        self.logger.debug(">>> PDP^-1 = M")
        self.logger.debug(np.matmul(np.matmul(P,D), LA.inv(P)))
    
        # Compute P * sqrt(D) * P^-1
        sqrtM=np.matmul(np.matmul(P,np.sqrt(D)), PInv)
        self.logger.debug(">>> M")
        self.logger.debug(M)
        self.logger.debug(">>> sqrt(M)")
        self.logger.debug(sqrtM)
        self.logger.debug(">>> sqrt(M) * sqrt(M) = M")
        self.logger.debug(np.matmul(sqrtM, sqrtM))
    
        return sqrtM

    
    def computeProbBounds(self, numberParticles):
        """ Compute the bound probabilities for set of partticles. """

        # c that is the distance between |0> and |Phi> is a number between
        # 0 and 1
        c=self.c
        N=numberParticles
    
        # trace (">>>> N")
        # self.logger.debug(N)
    
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
    
        # trace (">>>> G")
        # trace (G)
    
        sqrtG=self.sqrtM(G)
        traceSqrtG=np.trace(sqrtG)
        self.logger.debug(">>>> SQRT(G)")
        self.logger.debug(sqrtG)
    
        self.logger.debug(">>>> SQRT(G) * SQRT(G)")
        self.logger.debug(np.matmul(sqrtG,sqrtG))
    
        # lambdaMax = maximum eigenvalue of G
        eigenValuesG, eigerVectorsG = LA.eig(G)
        lambdaMax=np.max(eigenValuesG)
    
        # Probability distribution
        # Vector q => qK=(sqrt(G)kk/tr(sqrt(G)))
        vQ=np.empty([N])
        for i in range(N):
            vQ[i]=sqrtG[i,i]/traceSqrtG
        # print(">>> q")
        # print(vQ)
        # print(">>> Sum(q)=1")
        # print(np.sum(vQ))
    
        # Uniform disrtibution
        # Vector u = 1/N
        vU=np.empty([N])
        for i in range(N):
            vU[i]=1.0/N
        # print(">>> u")
        # print(vU)
        # print(">>> Sum(u)=1")
        # print(np.sum(vU))
    
        # Trace norm between (q,u) = Sum(abs(qk-uk))
        traceNormQU=0.0
        for i in range(N):
          traceNormQU += abs(vQ.item(i)-vU.item(i))
        self.logger.debug(">>> traceNorm(q,u)")
        self.logger.debug(traceNormQU)
    
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

    # Required

    # Optional
    parser.add_argument('--c',  default=0.0, type=float, help='Distance between |0> and |Phi> as a value between 0 and 1')
    parser.add_argument('--N',  default=5, type=int, help='Number of particles')

    args = parser.parse_args()

    # Check parameters

    # Run
    logging.config.fileConfig('logging.conf')
    logger = logging.getLogger('MainLogger')

    obj=CSquareRoot(args.c)
    print ("Bounds for c=%f" % (args.c))
    print (obj.computeProbBounds(args.N))
