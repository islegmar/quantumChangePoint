from matplotlib import pyplot as plt
import numpy as np
import argparse
import os
from scipy import interpolate


BLACK="#000000"
WHITE="#FFFFFF"
RED="#FF0000"
BLUE="#0000FF"
YELLOW="#FFFF00"
CYAN="#00FFFF"
MAGENTA="#FF00FF"
BLUE_LIGHT="#ADD8E6"
GREEN="#00FF00"
GREEN_LIGHT="#90EE90"

# In order
COLORS = [
    BLACK,
    RED,
    GREEN,
    BLUE,
    YELLOW,
    CYAN
]
STRATEGIES={
        "SRM" : { "color" : "", "class" : "CBasic" },
        "PBL" : { "color" : "", "class" : "CBasic" },
        "Helstrom" : { "color" : "", "class" : "CBasic" },
        "Bayesian" : { "color" : "", "class" : "CBasic" }
}


def assertFileExists(file):
    if not os.path.isfile(file):
        raise Exception("File %s does not exist!" % (file))

def drawGlobalLocal(totC, totIterations, strategies):
    fImage="graph-globalVSlocal.png"
    for ind, strategy in enumerate(strategies):
        fileLocal="data/%s-%d-%d-global0.csv"    % (strategy, totC, totIterations)
        fileGlobal="data/%s-%d-%d-global1.csv"    % (strategy, totC, totIterations)

        if os.path.isfile(fileLocal) and os.path.isfile(fileGlobal):
            dLocal  = np.genfromtxt(fileLocal,  delimiter=",", names=["x", "y"])
            dGlobal = np.genfromtxt(fileGlobal, delimiter=",", names=["x", "y"])
            
            plt.scatter(dLocal['x'], dLocal['y'], label='%s (local)'  % (strategy[1:]), color=COLORS[2*ind])
            plt.scatter(dGlobal['x'],dGlobal['y'],label='%s (global)' % (strategy[1:]), color=COLORS[2*ind+1])
        else:
            print("Ignoring strategy %s. File %s or %s does not exist." % (strategy, fileLocal, fileGlobal))
    
    plt.title('Local vs Global')
    
    plt.xlabel('c')
    plt.ylabel('Probability')
    
    plt.grid(alpha=.4,linestyle='--')
    
    plt.legend()
    
    plt.savefig(fImage)
    print("Image %s created!" % (fImage))
    plt.show()

def drawStrategies(strategies, title, totC, totIterations):
    fImage="graph-%d-%d.png" % (totC, totIterations)
    COLOR_SQUARE_RM=BLACK
    COLOR_BAYESIAN=GREEN
    COLOR_PBL=BLUE
    COLOR_HELSTROM=RED

    c = np.arange(0.001, 1.0, 0.001)
    n=5
    for strategy in strategies:
        if strategy not in STRATEGIES:
            raise Exception("Unknown sttategy '%s'" % (strategy))

        if strategy=="PBL":
            # Theoretical
            yPBL = 1 - c**2 + c**2/n
            plt.plot(c,yPBL,label='PBL (theoretical)', color=COLOR_PBL)

            # Exprimental
            fExperimentalData="data/CBasic-%d-%d-global0.csv" % (totC, totIterations)
            assertFileExists(fExperimentalData)
            dExperimental=np.genfromtxt(fExperimentalData, delimiter=",", names=["x", "y"])
            plt.scatter(dExperimental['x'], dExperimental['y'], label='PBL (experimental)', color=COLOR_PBL)
        elif strategy=="Helstrom":
            # Theoretical
            yHelstrom = (1/5)*( -2*(1/2*(1+np.sqrt(1-c**2)))**4 +
                                 5*(1/2*(1+np.sqrt(1-c**2)))**3 + 
                                 2*(1/2*(1+np.sqrt(1-c**2)))**2 ) 
            plt.plot(c,yHelstrom,label='Helstrom (theoretical)', color=COLOR_HELSTROM)

            # Experimental
            fExperimentalData="data/CHelstrom-%d-%d-global0.csv" % (totC, totIterations)
            assertFileExists(fExperimentalData)
            dExperimental = np.genfromtxt(fExperimentalData, delimiter=",", names=["x", "y"])
            plt.scatter(dExperimental['x'], dExperimental['y'],label='Helstrom (experimental)', color=COLOR_HELSTROM)
        elif strategy=="Bayesian":
            # Not good results to be shown :-(
            # --- # Theory 
            # --- # In this case we don't have an analytical formula but serie of data
            # --- fTheoreticalData="data/CBayesianTheory-%d-0-global0.csv" % (totC)
            # --- dTheoretical=np.genfromtxt(fTheoreticalData,delimiter=",", names=["x", "y"])
            # --- # plt.scatter(dBayesianTheory['x'], dBayesianTheory['y'], label='Bayesian (theory)', color=COLOR_BAYESIAN)
            # --- # Interpolate
            # --- a_BSpline = interpolate.make_interp_spline(dTheoretical['x'], dTheoretical['y'])
            # --- plt.plot(c, a_BSpline(c), label='Bayesian (theory)', color=COLOR_BAYESIAN)

            # Experimental
            fExperimentalData="data/CBayesian-%d-%d-global0.csv" % (totC, totIterations)
            assertFileExists(fExperimentalData)
            dExperimental = np.genfromtxt(fExperimentalData, delimiter=",", names=["x", "y"])
            plt.scatter(dExperimental['x'], dExperimental['y'], label='Bayesian (experimental)',  color=COLOR_BAYESIAN)
        elif strategy=="SRM":
            pass
            # Theory 
            fTheoreticalData="data/CSquareRoot-%d-0-global0.csv"    % (totC)
            dTheoretical=np.genfromtxt(fTheoreticalData,delimiter=",", names=["x", "y"])
            # plt.scatter(dSquareRoot['x'], dSquareRoot['y'], label='Square Root Measurement', color=CYAN)
            # Interporlate
            a_BSpline = interpolate.make_interp_spline(dTheoretical['x'], dTheoretical['y'])
            plt.plot(c, a_BSpline(c), label='Square Root Measurement',color=COLOR_SQUARE_RM)
        else:
            raise Exception("Unknown sttategy '%s'" % (strategy))
        
        
    
    plt.title(title)
    
    plt.xlabel('c')
    plt.ylabel('Probability')
    
    plt.grid(alpha=.4,linestyle='--')
    
    plt.legend()
    
    plt.savefig(fImage)
    print("Image %s created!" % (fImage))
    plt.show()

