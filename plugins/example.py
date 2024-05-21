#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Example plugin
#
################################################################################

import core
from core_functions import preParseLine
from core_functions import Parser
from core_functions import isDirective
from core_functions import printLine
from core_functions import infoMessage, errorMessage

class my():
    var_ = []

def reset():
    my.var_ = [None]

class cli():
    example_option = True

reset()

def getEnv():
    return [
        my.var_
    ]

################################################################################
# parse plugin-specific directives, but pre-parse for core directives first
################################################################################

def parseDirective(line):
    p = Parser()
    p.preParseDirective(line, parseLine)
    if p.done:
        return
    arg = p.arg
    argtrim = p.argtrim
    cmd = p.cmd
    options = p.options

    ####################

    if cmd == 'example':
        if argtrim:
            infoMessage('This is an example directive output acting on "{0}"'.format(argtrim))
        else:
            infoMessage('Usage: &example <text>')

    ####################

    else:
        errorMessage('Invalid directive: {0}'.format(line))

################################################################################
# add command-line options just for this plugin
################################################################################

def parseOption(option, parameter):
    # result[0] = known/unknown
    # result[1] = skip next word (option parameter)
    result = [False, False]
    if parameter == None:
        parameter = ''
    if option in ['-eo', '--example-option']:
        infoMessage('This is an example option output with no parameters.')
        result = [True, False]
    elif option in ['-eop', '--example-option-parameter']:
        infoMessage('This is an example option output with a parameter: {0}'.format(parameter))
        result = [True, True]
    return result

################################################################################
# plugin-specific parsing
################################################################################

def parseLine(line):
    if isDirective(line):
        parseDirective(line)
    else:
        out = preParseLine(line)
        if core.main.output_[-1]:
            if core.main.header_mode_:
                printLine('{0}'.format(out))
            else:
                printLine('{0}'.format(out))
        core.main.header_mode_ = False
