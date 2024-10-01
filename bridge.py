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
    get_env = placeholder
    identify = placeholder
    parse_line = placeholder
    parse_option = placeholder
    reset = placeholder
    my = placeholder

def use_plugin(plugin_name):
    try:
        p = importlib.import_module(f"plugins.{plugin_name}")
        Plugin.get_env = p.get_env
        Plugin.identify = p.identify
        Plugin.parse_line = p.parse_line
        Plugin.parse_option = p.parse_option
        Plugin.reset = p.reset
        Plugin.my = p.My
        Plugin.reset()
    except AttributeError as e:
        raise AttributeError from e
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError from e
    except ImportError:
        pass
    except: # pylint: disable=bare-except
        traceback.print_exc()
