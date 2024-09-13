#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Bridge connection to plugins
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import importlib
import traceback

def placeholder(place = '', holder = ''):
    return f"{place}{holder}"

class Plugin():
    getEnv = placeholder
    identify = placeholder
    parseLine = placeholder
    parse_option = placeholder
    reset = placeholder
    my = placeholder

def use_plugin(plugin_name):
    try:
        p = importlib.import_module(f"plugins.{plugin_name}")
        Plugin.getEnv = p.get_env
        Plugin.identify = p.identify
        Plugin.parseLine = p.parse_line
        Plugin.parseOption = p.parse_option
        Plugin.reset = p.reset
        Plugin.my = p.My
        Plugin.reset()
    except AttributeError as e:
        raise AttributeError from e
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError from e
    except: # pylint: disable=bare-except
        traceback.print_exc()
