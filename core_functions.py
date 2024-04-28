#!/usr/bin/env python3

import re, sys
from os.path import exists

import core

def ljustify(str, width):
    return str.ljust(width)[:width]

def cjustify(str, width):
    return str.center(width)[:width]

def rjustify(str, width):
    return str.rjust(width)[:width]

def currency(num):
    return '${:,.2f}'.format(num)

def infoMessage(message):
    if core.main.infomsg_[-1] and core.main.output_[-1]: printLine('<i> ' + message)

def errorMessage(message):
    printLine(core.ANSI.FG_RED + '<E> ' + message + core.ANSI.FG_DEFAULT, sys.stderr)

def printLine(line = '', stdio=sys.stdout):
    if core.testing.testing_[-1]:
        try:
            if core.testing.test_f_[-1] == None:
                read_source = core.testing.test_filename_[-1]
                if core.main.read_path_[-1]:
                    read_source = core.main.read_path_[-1] + '/' + core.testing.test_filename_[-1]
                if exists(read_source):
                    core.testing.test_f_[-1] = open(read_source, 'r')
                else:
                    core.testing.testMessage("File '{0}' does not exist; stopping test.".format(read_source), True)
                    core.testing.testStop(True)
            if core.testing.test_f_[-1] != None:
                line = re.sub('\n', '', line)
                test_line = core.testing.test_f_[-1].readline()
                if test_line != '':
                    test_line = re.sub('\n', '', test_line)
                    if line == test_line:
                        core.testing.testMessage('Passed: ' + line)
                        core.testing.test_pass_[-1] += 1
                    else:
                        core.testing.testMessage("Expected: '{0}'".format(test_line), True)
                        core.testing.testMessage("Received: '{0}'".format(line), True)
                        core.testing.test_fail_[-1] += 1
                else:
                    core.testing.testMessage('Unexpected EOF reached; stopping test.', True)
                    core.testing.testStop(True)
        except:
            core.testing.testMessage('Unexpected error: ' + line, True)
            traceback.print_exc()
    if not core.testing.testing_[-1]:
        print(line, file=stdio)
