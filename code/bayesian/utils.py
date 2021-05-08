def getHypothesis(stepWithChange, totSteps):
    """ Return a string with the form 0....1..... """

    # For example in the case totSteps=5
    # - stepWithChange = 1 => Particle in first position : 11111
    # - stepWithChange = 2 => Particle in first position : 01111
    # - stepWithChange = 3 => Particle in first position : 00111
    # - stepWithChange = 4 => Particle in first position : 00011
    # - stepWithChange = 5 => Particle in first position : 00001
    # eg. if stepWithChange=1 thet means we have stop then because we encouter
    return "".ljust(stepWithChange-1,'0').ljust(totSteps,'1')
