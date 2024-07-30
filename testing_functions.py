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

def listVars_(class_obj, filters, fullname = False, classname = None):
    # 'testing' is the longest built-in class name
    class_width = 7

    # 'line_parse_delimiter' is usually the longest variable name
    var_width = 21

    if classname == None:
        classname = class_obj.__name__
    if fullname:
        classname = '{0}.{1}'.format(class_obj.__module__, class_obj.__name__)

        # 'core.testing' is the longest built-in full class name
        class_width = 12

        # the plugin class full name tends to be the longest
        plugin_classname = '{0}.{1}'.format(bridge.plugin.my.__module__, bridge.plugin.my.__name__)
        if len(plugin_classname) > len(classname):
            class_width = len(plugin_classname)

    class_vars = vars(class_obj)

    # check for partial matches
    partial_matches = []
    for filter in filters:
        p = [cv for cv in class_vars if filter in cv]
        partial_matches.extend(p)
    filters.extend(partial_matches)

    # check for class or variable matches
    for var in class_vars:
        attr = getattr(class_obj, var)

        # we only want our own variables
        if not var.startswith('__') and not callable(attr):

            # finally check for matches
            if filters == [] or var in filters or classname in filters:

                # prettier name
                if var.endswith('_') and not fullname:
                    var = var[:-1]

                # passed the filters
                print('  {0}.{1} = {2}'.format(classname.rjust(class_width), var.ljust(var_width), attr))

def debug(argv, fullname = False):
    if argv != None:
        filters = argv.split()
    else:
        filters = []
    listVars_(core.main, filters, fullname)
    listVars_(core.cli, filters, fullname)
    listVars_(core.testing, filters, fullname)
    listVars_(bridge.plugin.my, filters, fullname, 'plugin')
