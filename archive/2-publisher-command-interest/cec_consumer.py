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
from pyndn import Data
from pyndn import Face
from pyndn import Interest
from pyndn.security import KeyChain

import json
import subprocess

class Echo(object):
    def __init__(self, face, keyChain, certificateName):
        self._face = face
        self._keyChain = keyChain
        self._certificateName = certificateName
        self._responseCount = 0

    def run(self, prefix):
        self._face.registerPrefix(prefix, self.onInterest, self.onRegisterFailed)
        # while self._responseCount < 2:
        while True:
            self._face.processEvents()
            time.sleep(0.01)

    def onInterest(self, prefix, interest, transport, registeredPrefixId):
        self._responseCount += 1
        commandInterest = interest # for naming clarity, since we respond to interest with interest
        print "Received Command Interest:", commandInterest.getName().toUri()

        # TODO: Verify command interests legitimacy

        # Respond to interest with data ack
        data = Data(interest.getName())
        data.setContent("ACK")
        self._keyChain.sign(data, self._certificateName)
        encodedData = data.wireEncode()
        transport.send(encodedData.toBuffer())
        print "Sent Data:", data.getName().toUri(), "with content:", "ACK"

        # Send interest requesting data
        responseInterest = Interest(Name(commandInterest.getName().getSubName(4)))
        responseInterest.setInterestLifetimeMilliseconds(3000)
        self._face.expressInterest(responseInterest, self.onData, self.onTimeout)
        print "Sent Interest:", responseInterest.getName().toUri()

    def onRegisterFailed(self, prefix):
        raise RegisterPrefixError('Register prefix failed')

    def onData(self, interest, data):
        self._responseCount += 1
        content = data.getContent().toRawStr()
        print "Received Data:", data.getName().toUri(), "with content:", content
        d = json.loads(content)
        pirVal = d["pir"]

        # TODO: Verify data packet's legitimacy

        # TODO: refactor
        # TODO: Don't hardcode "0" (tv's logical address)
        if pirVal:
            proc = subprocess.Popen(["cec-client", "-s", "-d", "1"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            (out, err) = proc.communicate(input="as")
            time.sleep(2.25)
            subprocess.check_call(["omxplayer", "-o", "hdmi", "/home/pi/YOUSHALLNOTPASS.mp4"])
            proc = subprocess.Popen(["cec-client", "-s", "-d", "1"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            (out, err) = proc.communicate(input="standby 0")
        else:
            pass # you shall pass

    def onTimeout(self, interest):
        self._responseCount += 1
        print "Interest:", interest.getName().toUri(), "timed out"

if __name__ == "__main__":
    face = Face("localhost")
    keyChain = KeyChain()
    face.setCommandSigningInfo(keyChain, keyChain.getDefaultCertificateName())
    echo = Echo(face, keyChain, keyChain.getDefaultCertificateName())

    prefix = Name("/home/all/command")
    print "Register prefix", prefix.toUri()
    echo.run(prefix)

    face.shutdown()

