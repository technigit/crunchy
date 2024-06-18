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

import fileinput, re, readline, traceback

import core
core.main.version_ = 'v0.0.23'

from core_functions import checkInteractivity, showInfo, parseOptions, skipLine, errorMessage

# abstraction layer for plugins
import bridge

################################################################################
# send data to the plugin for processing
################################################################################

def processData():
    should_stop = True
    try:
        if core.main.interactive_:
            line = input(core.main.interactive_prompt_)
            if not skipLine(line): bridge.plugin.parseLine(line)
            should_stop = False
        else:
            with fileinput.FileInput(files=(filenames), mode='r') as lines:
                for line in lines:
                    line = re.sub('\n', '', line)
                    if not skipLine(line): bridge.plugin.parseLine(line)
                    if not core.main.running_[-1]: break
    except EOFError:
        print()
        should_stop = True
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

# process command-line options
filenames = parseOptions()

# show information when starting in interactive mode
core.main.interactive_ = checkInteractivity(filenames)
showInfo()

# main parsing loop
while core.main.running_[-1]:
    processData()
    if not core.main.interactive_:
        break

# gracefully handle uncompleted goto directives
if core.main.goto_[-1]:
    errorMessage("EOF reached before tag '{0}'.".format(core.main.goto_[-1]))
