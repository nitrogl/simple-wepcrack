# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'interface/AboutBox.ui'
#
# Created: Thu Dec 18 08:09:49 2014
#      by: PyQt4 UI code generator 4.9.6
#
# WARNING! All changes made in this file will be lost!

from PyQt6 import QtCore, QtGui, QtWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_AboutBox(object):
    def setupUi(self, AboutBox):
        AboutBox.setObjectName(_fromUtf8("AboutBox"))
        AboutBox.resize(388, 334)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutBox.sizePolicy().hasHeightForWidth())
        AboutBox.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/res/swepc_green_small.png")), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
        AboutBox.setWindowIcon(icon)
        AboutBox.setLocale(QtCore.QLocale(QtCore.QLocale.Language.Italian, QtCore.QLocale.Country.Italy))
        AboutBox.setSizeGripEnabled(True)
        self.gridLayout = QtWidgets.QGridLayout(AboutBox)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.widget_2 = QtWidgets.QWidget(AboutBox)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.gridLayout_2 = QtWidgets.QGridLayout(self.widget_2)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.widgetLogo = QtWidgets.QWidget(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widgetLogo.sizePolicy().hasHeightForWidth())
        self.widgetLogo.setSizePolicy(sizePolicy)
        self.widgetLogo.setMinimumSize(QtCore.QSize(150, 130))
        self.widgetLogo.setMaximumSize(QtCore.QSize(150, 16777215))
        self.widgetLogo.setObjectName(_fromUtf8("widgetLogo"))
        self.labelLogo = QtWidgets.QLabel(self.widgetLogo)
        self.labelLogo.setEnabled(True)
        self.labelLogo.setGeometry(QtCore.QRect(0, 0, 151, 131))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelLogo.sizePolicy().hasHeightForWidth())
        self.labelLogo.setSizePolicy(sizePolicy)
        self.labelLogo.setText(_fromUtf8(""))
        self.labelLogo.setPixmap(QtGui.QPixmap(_fromUtf8(":/res/swepc_green_small.png")))
        self.labelLogo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelLogo.setObjectName(_fromUtf8("labelLogo"))
        self.horizontalLayout.addWidget(self.widgetLogo)
        self.labelTitles = QtWidgets.QLabel(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelTitles.sizePolicy().hasHeightForWidth())
        self.labelTitles.setSizePolicy(sizePolicy)
        self.labelTitles.setMinimumSize(QtCore.QSize(0, 130))
        self.labelTitles.setObjectName(_fromUtf8("labelTitles"))
        self.horizontalLayout.addWidget(self.labelTitles)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetDefaultConstraint)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.labelMessage = QtWidgets.QLabel(self.widget_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelMessage.sizePolicy().hasHeightForWidth())
        self.labelMessage.setSizePolicy(sizePolicy)
        self.labelMessage.setMinimumSize(QtCore.QSize(0, 0))
        self.labelMessage.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.labelMessage.setScaledContents(False)
        self.labelMessage.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.labelMessage.setWordWrap(True)
        self.labelMessage.setOpenExternalLinks(False)
        self.labelMessage.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse|QtCore.Qt.TextInteractionFlag.TextSelectableByMouse)
        self.labelMessage.setObjectName(_fromUtf8("labelMessage"))
        self.verticalLayout_2.addWidget(self.labelMessage)
        self.gridLayout_2.addLayout(self.verticalLayout_2, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.widget_2, 0, 0, 1, 1)

        self.retranslateUi(AboutBox)
        QtCore.QMetaObject.connectSlotsByName(AboutBox)

    def retranslateUi(self, AboutBox):
        AboutBox.setWindowTitle(_translate("AboutBox", "Simple WEP Crack - Aiuto", None))
        self.labelTitles.setText(_translate("AboutBox", "<html><head/><body><p>Simple WEP Crack</p><p>versione: <span style=\" font-weight:600;\">0.2 </span><br/>autore: <span style=\" font-weight:600;\">Roberto Metere </span><br/>data: <span style=\" font-weight:600;\">25 ottobre 2014</span></p><p>Copyright © 2014 Roberto Metere</p></body></html>", None))
        self.labelMessage.setText(_translate("AboutBox", "<html><head/><body><p><span style=\" font-weight:600;\">Simple WEP Crack</span> è sostanzialmente un\'icona di sistema che lancia diversi comandi utili per testare la sicurezza delle proprie reti WEP.</p><p>Inoltre può essere messo in modalità automatica, previa la scelta della rete, per motivi legali.</p></body></html>", None))

import AboutBox_rc
