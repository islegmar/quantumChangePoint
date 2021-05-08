import argparse
import numpy as np
import math
from numpy import linalg as LA
import sys
import csv
import copy

PSI='Psi'
PHI='Phi'

def genCSV(stopAt1, probH4States):
    p_csv="bayesian_stop_%r_ph_%r.csv" % (stopAt1, probH4States)

    # Ok, not too efficient but it helps in the notation
    # - states : it is the state for every experiment in every step
    # - prob   : it is the probability of that experiment in that step (initially all have the same likelihood)
    EXPERIMENTS={
        'H5' : {
            'states' : [PSI, PSI, PSI, PSI, PHI],
            'prob'   : [1/5],
            'str'    : "00001"
        },
        'H4' : {
            'states' : [PSI, PSI, PSI, PHI, PHI],
            'prob'   : [1/5],
            'str'    : "00011"
        },
        'H3' : {
            'states' : [PSI, PSI, PHI, PHI, PHI],
            'prob'   : [1/5],
            'str'    : "00111"
        },
        'H2' : {
            'states' : [PSI, PHI, PHI, PHI, PHI],
            'prob'   : [1/5],
            'str'    : "01111"
        },
        'H1' : {
            'states' : [PHI, PHI, PHI, PHI, PHI],
            'prob'   : [1/5],
            'str'    : "11111"
        }
    }

    # Level of logs
    LOG_LEVEL_LOW_DEBUG=200
    LOG_LEVEL_DEBUG=100
    LOG_LEVEL_INFO=10

    # ------------------------------------------
    # Utilities
    # ------------------------------------------
    def getProb(op_measurement, state):
        """ Get the probability of an measurement for a certain state """
        
        return np.vdot(op_measurement, state)**2

    def eqFloat(f1, f2):
        return abs(f1 - f2) < 1e-10

    def trace(log_level, msg):
        if LOG_LEVEL_CURRENT >= log_level:
            print(msg)

    def float2Str(num):
        return "%0.4f" % (num)

    # ------------------------------------------
    # Methods
    # ------------------------------------------
    def getHelstromPOVM(step, experiments, theta):
        """ Return the POVM for that step in the experiment. 
        
        It has into account the prior information.
        """
        
        trace (LOG_LEVEL_LOW_DEBUG, ">>> Step %d" % (step))

        # ------------------------------------------
        # Step 1 : compute the p_psi and p_phi based
        #          on the probability of every experiment and
        #          the step we are (how many expermients contribute 
        #          to every state)
        # ------------------------------------------
        p_psi=0.0
        p_phi=0.0
        for name, item in experiments.items():
            if probH4States:
                if item['states'][step]==PSI: p_psi += item['prob'][step]
                if item['states'][step]==PHI: p_phi += item['prob'][step]
            else:
                trace (LOG_LEVEL_LOW_DEBUG, "\t[%s] Step : %d, State : %s, Prob : %f" % (name, step, item['states'][step], item['prob'][step]))
                if item['states'][step]==PSI and p_psi< item['prob'][step]:
                    p_psi = item['prob'][step]
                if item['states'][step]==PHI and p_phi< item['prob'][step]:
                    p_phi = item['prob'][step]
                                
        trace (LOG_LEVEL_DEBUG, "\tP_Psi = %f" % (p_psi))
        trace (LOG_LEVEL_DEBUG, "\tP_Phi = %f" % (p_phi))
        trace (LOG_LEVEL_LOW_DEBUG, "\tP_Psi + P_Phi = %f (must be one)" % (p_psi + p_phi))
        # assert eqFloat(p_psi + p_phi,1.0), "P_Psi + Phi must be 1"
           
        # ------------------------------------------
        # Step 2 : Hesltrom to get the probabilities
        # ------------------------------------------
        gamma=np.array([
            [ (p_psi-p_phi)*math.cos(theta)**2, (1/2)*math.sin(2*theta)        ],
            [ (1/2)*math.sin(2*theta)         , (p_psi-p_phi)*math.sin(theta)**2]
        ])
        W, V = LA.eig(gamma)
        
        print (W)
        print (V)
        
        # Obtain the measurement operator for Psi and Phi
        # - Psi : The eigenvector with the positive eigenvalue
        # - Phi : The eigenvector with the negative eigenvalue 
        print ("W[0] : %f, W[1] : %f" % (W[0], W[1]))
        V_Psi=V[:,0] if W[0] > W[1] else V[:,1]
        V_Phi=V[:,0] if W[0] < W[1] else V[:,1]

        assert eqFloat(np.vdot(V_Psi, V_Psi), 1.0), "V_Psi length 1"
        assert eqFloat(np.vdot(V_Phi, V_Phi), 1.0), "V_Phi length 1"
        assert eqFloat(np.vdot(V_Psi, V_Phi), 0.0), "V_Psi and V_Phi ortogonal"
        
        return {
            PSI : {
                "prob" : p_psi,
                "operator" : V_Psi
            },
            PHI : {
                "prob" : p_phi,
                "operator" : V_Phi
            }
        }

    def debugData(row, data, state_psi, state_phi):
        V_Psi = data[PSI]["operator"]
        V_Phi = data[PHI]["operator"]   

        # Now compute the probabilities of measurement 
        p_psi_psi = getProb(V_Psi, state_psi)
        p_phi_psi = getProb(V_Phi, state_psi)
        p_psi_phi = getProb(V_Psi, state_phi)
        p_phi_phi = getProb(V_Phi, state_phi)
        
        trace (LOG_LEVEL_LOW_DEBUG, "\tState Psi")
        trace (LOG_LEVEL_LOW_DEBUG, "\t\tP(Psi|Psi) : %f" % (p_psi_psi))
        trace (LOG_LEVEL_LOW_DEBUG, "\t\tP(Phi|Psi) : %f" % (p_phi_psi))
        # If the state is Psi I can measure Psi or Phi so the sum must be 1
        assert eqFloat(p_psi_psi + p_phi_psi, 1.0), "P(Psi|Psi) + P(Phi|Psi) = 1"
        
        trace (LOG_LEVEL_LOW_DEBUG, "\tState Phi")
        trace (LOG_LEVEL_LOW_DEBUG, "\t\tP(Psi|Phi) : %f" % (p_psi_phi))
        trace (LOG_LEVEL_LOW_DEBUG, "\t\tP(Phi|Phi) : %f" % (p_phi_phi))
        # If the state is Phi I can measure Psi or Phi so the sum must be 1
        assert eqFloat(p_psi_phi + p_phi_phi, 1.0), "P(Psi|Phi) + P(Phi|Phi) = 1"

        # If I measure Psi is becuase mainly the state is Psi
        assert p_psi_psi >= p_psi_phi, "P(Psi|Psi) > P(Psi|Phi)"
        
        # If I measure Phi is becuase mainly the state is Phi
        assert p_phi_phi >= p_phi_psi, "P(Phi|Phi) > P(Phi|Psi)"

        row.append(float2Str(p_psi_psi))
        row.append(float2Str(p_phi_psi))
        row.append(float2Str(p_psi_phi))
        row.append(float2Str(p_phi_phi))

    def updatePriors(my_row, my_result, step, experiments, data, state_psi, state_phi):
        """ Given I get as result, update the priors. 

        my_result can be PSI or PHI
        """

        my_row.append(my_result)
        
        print(data)
        print(my_result)
        my_operator = data[my_result]["operator"]

        # ------------------------------------------
        # Step 4 : Given that result, update the probabilities of every experiment
        # ------------------------------------------

        # Get the probability of getting that result  
        #     p_my_result = SUM_hypothesis { p(result|hypothesis) * p (hypothesis)
        # where:
        #     -  p(result|hypothesis) = p(result|PSI) OR p(result|PHI) depending on 
        #        the value of hypothesis in 'step' if it is PSI or PHI 
        p_my_result = 0.0
        for name, item in experiments.items():
            state = item['states'][step]
            if state==PSI:
                p_my_result += item['prob'][step] * getProb(my_operator, state_psi)
            else:
                p_my_result += item['prob'][step] * getProb(my_operator, state_phi)
            trace (LOG_LEVEL_LOW_DEBUG, "\t\tName : %s, State : %s, p_my_result : %f" % (name, state, p_my_result))
            
        trace (LOG_LEVEL_LOW_DEBUG, "\tP(my_result=%s) : %f" % (my_result, p_my_result))
        my_row.append(float2Str(p_my_result))
        
        for name, item in experiments.items():
            state = item['states'][step]
            if state==PSI: 
                item['prob'].append((item['prob'][step]*getProb(my_operator, state_psi)) / p_my_result)
            if state==PHI: 
                item['prob'].append((item['prob'][step]*getProb(my_operator, state_phi)) / p_my_result)
            trace (LOG_LEVEL_DEBUG, "\tP(%s) : %f => %f (state : %s)" % (name, item['prob'][step], item['prob'][step+1], state))    
            
            
    LOG_LEVEL_CURRENT = LOG_LEVEL_LOW_DEBUG

    KEYS=sorted(EXPERIMENTS.keys(), reverse=True)
    TOT_STEPS=len(EXPERIMENTS['H1']['states'])

    theta=math.pi/64
    state_psi=np.transpose(np.array([math.cos(theta),  math.sin(theta)]))
    state_phi=np.transpose(np.array([math.cos(theta), -math.sin(theta)]))

    assert eqFloat(np.vdot(state_psi, state_psi), 1.0), "state_Psi length 1"
    assert eqFloat(np.vdot(state_phi, state_phi), 1.0), "state_Phi length 1"

    with open(p_csv, 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')
        header=[]
        header.append("Output")
        for key in KEYS:
            header.append("%s (%s)" % (key, EXPERIMENTS[key]["str"]))

        for step in range(TOT_STEPS):
            header.append("[%d] P_PSI" % (step+1))
            header.append("[%d] P_PHI" % (step+1))
            header.append("[%d] V_PSI" % (step+1))
            header.append("[%d] V_PHI" % (step+1))
            header.append("[%d] p_psi_psi" % (step+1))
            header.append("[%d] p_phi_psi" % (step+1))
            header.append("[%d] p_psi_phi" % (step+1))
            header.append("[%d] p_phi_phi" % (step+1))
            header.append("[%d] result" % (step+1))
            header.append("[%d] P(result)" % (step+1))
            for key in KEYS:
                header.append("[%d] %s" % (step+1, key))
        writer.writerow(header)

        # Loop over all the possible 32 outcomes
        for output_int in range(1,32):
            my_experiments=copy.deepcopy(EXPERIMENTS)
            output_str=format(output_int, '05b')

            # Partial data for the row
            my_partial_row=[]
            # Loop over the possible results for every experiment
            for step in range(TOT_STEPS):
                result_int=int(output_str[step])
                result_str=PSI if result_int==0 else PHI

                # Step 1> Get the POVM for this step
                data=getHelstromPOVM(step, my_experiments, theta)
                my_partial_row.append(float2Str(data[PSI]["prob"]))
                my_partial_row.append(float2Str(data[PHI]["prob"]))
                my_partial_row.append(data[PSI]["operator"])
                my_partial_row.append(data[PHI]["operator"])

                # Step 2> Add some aditional info
                debugData(my_partial_row, data, state_psi, state_phi)

                # result=measureHelstrom(hypo_data['states'][step], theta, povm)
                trace(LOG_LEVEL_INFO, "\t\tMeasured : %s" % (result_str))
                # Step 3> Update the priors with this result
                updatePriors(my_partial_row, result_str, step, my_experiments, data, state_psi, state_phi)

                for key in KEYS:
                    my_partial_row.append(float2Str(my_experiments[key]['prob'][-1]))

                # If we get a 1 we top
                if stopAt1 and result_int==1:
                    break

            # Find the most probable
            winner=None
            p_higher=None
            for name, item in my_experiments.items():
                my_prob=item['prob'][-1]
                if p_higher is None or my_prob > p_higher:
                    winner=name
                    p_higher=my_prob

            # All the row data
            my_row=[]
            my_row.append(output_str)
            for key in KEYS:
                my_row.append("X" if key==winner else "")
            my_row.extend(my_partial_row)

            writer.writerow(my_row)
        
    print ("")
    print ("File %s created!" % (p_csv))
    print ("Stop in the first 1 : %r " % (stopAt1))
    print ("Use prob. hypothesis when compute prob. Psi and Phi : %r " % (probH4States))

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions
    #parser.add_argument('--stop', action="store_true", help='<Help>')
    #parser.add_argument('--ph', action="store_true", help='<Help>')

    # Required

    # Optional
    parser.add_argument('--stop',  type=int, help='If True it stops when we get the first 1')
    parser.add_argument('--ph',    type=int, help='If True we use the P(H) when computing P(Psi) and P(Phi)')

    args = parser.parse_args()

    # Check parameters

    # Main
    genCSV(bool(args.stop), bool(args.ph))
