#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Testing functions
#
################################################################################

import core, bridge
from core_functions import rjustify

def reset():
    core.testing.testing_ = [False]
    core.testing.test_filename_ = [None]
    core.testing.test_f_ = [None]
    core.testing.test_pause_ = [False]
    core.testing.test_verbose_ = [False]
    core.testing.test_pass_ = [0]
    core.testing.test_fail_ = [0]

def testMessage(message, verbose = False):
    if core.testing.test_verbose_[-1] or verbose: print(core.ANSI.FG_YELLOW + '<T> ' + message + core.ANSI.FG_DEFAULT)

def testStop(verbose = False):
    core.testing.testing_[-1] = False
    core.testing.test_pause_[-1] = False
    if core.testing.test_f_[-1] != None:
        eof_test = core.testing.test_f_[-1].readline()
        if eof_test != '':
            testMessage('The test was unexpectedly interrupted.', True)
            while eof_test != '':
                core.testing.test_fail_[-1] += 1
                eof_test = core.testing.test_f_[-1].readline()
        core.testing.test_f_[-1].close()
    core.testing.test_f_[-1] = None
    testMessage('Test stopped.', verbose)
    total = core.testing.test_pass_[-1] + core.testing.test_fail_[-1]
    s = 's' if total != 1 else ''
    tested = str(total) + ' line' + s + ' tested: '
    if core.testing.test_pass_[-1] > 0:
        passed = core.ANSI.FG_GREEN + str(core.testing.test_pass_[-1]) + ' passed' + core.ANSI.FG_YELLOW + ' :: '
    else:
        passed = str(core.testing.test_pass_[-1]) + ' passed :: '
    if core.testing.test_fail_[-1] > 0:
        failed = core.ANSI.FG_RED + str(core.testing.test_fail_[-1]) + ' failed' + core.ANSI.FG_YELLOW + ' :: '
    else:
        failed = str(core.testing.test_fail_[-1]) + ' failed :: '
    testfile = core.testing.test_filename_[-1]
    text_offset = 0 if total < 1000 else 2 # make room for big numbers
    testMessage(rjustify(tested, 18 + text_offset) + rjustify(passed, 24 + text_offset) + failed + testfile, True)
    core.testing.test_filename_[-1] = ''

def listVars_(core_class, filters, classname = None):
    if classname == None:
        classname = core_class.__name__
    for var in vars(core_class):
        attr = getattr(core_class, var)
        should_show = filters == [] or var in filters or classname in filters
        if not var.startswith('__') and not callable(attr) and should_show:
            print('{0}.{1} = {2}'.format(classname.rjust(8), var.ljust(21), attr))

def debug(argv):
    if argv != None:
        filters = argv.split()
    else:
        filters = []
    listVars_(core.main, filters)
    listVars_(core.cli, filters)
    listVars_(core.testing, filters)
    listVars_(bridge.plugin.my, filters, 'plugin')
