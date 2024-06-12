#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Bridge connection to plugins
#
################################################################################

import importlib, traceback

def placeholder(_none = None, none_ = None):
    print('placeholder')

class plugin():
    getEnv = placeholder
    identify = placeholder
    parseLine = placeholder
    parseOption = placeholder
    reset = placeholder
    my = placeholder

def usePlugin(plugin_name):
    try:
        p = importlib.import_module('plugins.{0}'.format(plugin_name))
        plugin.getEnv = p.getEnv
        plugin.identify = p.identify
        plugin.parseLine = p.parseLine
        plugin.parseOption = p.parseOption
        plugin.reset = p.reset
        plugin.my = p.my
        plugin.reset()
    except AttributeError:
        print('Bridge: Incomplete plugin implementation.  Check that all attributes are implemented.')
        exit()
    except ModuleNotFoundError:
        raise ModuleNotFoundError
    except:
        traceback.print_exc()
