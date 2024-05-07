#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Main processing module
#
################################################################################

version_ = 'v0.0.15'

import fileinput, re, sys, traceback

################################################################################
# primary logic
################################################################################

import core
from core_functions import parseOptions, printLine, skipLine, errorMessage

################################################################################
# abstraction layer for plugins
################################################################################

import bridge

################################################################################
# internal environment value(s)
################################################################################

# interactive mode affects UX for error handling
interactive_ = False

################################################################################
# show utility information in interactive mode
################################################################################

def show_info(should_show = False):
    global interactive_
    if should_show or (len(sys.argv) == 1 and sys.stdin.isatty()):
        interactive_ = True
        printLine("""
Crunchy Report Generator aka Crunch Really Useful Numbers Coded Hackishly
{0}

To get help, enter &help
To exit interactive mode, use Ctrl-D
""".format(version_))

################################################################################
# send data to the module for processing
################################################################################

def processData():
    should_stop = True
    try:
        with fileinput.FileInput(files=(filenames), mode='r') as input:
            for line in input:
                line = re.sub('\n', '', line)
                if not skipLine(line): bridge.parseLine(line)
                if not core.main.running_[-1]: break
    except FileNotFoundError as e:
        errorMessage('Input file not found: {0}'.format(e.filename))
    except IndexError:
        errorMessage('Badly formed data: {0}'.format(line))
        should_stop = False
    except ValueError:
        errorMessage('Invalid input: {0}'.format(line))
        should_stop = False
    except KeyboardInterrupt:
        errorMessage('Interrupted.')
    except:
        errorMessage('Unexpected error.')
        traceback.print_exc()
    finally:
        fileinput.close()
        if core.testing.testing_[-1]:
            core.testing.testStop()
    if should_stop:
        core.main.running_[-1] = False

####################
# start here
####################

# initialize all environments
core.reset()
core.testing.reset()
bridge.reset()

# show information when starting in interactive mode
show_info()

# process command-line options
filenames = parseOptions()

# main parsing loop
while core.main.running_[-1]:
    processData()
    if not interactive_:
        break

# gracefully handle uncompleted goto directives
if core.main.goto_[-1]:
    errorMessage("EOF reached before tag '{0}'.".format(core.main.goto_[-1]))
