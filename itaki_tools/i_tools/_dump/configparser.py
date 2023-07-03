import sys, math, os
import nuke,nukescripts
import Qt
from Qt import QtGui
from Qt import QtCore
from Qt.QtGui import *
from Qt.QtCore import *
from nukescripts import panels
import datetime
import operator

import configparser
PresetsFile = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'presets/GradientPresets.cfg')

config = configparser.ConfigParser()
# config.read(PresetsFile)