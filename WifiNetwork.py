#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Roberto Metere
#
# WifiNetwork class

class WifiNetwork(object):
  ssid = ""
  bssid = "00:00:00:00:00:00"
  discoveredBy = "00:00:00:00:00:00"
  security = "None"
  channel = 11
  quality = 0
  
  def __init__ (self):
    return
  
  def __eq__ (self, other):
    if type(self) != type(other):
      return False
    return (self.bssid == other.bssid)
  
  def __hash__ (self):
    return hash(str(self.bssid))
  
  def setSSID(self, name):
    self.ssid = name
  
  def setBSSID(self, mac):
    self.bssid = mac
  
  def setSecurity(self, sec):
    self.security = sec
  
  def setDiscoveredBy(self, discoveredBy):
    self.discoveredBy = discoveredBy
  
  def setQuality(self, quality):
    self.quality = quality
  
  def setChannel(self, channel):
    self.channel = channel