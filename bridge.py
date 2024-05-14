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

import plugins.banking

getEnv = plugins.banking.getEnv
parseLine = plugins.banking.parseLine
parseOption = plugins.banking.parseOption
reset = plugins.banking.reset
my = plugins.banking.my
