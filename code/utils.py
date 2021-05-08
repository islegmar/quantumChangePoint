# -*- coding: utf-8 -*-
""" Utilities. """

import argparse

# -----------------------------------------------------------------------------
# Global variables
# -----------------------------------------------------------------------------
LOG_LEVEL_NO = 0
LOG_LEVEL_INFO = 10
LOG_LEVEL_DEBUG = 20
LOG_LEVEL_LOW_DEBUG = 30
CURR_LOG_LEVEL = LOG_LEVEL_INFO

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def trace(logLevel, line):
    """ Trace function. """

    if logLevel <= CURR_LOG_LEVEL:
        print (line)

def printLevel():
    print("Level : %d" % (CURR_LOG_LEVEL))

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    trace(LOG_LEVEL_DEBUG, "Do not see this line")
    CURR_LOG_LEVEL = LOG_LEVEL_DEBUG
    trace(LOG_LEVEL_DEBUG, "See this line")
