#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Roberto Metere
#
# Wifi scanner module

import sys, os, re
from sets import Set
from WifiNetwork import WifiNetwork

# Platform dependent loading modules
if (os.name == "posix"):
  import iw_parse, subprocess
  
  # for NetworkManager scan
  import dbus

  # Device types
  NM_DEVICE_TYPE_UNKNOWN = 0
  NM_DEVICE_TYPE_ETHERNET = 1
  NM_DEVICE_TYPE_WIFI = 2
  NM_DEVICE_TYPE_UNUSED1 = 3
  NM_DEVICE_TYPE_UNUSED2 = 4
  NM_DEVICE_TYPE_BT = 5
  NM_DEVICE_TYPE_OLPC_MESH = 6
  NM_DEVICE_TYPE_WIMAX = 7
  NM_DEVICE_TYPE_MODEM = 8
  NM_DEVICE_TYPE_INFINIBAND = 9
  NM_DEVICE_TYPE_BOND = 10
  NM_DEVICE_TYPE_VLAN = 11
  NM_DEVICE_TYPE_ADSL = 12
  NM_DEVICE_TYPE_BRIDGE = 13

  # Device states
  NM_DEVICE_STATE_UNKNOWN = 0
  NM_DEVICE_STATE_UNMANAGED = 10
  NM_DEVICE_STATE_UNAVAILABLE = 20
  NM_DEVICE_STATE_DISCONNECTED = 30
  NM_DEVICE_STATE_PREPARE = 40
  NM_DEVICE_STATE_CONFIG = 50
  NM_DEVICE_STATE_NEED_AUTH = 60
  NM_DEVICE_STATE_IP_CONFIG = 70
  NM_DEVICE_STATE_IP_CHECK = 80
  NM_DEVICE_STATE_SECONDARIES = 90
  NM_DEVICE_STATE_ACTIVATED = 100
  NM_DEVICE_STATE_DEACTIVATING = 110
  NM_DEVICE_STATE_FAILED = 120

  #Device security
  NM_802_11_AP_SEC_NONE = 0
  NM_802_11_AP_SEC_PAIR_WEP40 = 1
  NM_802_11_AP_SEC_PAIR_WEP104 = 2
  NM_802_11_AP_SEC_PAIR_TKIP = 4
  NM_802_11_AP_SEC_PAIR_CCMP = 8
  NM_802_11_AP_SEC_GROUP_WEP40 = 16
  NM_802_11_AP_SEC_GROUP_WEP104 = 32
  NM_802_11_AP_SEC_GROUP_TKIP = 64
  NM_802_11_AP_SEC_GROUP_CCMP = 128
  NM_802_11_AP_SEC_KEY_MGMT_PSK = 256
  NM_802_11_AP_SEC_KEY_MGMT_802_1X = 512


class WifiScanResult(object):
  device = "lo"
  hwAddress = "00:00:00:00:00:00"
  wifiNetworks = Set()
  
  def __init__(self):
    return
  
  def setDevice(self, dev):
    self.device = dev
  
  def setHwAddress(self, mac):
    self.hwAddress = mac
  
  def addWifiNetwork(self, network):
    for n in self.wifiNetworks:
      if (n.bssid == network.bssid):
	return
    self.wifiNetworks.add(network)
  
  def clear(self):
    self.wifiNetworks = Set()

