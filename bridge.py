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
    parseLine = placeholder
    parseOption = placeholder
    reset = placeholder
    my = placeholder

def usePlugin(plugin_name):
    try:
        p = importlib.import_module('plugins.%s' % plugin_name)
        plugin.getEnv = p.getEnv
        plugin.parseLine = p.parseLine
        plugin.parseOption = p.parseOption
        plugin.reset = p.reset
        plugin.my = p.my
        plugin.reset()
    except ModuleNotFoundError:
        raise ModuleNotFoundError
    except:
        traceback.print_exc()
