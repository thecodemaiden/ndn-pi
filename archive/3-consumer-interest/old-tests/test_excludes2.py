# Copyright (C) 2014 Regents of the University of California.
# Author: Spencer Sutterlin <ssutterlin1@ucla.edu>
# 
# This file is part of ndn-pi (Named Data Networking - Pi).
#
# ndn-pi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# A copy of the GNU General Public License is in the file COPYING.

import time
from pyndn import Name
from pyndn import Face
from pyndn import Interest
from pyndn import Exclude

import json

response = False
timeout = False
exclude = Exclude()
face = Face("localhost")

def onData(interest, data):
    global response
    response = True
    print "Interest:", interest.getName().toUri(),
    print "Data:", data.getName().toUri(),
    print "Content:", data.getContent().toRawStr()
    print "Excluding:", data.getName().get(3).toEscapedString()
    exclude.appendComponent(data.getName().get(3))

def onTimeout(interest):
    global response
    response = True
    global timeout
    timeout = True
    print "Timeout:", interest.getName().toUri()

while not timeout:
    interest = Interest(Name("/home/pir/00000000d1f2533912"))
    interest.setExclude(exclude)
    print "Interest:", interest.getName().toUri()
    print "\tExcludes:", interest.getExclude().toUri()
    face.expressInterest(interest, onData, onTimeout)

    while not response:
        face.processEvents()
        time.sleep(0.5)