class WifiScanner(object):
  scanResults = Set()

  def ssid2str(self, dbusByteArray):
    ssid = ""
    for byte in dbusByteArray:
      ssid = ssid + str(byte)
    return ssid

  def securityCode2str(self, code):
    if (code & NM_802_11_AP_SEC_NONE) == 0:
      return "None" + str(code)
    elif (code & ( \
      NM_802_11_AP_SEC_PAIR_WEP40 \
	| NM_802_11_AP_SEC_PAIR_WEP104 \
	  | NM_802_11_AP_SEC_GROUP_WEP40 \
	    | NM_802_11_AP_SEC_GROUP_WEP104 \
	      )) > 0:
      return "WEP"
    else:
      return "WPA"

  # Wifi scanner for linux systems
  def posixWifiScan(self):

    # Result
    self.scanResults = Set()

    # Get all wireless devices
    try:
      fb = subprocess.check_output(["iwconfig"], shell = True, stderr=subprocess.PIPE)
      
      devs = []
      for l in fb.splitlines():
	dev = re.search('802.11', l)
	if dev is not None:
	  devs = devs + [l.split()[0]]
    except OSError as e:
      print "posixWifiScan error. ", e
      return
    except subprocess.CalledProcessError as e:
      print "posixWifiScan issue. ", e
      return
    
    # Device scan
    if len(devs) > 0:
      # Scan with only the first Wifi device
      # TODO implement scanning from each wireless device found
      interface = devs[0]
      
      try:
	# Get MAC address
	fb = subprocess.check_output(["ifconfig", interface])
	
	hwAddress = None
	for l in fb.splitlines():
	  res = re.search('ether', l)
	  if res is not None:
	    hwAddress = l.split()[1].upper()
	    break
	if hwAddress == None:
	  raise OSError("Unable to find MAC address for device " + interface)
	
	# Put interface up
	fb = subprocess.check_output(["ifconfig", interface, "up"])
	
	# Scan!
	fb = subprocess.check_output(["iwlist", interface, "scanning"])
      except OSError as e:
	print "posixWifiScan scan error. ", e
	return
      except subprocess.CalledProcessError as e:
	print "posixWifiScan scan issue. ", e
	return
	
      wifiScanResult = WifiScanResult()
      wifiScanResult.setDevice(interface)
      wifiScanResult.setHwAddress(hwAddress)
      
      # Read information from cells and add network
      for cell in iw_parse.get_parsed_cells(fb):
	wnet = WifiNetwork()
	wnet.setSSID(cell["Name"])
	wnet.setBSSID(cell["Address"])
	wnet.setSecurity(cell["Encryption"])
	wnet.setChannel(cell["Channel"])
	wnet.setDiscoveredBy(wifiScanResult.hwAddress)
	wifiScanResult.addWifiNetwork(wnet)
      
      self.scanResults.add(wifiScanResult)

  # Wifi scanner for linux systems with NetworkManager active
  def posixWifiScanNetworkManager(self):
    # Result
    self.scanResults = Set()

    # Get network devices
    devices = dbus.Interface( \
      dbus.SystemBus().get_object( \
	"org.freedesktop.NetworkManager", \
	  "/org/freedesktop/NetworkManager"), \
	"org.freedesktop.NetworkManager").GetDevices()
    for d in devices:
      deviceProxy = dbus.SystemBus().get_object("org.freedesktop.NetworkManager", d)
      interfaceProperties = dbus.Interface(deviceProxy, "org.freedesktop.DBus.Properties")

      # Get interface specs
      interface = str(interfaceProperties.Get("org.freedesktop.NetworkManager.Device", "Interface"))
      dtype = interfaceProperties.Get("org.freedesktop.NetworkManager.Device", "DeviceType")
      state = interfaceProperties.Get("org.freedesktop.NetworkManager.Device", "State")

      # Make sure the device is enabled before we try to use it
      if (state != NM_DEVICE_STATE_DISCONNECTED) and (state != NM_DEVICE_STATE_ACTIVATED):
	continue

      # Scan
      if dtype == NM_DEVICE_TYPE_WIFI:   # WiFi
	wifiScanResult = WifiScanResult()
	wifiScanResult.setDevice(interface)
	wifiScanResult.setHwAddress(str(interfaceProperties.Get("org.freedesktop.NetworkManager.Device.Wireless", "HwAddress")))
	
	# Get all APs the card can see
	aps = dbus.Interface(deviceProxy, "org.freedesktop.NetworkManager.Device.Wireless").GetAccessPoints()
	for path in aps:
	  #ap_proxy =
	  apProperties = dbus.Interface( \
	    dbus.SystemBus().get_object("org.freedesktop.NetworkManager", path), \
	      "org.freedesktop.DBus.Properties")
	  bssid = apProperties.Get("org.freedesktop.NetworkManager.AccessPoint", "HwAddress")
	  ssid = apProperties.Get("org.freedesktop.NetworkManager.AccessPoint", "Ssid")
	  sec = apProperties.Get("org.freedesktop.NetworkManager.AccessPoint", "WpaFlags")

	  # Add network
	  wnet = WifiNetwork()
	  wnet.setSSID(self.ssid2str(ssid))
	  wnet.setBSSID(str(bssid))
	  wnet.setSecurity(self.securityCode2str(sec))
	  wnet.setDiscoveredBy(wifiScanResult.hwAddress)
	  wifiScanResult.addWifiNetwork(wnet)
	
	self.scanResults.add(wifiScanResult)

  # Cross platform scanner
  def scan(self):
    scanners = { "posix" : self.posixWifiScan }
    try:
      scanners[os.name]()
    except KeyError:
      print >>sys.stderr, "Error. Operating system not supported."
      sys.exit(2)

  def shellPrint(self):
    if (len(self.scanResults) > 0):
      for dev in self.scanResults:
	print "Access points for device", dev.device, "(" + dev.hwAddress + "):"
	for ap in dev.wifiNetworks:
	  print "\t" + ap.ssid,"(" + ap.bssid + " - " + ap.channel + ") - " + ap.security
    else:
      print "No access points found or wireless devices missing.\n"
	
  def getWifiNetworkBySSID(self, name):
    for dev in self.scanResults:
      for ap in dev.wifiNetworks:
	if (ap.ssid == name):
	  return ap
    return None
  
# Run the application
def main():
  ws = WifiScanner()
  ws.scan()
  ws.shellPrint()

if __name__ == '__main__':
    main()