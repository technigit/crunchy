#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Shell plugin
#
################################################################################

from core_functions import Parser, isDirective, infoMessage, errorMessage

def identify(): return 'shell'

class my(): pass
def getEnv(): pass
def parseOption(option, parameter): return [False, False]
def reset(): pass

def parseLine(line):
    if isDirective(line):
        p = Parser()
        p.preParseDirective(line)
        if not p.done:
            errorMessage('Invalid directive: {0}'.format(line))
    else:
        infoMessage('Shell: This plugin does not process data.')
