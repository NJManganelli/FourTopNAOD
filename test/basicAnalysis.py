#Try to make this Python 2.7/3.6 safe...
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
import os, sys
import ROOT
#ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module

from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
