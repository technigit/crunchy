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

from core_functions import Parser, isDirective, infoMessage

def identify(): return 'shell'

class my(): pass
def getEnv(): pass
def parseOption(option, parameter): return [False, False]
def reset(): pass

def parseMyDirective(line):
    p = Parser()
    p.parseDirective(line)

def pluginMain(line):
    infoMessage(f"{identify()}: This plugin does not process data.")

def parseLine(line):
    if isDirective(line):
        parseMyDirective(line)
    else:
        pluginMain(line)
