import helstrom
from CPVM import CPVM
import math
import numpy as np
import logging

class CBayesianTheoretical:
    """Compute the teoretical probability of success for the Bayesian.

    In this case we don't have an analytical formula so let's compute for
    several values of 'c'."""

    def __init__(self, experiments, c):
        self.logger=logging.getLogger("MainLogger")

        # Indicates in which step we are, it has influence when we compute
        # our PVM
        self.step=0
        self.experiments=[]
        for experiment in experiments:
            # All the experiments have same prior (in the beginning)
            self.experiments.append({
                'states' : experiment,
                'prob' : [1/len(experiments)]
            })
        self.totSteps=len(self.experiments[0]

        # c represents the angle between the states : <0|1> and it is an angle
        # betwen [0,pi/2] BUT in our case, because we are going to use Helstrom,
        # the angle is the half
        self.theta=math.acos(c)/2
        self.state_0=[math.cos(self.theta),  math.sin(self.theta)]
        self.state_1=[math.cos(self.theta), -math.sin(self.theta)]

    def getPS(self, particle):
        """Get the probability of success.

        Given that c, compute the teoretical probability of success."""

        # Loop over all the possible outcomes that are combinations of '0' and '1'
        # from  0 => 00000
        #   to 31 => 11111
        for output_int in range(0,2**self.totParticles):
            my_experiments=copy.deepcopy(self.experiments)
            # eg. output_int = 4 => output_str = 00100
            output_str=format(output_int, '0%db' % (setf.totParticles))

            # Go over all the particles in the experiment and measure the 
            # probability of every outcome
            # Perform a Bayesian
            o_measurement=CBayesian(self.experiments, self.c)
            for step in range(self.totSteps):
                result_int=int(output_str[step])
                
                measurement=o_measurement.performMeasurement(particle, True)
                if measurement==1:  break
            # Ok, now let's see w
                
                if o_measurement.getHypothesis()==experiment:
                    expOK+=1
                else:
                    expKO+=1
        # End all executions for that experiment
        logger.info("... ok = %d, ko = %d" % (expOK, expKO))
        totOK+=expOK    
        totKO+=expKO    

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
        self.logger.debug("[step : %d] Particle : %s" % (self.step, particle))

        # ------------------------------------------
        # Step 1 : compute the p_0 and p_1 
        #          For the upper bound of the priobabbility we apply a 
        #          'Greedy Strategy' where we just get the experiment with the
        #          higher probabiity
        # ------------------------------------------
        tmp_p_0=0.0
        tmp_p_1=0.0
        for experiment in self.experiments:
            self.logger.debug("P(%s) : %f" % (experiment, experiment['prob'][self.step]))
            if experiment['states'][self.step]=='0':
                if tmp_p_0<experiment['prob'][self.step]:
                    tmp_p_0 = experiment['prob'][self.step]
            if experiment['states'][self.step]=='1':
                if tmp_p_1<experiment['prob'][self.step]:
                    tmp_p_1 = experiment['prob'][self.step]

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

        # ------------------------------------------
        # Step 4 : update the priors
        # ------------------------------------------
        # Get the probability of getting that result  
        #     p_my_result = SUM_hypothesis { p(result|hypothesis) * p (hypothesis)
        # where:
        #     -  p(result|hypothesis) = p(result|PSI) OR p(result|PHI) depending on 
        #        the value of hypothesis in 'step' if it is PSI or PHI 
        p_my_result = 0.0
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            p_my_result += oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1) * experiment['prob'][self.step] 
        self.logger.debug("Prob(%d) : %f" % (my_result, p_my_result))
        
        # Now update the probability for every hypothesis using Bayesian
        for experiment in self.experiments:
            state = experiment['states'][self.step]
            my_new_prior = oPVM.getProb(my_result, self.state_0 if state=='0' else self.state_1) * experiment['prob'][self.step] 
            experiment['prob'].append(my_new_prior/p_my_result)
        self.logger.debug (self.experiments)

        self.step+=1

        # Return the my_result
        return my_result

    def getPS(self, experiment):
        """ Get the probability of a certain experiment. """

        # Find the most probable
        winner=None
        p_higher=None
        for item in self.experiments:
            if item['state
            my_prob=experiment['prob'][-1]
            self.logger.debug ("P(%s) : %f" % (experiment['states'], my_prob))
            if p_higher is None or my_prob > p_higher:
                winner=experiment
                p_higher=my_prob
        self.logger.debug ("Winner : %s" % (winner['states']))

        return winner['states']
