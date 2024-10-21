#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Roberto Metere
#
# GUI Qt Process which implements Aircrack.Process
import re, PyQt6
import Aircrack

from PyQt6 import QtWidgets, QtCore
from abc import ABCMeta

class MetaAircrackGuiProcess(type(QtWidgets.QWidget), ABCMeta): pass

class AbstractAircrackGuiProcess(QtWidgets.QWidget, Aircrack.Process):
  __metaclass__ = MetaAircrackGuiProcess
  pass

# Gui Process captures output from shell commands
class AircrackGuiProcess(AbstractAircrackGuiProcess):
  process = None
  layout = None
  cmdLabel = None
  output = None
  deletePreviousContent = False
  beginTrigger = None
  endTrigger = None
  lineFilterRegEx = None
  background = False
  stopTrigger = None
  stopCallback = None
  stopLine = None
  
  def __init__(self, parent = None, title = "Aircrack GUI Process", icon = None):
    super(QtWidgets.QWidget, self).__init__(None)
    self.setWindowIcon(icon)
    self.setWindowTitle(title)
    self.process = QtCore.QProcess(parent)
    self.layout = QtWidgets.QVBoxLayout()
    self.cmdLabel = QtWidgets.QLabel()
    self.output = QtWidgets.QTextEdit()
    self.output.setReadOnly(True)
    
    self.layout.addWidget(self.cmdLabel)
    self.layout.addWidget(self.output)
    self.setLayout(self.layout)
    self.resize(640, 480)
    
    self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
    self.process.readyReadStandardOutput.connect(self.stdoutReady)
  
  def closeEvent(self, event):
    messageBox = QtWidgets.QMessageBox()
    messageBox.setIcon(QtWidgets.QMessageBox.Information)
    messageBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )
    messageBox.setText("Terminate process?")
    messageBox.setModal(True)
    
    reply = messageBox.exec()
    if reply == QtWidgets.QMessageBox.Yes:
      self.stop()
    event.ignore()
  
  def dataReady(self, data = None):
    if self.beginTrigger is not None:
      reg = re.search(self.beginTrigger, data.decode('utf-8'))
      if reg is not None:
        outString = data[data.find(reg.group(0)):]
        if self.endTrigger is not None:
          reg = re.search(self.endTrigger, outString.decode('utf-8'))
          if reg is not None:
            outString = outString[:outString.rfind(reg.group(0))]
      else:
        outString = None
    else:
      outString = data
    if outString is not None:
      # Remove "noise"
      outString = re.sub(r'\[([0-9]+;[0-9]+)*H', '', outString)
      outString = re.sub(r'\[[0-9]*[JKC]', '\n', outString)
      
      # Stop Trigger?
      if self.stopTrigger is not None:
        reg = re.search(self.stopTrigger, outString.decode('utf-8'))
        if reg is not None:
          self.stopLine = None
          for l in outString.splitlines():
            if l.startswith(self.stopTrigger):
              self.stopLine = l
          if self.stopLine is None:
            print(_("We got a big error here!"))
          else:
            print(self.stopLine)
            self.stop()
            self.stopCallback()
      
      # Filter lines if needed
      if self.lineFilterRegEx is not None:
        rows = outString.splitlines()
        outRows = []
        for r in rows:
          reg = re.search(self.lineFilterRegEx, r.decode('utf-8'))
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
    if not self.background:
      self.show()
  
  def stop(self):
    self.process.terminate()
    self.hide()
  
  def setBackground(self, value):
    self.background = (value == True)
  
  def setDeletePreviousContent(self, value):
    self.deletePreviousContent = (value == True)
  
  def setBeginTrigger(self, beginTrigger):
    self.beginTrigger = beginTrigger
  
  def setEndTrigger(self, endTrigger):
    self.endTrigger = endTrigger
  
  def setLineFilterRegEx(self, lineFilterRegEx):
    self.lineFilterRegEx = lineFilterRegEx
  
  def setStopTrigger(self, stopTrigger, callBack = None):
    self.stopTrigger = stopTrigger
    self.stopCallback = callBack
