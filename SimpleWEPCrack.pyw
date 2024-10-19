#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Roberto Metere
#
# Simple WEP Crack

# Imports
from threading import Thread
import sys, os, time, re, PyQt4
from PyQt4 import QtCore, QtGui, QtNetwork
from AboutBox_rc import *
from Ui_AboutBox import Ui_AboutBox
from WifiScanner import WifiScanner
from WifiNetwork import WifiNetwork
import Aircrack
from Aircrack import AircrackNG
from AircrackGuiProcess import AircrackGuiProcess
import gettext
gettext.bindtextdomain("messages", "lang")
gettext.textdomain("messages")

def changeLanguage(lang):
  lang = gettext.translation('messages', localedir = 'lang', languages = [lang], fallback = True)
  _ = lang.ugettext
  lang.install()

def isDirectoryEmpty(checkDir):
  if os.path.exists(checkDir) and not os.path.isfile(checkDir):
    return os.listdir(checkDir) == []
  return False

def printNow(string):
  print(string, flush=True)

# Simple WEP Crack
class SimpleWEPCrack (QtGui.QApplication):
  aboutBox = None
  messageBox = None
  systemTrayIcon = None
  trayMenu = None
  wifiScanner = None
  currentNetwork = None
  actions = {}
  icon = None
  widget = None
  aircrack = None
  monitorDevices = []
  processes = { "dump": None, "replay": {}, "crack": None }
  autoMode = False
  animIcon = None
  animating = False

  # Application
  def __init__(self, arguments):
    super(SimpleWEPCrack, self).__init__(arguments)
    
    # Application
    self.setQuitOnLastWindowClosed(False)
    self.icon = QtGui.QIcon(QtGui.QPixmap('res/swepc_gray.png'))
    self.iconNoMon = QtGui.QIcon(QtGui.QPixmap('res/swepc_yellow.png'))
    self.iconOperative = QtGui.QIcon(QtGui.QPixmap('res/swepc_green.png'))
    self.iconBusy = QtGui.QIcon(QtGui.QPixmap('res/swepc_red.png'))
    self.iconCrackingAnim = [
      QtGui.QIcon(QtGui.QPixmap('res/swepc_red_0.png')),
      QtGui.QIcon(QtGui.QPixmap('res/swepc_red_1.png')),
      QtGui.QIcon(QtGui.QPixmap('res/swepc_red_2.png')),
      QtGui.QIcon(QtGui.QPixmap('res/swepc_red_3.png')),
      QtGui.QIcon(QtGui.QPixmap('res/swepc_red_4.png'))
      ]
    
    # As first, check for permissions
    self.enoughPrivileges()
    
    # Parent widget
    self.widget = QtGui.QWidget()
    self.applyCommonWidgetProperties(self.widget)
    
    # Wifi stuff
    self.wifiScanner = WifiScanner()
    self.currentNetwork = WifiNetwork()
    self.aircrack = AircrackNG()
    self.monitorDevices = self.aircrack.mon.detect()
    
    # Initialize about box
    self.aboutBox = QtGui.QDialog()
    Ui_AboutBox().setupUi(self.aboutBox)
    
    # Tray icon
    self.systemTrayIcon = QtGui.QSystemTrayIcon()
    self.systemTrayIcon.setIcon(self.icon)
    
    # Tray menu
    self.trayMenu = QtGui.QMenu()
    self.actions["wep"] = self.trayMenu.addAction(_("Find network..."), self.chooseNetwork)
    self.actions["autocrack"] = self.trayMenu.addAction(_("Auto-crack..."), self.crackNetwork)
    self.actions["dir"] = self.trayMenu.addAction(_("Aircrack directory..."), self.chooseAircrackBinDirs)
    self.trayMenu.addSeparator()
    self.actions["check"] = self.trayMenu.addAction(_("Solve conflicts"), self.killConflictingPrograms)
    self.actions["startmon"] = self.trayMenu.addAction(_("Start monitor..."), self.startMonitor)
    self.actions["inj"] = self.trayMenu.addAction(_("Test monitor"), self.testMonitor)
    self.actions["stopmon"] = self.trayMenu.addAction(_("Remove monitors"), self.stopMonitors)
    self.trayMenu.addSeparator()
    self.actions["dump"] = self.trayMenu.addAction(_("Gain data"), self.dump)
    self.actions["fauth"] = self.trayMenu.addAction(_("Fake authentication"), self.fakeauth)
    self.actions["arpinj"] = self.trayMenu.addAction(_("ARP Replay"), self.arpReplay)
    self.actions["crack"] = self.trayMenu.addAction(_("Crack!!"), self.crackPassword)
    self.trayMenu.addSeparator()
    self.actions["about"] = self.trayMenu.addAction(_("Credits"), self.aboutBox.exec_)
    self.actions["exit"] = self.trayMenu.addAction(_("Exit"), self.quitProgram)
    self.setStatusNoNetStatus()
    
    # Set menu to tray icon and show
    self.systemTrayIcon.setContextMenu(self.trayMenu)
    self.systemTrayIcon.show()
    
  def setIcon(self, icon = None):
    if icon is None:
      self.systemTrayIcon.setIcon(self.icon)
    else:
      self.systemTrayIcon.setIcon(icon)
      
  def animateIconThread(self, iconList):
    self.animating = True
    i = 0;
    while self.animating:
      i = (i + 1) % (len(iconList))
      self.setIcon(iconList[i])
      time.sleep(1)
  
  def animateCrackingIcon(self, animate = True):
    self.animateIcon(self.iconCrackingAnim, animate)
    
  def animateIcon(self, iconList = None, animate = True):
    if self.animIcon is not None:
      self.animating = False
      self.animIcon.join()
      self.animIcon = None
    if animate and iconList is not None:
      self.animIcon = Thread(target = self.animateIconThread, args = (iconList, ))
      self.animIcon.start()
    else:
      self.animating = False

  def applyCommonWidgetProperties(self, widget):
    widget.setWindowIcon(self.icon)
    widget.setWindowTitle("Simple WEP Crack")
        
  def showModalText(self, text, modal = True, buttons = QtGui.QMessageBox.Close):
    if not self.autoMode:
      messageBox = QtGui.QMessageBox()
      self.applyCommonWidgetProperties(messageBox)
      messageBox.setIcon(QtGui.QMessageBox.Information)
      messageBox.setStandardButtons(buttons)
      messageBox.setText(text)
      messageBox.setModal(modal)
      return messageBox.exec_()

  def enoughPrivileges(self, exitNow = True):
    try:
      os.open('/etc/foo', os.O_APPEND | os.O_CREAT)
    except OSError as e:
      messageBox = QtGui.QMessageBox()
      self.applyCommonWidgetProperties(messageBox)
      messageBox.setIcon(QtGui.QMessageBox.Critical)
      messageBox.setStandardButtons(QtGui.QMessageBox.Close)
      messageBox.setText(_("Simple WEP Crack. Error. Insufficient privileges: restart this program from a user with more privileges (root/Administrator)"))
      messageBox.exec_()
      if exitNow:
        sys.exit(1)
      else:
        return False
    else:
      os.remove('/etc/foo')
    return True
  
  def closeEvent(self, event):
    for k in self.processes:
      if self.processes[k] is not None:
        self.processes[k].stop()
    self.animateIcon(None, False)

  def setStatusNoNetStatus(self):
    # Disable aircrack
    for k in ["check", "startmon", "inj", "stopmon", "dump", "fauth", "arpinj", "crack"]:
      self.actions[k].setEnabled(False)
    self.systemTrayIcon.setIcon(self.icon)

  def setStatusNoMonStatus(self):
    self.setStatusNoNetStatus()
    
    # Enable monitor creation
    for k in ["check", "startmon"]:
      self.actions[k].setEnabled(True)
    self.systemTrayIcon.setIcon(self.iconNoMon)

  def setStatusOperative(self):
    # Enable air suite tools
    for k in ["check", "startmon", "inj", "stopmon", "dump", "fauth", "arpinj"]:
      self.actions[k].setEnabled(True)
    # Enable aircrack
    for k in ["crack"]:
      self.actions[k].setEnabled(self.currentNetwork is not None and self.currentNetwork.ssid is not None and not isDirectoryEmpty(self.aircrack.workDir + "/" + self.currentNetwork.ssid))
    self.systemTrayIcon.setIcon(self.iconOperative)

  def setStatusAuto(self):
    # Disable aircrack
    for k in ["check", "startmon", "inj", "stopmon", "dump", "fauth", "arpinj", "crack"]:
      self.actions[k].setEnabled(False)
    self.systemTrayIcon.setIcon(self.icon)

  def quitProgram(self):
    procs = []
    for k in ["dump", "crack"]:
      if self.processes[k] is not None and self.processes[k].process.state() != QtCore.QProcess.NotRunning:
        procs = procs + [self.processes[k]]
    for k in self.processes["replay"]:
      if self.processes["replay"][k] is not None and self.processes["replay"][k].process.state() != QtCore.QProcess.NotRunning:
        procs = procs + [self.processes["replay"][k]]

    if len(procs) > 0:
      reply = self.showModalText(_("Proceeding with closing, all currently active processes will be terminated. Would you want to quit program anyway?"), buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
      if reply == QtGui.QMessageBox.Yes:
        #running = False
        #while running:
          #running = False
          #for p in procs:
            #if p.process.state() != QtCore.QProcess.NotRunning:
              #running = True
              #p.stop()
        self.quit()
    else:
      self.quit()






  #
  # From now on, all the actions...
  #
  def chooseNetwork(self):
    self.systemTrayIcon.setIcon(self.iconBusy)
    self.systemTrayIcon.show()
    self.wifiScanner.scan()
    
    items = []
    for dev in self.wifiScanner.scanResults:
      for ap in dev.wifiNetworks:
        if ap.security == "WEP":
          items = items + [ ap.ssid ]
    
    if len(items) > 0:
      dialog = QtGui.QInputDialog()
      self.applyCommonWidgetProperties(dialog)
      item, ok = dialog.getItem(self.widget, _("Choose a WEP network"), _("WEP networks found: "), items, 0, False)
      if ok and item:
        self.currentNetwork = self.wifiScanner.getWifiNetworkBySSID(item)
        self.actions["wep"].setText(_("Network: ") + self.currentNetwork.ssid)
        if len(self.monitorDevices) == 0:
          self.setStatusNoMonStatus()
        else:
          self.setStatusOperative()
      else:
        self.actions["wep"].setText(_("Find network..."))
        self.systemTrayIcon.setIcon(self.icon)
    else:
      messageBox = QtGui.QMessageBox()
      self.applyCommonWidgetProperties(messageBox)
      messageBox.setIcon(QtGui.QMessageBox.Information)
      messageBox.setStandardButtons(QtGui.QMessageBox.Close)
      messageBox.setText(_("No WEP-protected network found. Try again."))
      messageBox.exec_()
      self.actions["wep"].setText(_("Find network..."))
      self.systemTrayIcon.setIcon(self.icon)

  def chooseAircrackBinDirs(self):
    self.systemTrayIcon.setIcon(self.iconBusy)
    messageBox = QtGui.QMessageBox()
    self.applyCommonWidgetProperties(messageBox)
    messageBox.setIcon(QtGui.QMessageBox.Information)
    messageBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    messageBox.setText(_("aircrack-ng directories are currently:\n\n\t") + self.aircrack.binDir + "\n\t" + self.aircrack.sbinDir + _("\n\nDo you need to change them?"))
    if (messageBox.exec_() == QtGui.QMessageBox.Yes):
      bindir = QtGui.QFileDialog.getExistingDirectory(self.widget, _("Choose \"aircrack-ng\" directory"), self.aircrack.binDir, QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks)
      if bindir:
        self.aircrack.setBinDir(bindir)
      
      sbindir = QtGui.QFileDialog.getExistingDirectory(self.widget, _("Choose \"airmon-ng\", \"airodump-ng\" and \"aireplay-ng\" directory"), self.aircrack.sbinDir, QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks)
      if sbindir:
        self.aircrack.setSbinDir(sbindir)

  def chooseMonitor(self):
    if (self.autoMode):
      if len(self.monitorDevices) > 0:
        return self.monitorDevices[0]
      else:
        return None
    
    if len(self.monitorDevices) > 1:
      dialog = QtGui.QInputDialog()
      self.applyCommonWidgetProperties(dialog)
      item, ok = dialog.getItem(self.widget, _("Choose a monitor device"), _("Available monitors: "), self.monitorDevices, 0, False)
      if not ok or not item:
        return None
      else:
        return item
    elif len(self.monitorDevices) == 1:
      return self.monitorDevices[0]
    else:
      return None

  def killConflictingPrograms(self):
    self.systemTrayIcon.setIcon(self.iconBusy)
    self.showModalText(self.aircrack.mon.check())

  def startMonitor(self):
    self.systemTrayIcon.setIcon(self.iconBusy)
    for res in self.wifiScanner.scanResults:
      self.monitorDevices = self.aircrack.mon.start(res.device, self.currentNetwork.channel)
      if len(self.monitorDevices) > 0:
        self.showModalText(_("Monitor devices found/created:\n") + "\n".join(self.monitorDevices))
      self.setStatusOperative()

  def testMonitor(self):
    res = False
    self.systemTrayIcon.setIcon(self.iconBusy)
    # Injection test
    mon = self.chooseMonitor()
    if self.aircrack.replay.testInjection(self.currentNetwork, mon):
      self.showModalText(_("Monitor ") + mon + _(" works properly"))
      res = True
    else:
      self.showModalText(_("Injection failed, chosen monitor could not work properly"))
    self.systemTrayIcon.setIcon(self.iconOperative)
    return res

  def stopMonitors(self):
    self.systemTrayIcon.setIcon(self.iconBusy)
    monDeleted = []
    monNotDeleted = []
    for mon in self.monitorDevices:
      if self.aircrack.mon.stop(mon):
        monDeleted = monDeleted + [mon]
      else:
        monNotDeleted = monNotDeleted + [mon]
    msg = ""
    if len(monDeleted) + len(monNotDeleted) == 0:
      msg = _("No monitor detected")
    elif len(monDeleted) > 0:
      msg = _("Correctly closed monitors:\n") + "\n".join(monDeleted)
    if len(monNotDeleted) > 0:
      msg = msg + _("\n\nError closing those monitors:\n") + "\n".join(monNotDeleted)
    self.showModalText(msg)
    self.setStatusNoMonStatus()
    self.monitorDevices = monNotDeleted

  def dump(self):
    mon = str(self.chooseMonitor())
    if mon is not None:
      self.processes["dump"] = AircrackGuiProcess(self, title = _("Simple WEP Crack - Dump"), icon = self.icon)
      self.processes["dump"].setDeletePreviousContent(True)
      self.processes["dump"].setBeginTrigger('CH [ ]*[0-9]+')
      self.processes["dump"].setBackground(self.autoMode)
      self.aircrack.startCrackTime()
      self.aircrack.odump.dump(self.currentNetwork, mon, self.aircrack.workDir + "/" + self.currentNetwork.ssid, process = self.processes["dump"])

  def fakeauth(self):
    mon = str(self.chooseMonitor())
    if mon is not None:
      self.processes["replay"]["fauth"] = AircrackGuiProcess(self, title = _("Simple WEP Crack - Fake Authentication"), icon = self.icon)
      self.processes["replay"]["fauth"].setDeletePreviousContent(False)
      self.processes["replay"]["fauth"].setBackground(self.autoMode)
      self.aircrack.replay.fakeAuthentication(self.currentNetwork, mon, process = self.processes["replay"]["fauth"])

  def arpReplay(self):
    mon = str(self.chooseMonitor())
    if mon is not None:
      self.processes["replay"]["arp"] = AircrackGuiProcess(self, title = _("Simple WEP Crack - ARP Requests replay"), icon = self.icon)
      self.processes["replay"]["arp"].setDeletePreviousContent(True)
      self.processes["replay"]["arp"].setBackground(self.autoMode)
      self.aircrack.replay.arpInjection(self.currentNetwork, mon, process = self.processes["replay"]["arp"])

  def crackPassword(self):
    if self.aircrack.odump.output is not None:
      self.processes["cracker"] = AircrackGuiProcess(self, title = _("Simple WEP Crack - Crack password!!"), icon = self.icon)
      self.processes["cracker"].setDeletePreviousContent(False)
      self.processes["cracker"].setLineFilterRegEx('Opening|Attack|Starting|Tested|Failed|KEY FOUND')
      self.processes["cracker"].setStopTrigger('KEY FOUND', self.keyFound)
      self.processes["cracker"].setBackground(self.autoMode)
      self.aircrack.cracker.crack(self.currentNetwork, self.aircrack.workDir + "/" + self.currentNetwork.ssid, self.aircrack.odump.output, process = self.processes["cracker"])

  def crackNetwork(self):
    self.animateCrackingIcon()
    self.autoMode = True
    printNow (_("Autocrack. Choosing network..."))
    self.chooseNetwork()
    if self.currentNetwork.isValid():
      printNow (_(" error. Autocrack manually stopped.") + "\n")
      self.autoMode = False
      self.showModalText(_(" Automatic WEP crack has been manually stopped."))
      return
    printNow (_("done.") + "\n")
    self.killConflictingPrograms()
    time.sleep(5)
    if len(self.monitorDevices) == 0:
      printNow (_("Autocrack. Starting monitor network..."))
      mon = self.startMonitor()
      if len(self.monitorDevices) == 0:
        printNow (_(" error. Autocrack has stopped.") + "\n")
        self.autoMode = False
        self.showModalText(_("Automatic WEP crack stopped. Unable to start a monitor device"))
        return
      printNow (_("done.") + "\n")
    printNow (_("Autocrack. Testing monitor..."))
    if not self.testMonitor():
      printNow (_(" failed. Autocrack has stopped.") + "\n")
      self.autoMode = False
      self.showModalText(_("Automatic WEP crack stopped. Unable to inject properly"))
      return
    printNow (_("passed.") + "\n")
    
    # Now crack
    printNow (_("Autocrack. Cracking, wait just a century..."))
    self.fakeauth()
    self.arpReplay()
    self.dump()
    time.sleep(5) # wait X seconds before running the cracker
    self.crackPassword()
    
  def keyFound(self):
    self.aircrack.stopCrackTime()
    self.autoMode = False
    self.processes["cracker"].stop()
    self.processes["replay"]["arp"].stop()
    self.processes["replay"]["fauth"].stop()
    self.processes["dump"].stop()
    elapsed = self.aircrack.getElapsedTimeMillis() / 1000.
    self.showModalText(self.processes["cracker"].stopLine + "\n(" + _("in") + " " + str(elapsed) + " " + _("seconds)"))
    self.animateIcon(None, False)
    self.systemTrayIcon.setIcon(self.iconOperative)

# Run the application
def main():
  changeLanguage('it_IT')
  app = SimpleWEPCrack( sys.argv )
  sys.exit(app.exec_())

if __name__ == '__main__':
    main()
