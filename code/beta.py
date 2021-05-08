# -*- coding: utf-8 -*-
""" Template script """

import argparse

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def trace(line):
    """ Trace function. """
    print (line)

# -----------------------------------------------------------------------------
# Methods
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<Help here>")

    # Actions
    # parser.add_argument('--action', action="store_true", help='<Help>')

    # Required

    # Optional
    # parser.add_argument('--data',  default='', help='<Help>')

    args = parser.parse_args()

    # Check parameters
