# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/PushParadox
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


import aqt
import aqt.deckconf
from aqt import mw
from anki.hooks import wrap
from aqt.qt import *
from anki.lang import _

from .lib.com.lovac42.anki.version import ANKI21

if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


def valuechange(self):
    msg='(disabled)'
    n=self.siblingStage.value()
    if n:
        msg="Bury related New Card(s) until all<br>siblings exceed an interval (IVL) of %d"%n
    self.pushParadoxLbl.setText(_(msg))


def dconfsetupUi(self, Dialog):
    r=self.gridLayout.rowCount()
    label=QtWidgets.QLabel(self.tab)
    label.setText(_("Sibling interval:"))
    self.gridLayout.addWidget(label, r, 0, 1, 1)

    self.siblingStage=QtWidgets.QSpinBox(self.tab)
    self.siblingStage.setMinimum(0)
    self.siblingStage.setMaximum(999)
    self.siblingStage.setSingleStep(5)
    self.siblingStage.valueChanged.connect(lambda:valuechange(self))
    self.gridLayout.addWidget(self.siblingStage, r, 1, 1, 1)

    self.pushParadoxLbl=QtWidgets.QLabel(self.tab)
    self.pushParadoxLbl.setText(_("(disabled)"))
    self.gridLayout.addWidget(self.pushParadoxLbl, r, 2, 1, 1)


def loadConf(self):
    lim=self.conf.get("siblingStage", 0)
    self.form.siblingStage.setValue(lim)


def saveConf(self):
    self.conf['siblingStage']=self.form.siblingStage.value()


aqt.forms.dconf.Ui_Dialog.setupUi = wrap(aqt.forms.dconf.Ui_Dialog.setupUi, dconfsetupUi, pos="after")
aqt.deckconf.DeckConf.loadConf = wrap(aqt.deckconf.DeckConf.loadConf, loadConf, pos="after")
aqt.deckconf.DeckConf.saveConf = wrap(aqt.deckconf.DeckConf.saveConf, saveConf, pos="before")
