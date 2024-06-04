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
from core_functions import preParse, mapElements
from core_functions import Parser
from core_functions import isDirective
from core_functions import printLine
from core_functions import infoMessage, errorMessage

def identify(): return 'example'

class my():
    sums_ = []
    rows_ = None

def reset():
    my.sums_ = [[]]
    my.rows_ = 0

class cli():
    example_option = True

reset()

def getEnv():
    return [
        my.sums_
    ]

################################################################################
# parse plugin-specific directives, but pre-parse for core directives first
################################################################################

def parseMyDirective(line):
    p = Parser()
    p.preParseDirective(line)
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

    elif cmd == 'stats':
        if argtrim:
            if argtrim == 'sums':
                printLine(mapElements(my.sums_[-1]))
            elif argtrim == 'averages':
                averages = []
                for sum in my.sums_[-1]:
                    averages.append('{0:8.3f}'.format(sum/my.rows_))
                printLine(mapElements(averages))
        else:
            infoMessage('Usage: &stats <type>')

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

def pluginMain(out):
    linesum = 0
    for i, element in enumerate(core.main.elements_):
        if len(my.sums_[-1]) >= i + 1:
            my.sums_[-1][i] += int(element)
        else:
            my.sums_[-1].append(int(element))
        linesum += int(element)
    printLine('{0} {1:8.0f} {2:8.3f}'.format(out, linesum, linesum / len(core.main.elements_)))
    my.rows_ += 1

####################
# start here
####################

def parseLine(line):
    if isDirective(line):
        parseMyDirective(line)
    else:
        out = preParse(line)
        if core.main.output_[-1]:
            if core.main.header_mode_:
                printLine('{0}'.format(out))
            else:
                pluginMain(out)
        core.main.header_mode_ = False