def drawBayesian(totC, totIterations):
    fImage="bayesian-theoreticaVSexperimental.png" 
    COLOR_SQUARE_RM=BLACK
    COLOR_BAYESIAN=GREEN
    COLOR_PBL=BLUE
    COLOR_HELSTROM=RED

    # --- Theoretical
    fCSVBayesianTheory="data/CBayesianTheory-%d-0-global0.csv"    % (totC)
    dBayesianTheory=np.genfromtxt(fCSVBayesianTheory,delimiter=",", names=["x", "y"])
    plt.scatter(dBayesianTheory['x'], dBayesianTheory['y'], label='Bayesian (theory)', color=BLACK)
    #-- # Interpolate
    #-- a_BSpline = interpolate.make_interp_spline(dBayesianTheory['x'], dBayesianTheory['y'])
    #-- #y_new = a_BSpline(c)
    #-- plt.plot(c, a_BSpline(c), label='Bayesian (theory)', color=COLOR_BAYESIAN)

    # --- Experimental (data from a CSV)
    fCSVBayesianLocal="data/CBayesian-%d-%d-global0.csv"    % (totC, totIterations)
    assertFileExists(fCSVBayesianLocal)
    dBayesianLocal = np.genfromtxt(fCSVBayesianLocal, delimiter=",", names=["x", "y"])
    plt.scatter(dBayesianLocal['x'],  dBayesianLocal['y'],  label='Bayesian (experimental)',  color=RED)
    
    plt.title('Bayesian : theoretical vs. experimental')
    
    plt.xlabel('c')
    plt.ylabel('Probability')
    
    plt.grid(alpha=.4,linestyle='--')
    
    plt.legend()
    
    plt.savefig(fImage)
    print("Image %s created!" % (fImage))
    plt.show()

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions

    # Required

    # Optional
    parser.add_argument('--lg',    help='Show local / global results for a comma separated list of strategies')
    parser.add_argument('--totC',  default=10, type=int, help='Total of c values')
    parser.add_argument('--tot',   default=10, type=int, help='Total of times every experiment is executed')
    parser.add_argument('--strategies',   default="SRM,PBL,Helstrom,Bayesian", help='Comma separarted line of strategies to be drawn')
    parser.add_argument('--title',   default='Probability of success with several strategies (analytical/experimental)', help='Comma separarted line of strategies to be drawn')

    args = parser.parse_args()

    # Check parameters

    # Run
    if args.lg:
        drawGlobalLocal(args.totC, args.tot, args.lg.split(","))
    else:
        drawStrategies(args.strategies.split(","), args.title, args.totC, args.tot)
        #drawBayesian(args.totC, args.tot)
