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

import fileinput, re, traceback

import core
core.main.version_ = 'v0.0.21'

from core_functions import showInfo, parseOptions, skipLine, errorMessage

# abstraction layer for plugins
import bridge

################################################################################
# send data to the plugin for processing
################################################################################

def processData():
    should_stop = True
    try:
        with fileinput.FileInput(files=(filenames), mode='r') as input:
            for line in input:
                line = re.sub('\n', '', line)
                if not skipLine(line): bridge.plugin.parseLine(line)
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
bridge.usePlugin('shell')

# show information when starting in interactive mode
showInfo()

# process command-line options
filenames = parseOptions()

# main parsing loop
while core.main.running_[-1]:
    processData()
    if not core.main.interactive_:
        break

# gracefully handle uncompleted goto directives
if core.main.goto_[-1]:
    errorMessage("EOF reached before tag '{0}'.".format(core.main.goto_[-1]))
