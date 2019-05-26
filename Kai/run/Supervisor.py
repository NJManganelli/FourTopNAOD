from __future__ import print_function, division

import os
import sys
import time
import argparse
import subprocess
from collections import OrderedDict
from ruamel.yaml import YAML

parser = argparse.ArgumentParser(description='Supervisor handles submission and bookkeeping for physics samples.')
parser.add_argument('--check_events', dest='check_events', action='store_true',
                    help='check that the number of events in source files match those in the sample card')
parser.add_argument('--sample_card', dest='sample_cards', action='append', type=str,
                    help='path and name of the sample card(s) to be used')

args = parser.parse_args()
# args = parser.parse_args('--check_events --sample_card sampletest.yml'.split())
print("Supervisor will check integrity of sample card's event counts: " + str(args.check_events))
print("The path and name of the sample cards(s) are: ")
SampleList = []
yaml = YAML() #default roundtrip type
for scard in args.sample_cards:
    print("\t" + scard)
    with open(scard) as sample:
        SampleList += yaml.load(sample)
print(SampleList)
# result = subprocess.check_output(["ls", "-ltr"], shell=False)
# print(result)





