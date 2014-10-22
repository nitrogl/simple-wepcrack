#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Roberto Metere
#
# GUI Qt Process which implements Aircrack.Process
import re, PyQt4
import Aircrack

from PyQt4 import QtGui, QtCore
from abc import ABCMeta

class MetaAircrackGuiProcess(type(QtGui.QWidget), ABCMeta): pass

class AbstractAircrackGuiProcess(QtGui.QWidget, Aircrack.Process):
  __metaclass__ = MetaAircrackGuiProcess
  pass

# Gui Process captures output from shell commands
class AircrackGuiProcess(AbstractAircrackGuiProcess):
  process = None
  layout = None
  cmdLabel = None
  output = None
  deletePreviousContent = False
  startTrigger = None
  stopTrigger = None
  lineFilterRegEx = None
  
  def __init__(self, parent = None, title = "Aircrack GUI Process", icon = None):
    super(QtGui.QWidget, self).__init__(None)
    self.setWindowIcon(icon)
    self.setWindowTitle(title)
    self.process = QtCore.QProcess(parent)
    self.layout = QtGui.QVBoxLayout()
    self.cmdLabel = QtGui.QLabel()
    self.output = QtGui.QTextEdit()
    self.output.setReadOnly(True)
    
    self.layout.addWidget(self.cmdLabel)
    self.layout.addWidget(self.output)
    self.setLayout(self.layout)
    self.resize(640, 480)
    
    self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
    self.process.readyReadStandardOutput.connect(self.stdoutReady)
  
  def closeEvent(self, event):
    messageBox = QtGui.QMessageBox()
    messageBox.setIcon(QtGui.QMessageBox.Information)
    messageBox.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No )
    messageBox.setText("Terminate process?")
    messageBox.setModal(True)
    
    reply = messageBox.exec_()
    if reply == QtGui.QMessageBox.Yes:
      self.stop()
    event.ignore()
  
  def dataReady(self, data = None):
    if self.startTrigger is not None:
      reg = re.search(self.startTrigger, data)
      if reg is not None:
	outString = data[data.find(reg.group(0)):]
	if self.stopTrigger is not None:
	  reg = re.search(self.stopTrigger, outString)
	  if reg is not None:
	    outString = outString[:outString.rfind(reg.group(0))]
      else:
	outString = None
    else:
      outString = data
    if outString is not None:
      # Remove "noise"
      outString = re.sub('\[([0-9]+;[0-9]+)*H', '', outString)
      outString = re.sub('\[[0-9]*[JK]', '\n', outString)
      
      # Filter lines if needed
      if self.lineFilterRegEx is not None:
	rows = outString.splitlines()
	outRows = []
	for r in rows:
	  reg = re.search(self.lineFilterRegEx, r)
	  if reg is not None:
	    outRows = outRows + [r]
	outString = "\n".join(outRows)
      
      if self.deletePreviousContent:
	self.output.setText(outString)
      else:
	cursor = self.output.textCursor()
	cursor.movePosition(cursor.End)
	cursor.insertText(outString)
	self.output.ensureCursorVisible()
      return outString
    else:
      return ""
  
  def stdoutReady(self):
    self.dataReady(str(self.process.readAllStandardOutput()))
  
  def stderrReady(self):
    self.dataReady(str(self.process.readAllStandardError()))
  
  def run(self, cmd):
    self.cmdLabel.setText(" ".join(cmd))
    #self.process.start(cmd[0], cmd[1:], QtCore.QIODevice.ReadOnly | QtCore.QIODevice.Unbuffered)
    self.process.start(cmd[0], cmd[1:], QtCore.QIODevice.ReadOnly)
    self.show()
  
  def stop(self):
    self.process.terminate()
    self.hide()
  
  def setDeletePreviousContent(self, value):
    self.deletePreviousContent = (value == True)
  
  def setStartTrigger(self, startTrigger):
    self.startTrigger = startTrigger
  
  def setStopTrigger(self, stopTrigger):
    self.stopTrigger = stopTrigger
  
  def setLineFilterRegEx(self, lineFilterRegEx):
    self.lineFilterRegEx = lineFilterRegEx
