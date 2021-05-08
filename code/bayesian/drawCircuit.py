import argparse
import base64
import helstrom
import math
from MyCPVM import CPVM

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions

    # Required

    # Optional
    parser.add_argument('--pPsi',   default=0.5, type=float, help='<Help>')
    parser.add_argument('--pPhi',   default=0.5, type=float, help='<Help>')
    parser.add_argument('--theta',  default=math.pi/8, type=float, help='<Help>')
    parser.add_argument('--file',   default="circtuit.png", help='<Help>')

    args = parser.parse_args()

    # Check parameters

    # Run
    V_Psi, V_Phi = helstrom.getPVM(args.pPsi, args.pPhi, args.theta)
    oCPVM=CPVM([V_Psi, V_Phi])
    result, circuit = oCPVM.measure([math.cos(args.theta), math.sin(args.theta)])
    circuit.draw(output='mpl', filename=args.file)
    print ("File %s created!" % (args.file))

    data = open(args.file, "r").read()
    encoded = base64.b64encode(data)
    print (encoded)
