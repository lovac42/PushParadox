# -*- coding: utf-8 -*-
# Copyright: (C) 2018 Lovac42
# Support: https://github.com/lovac42/PushParadox
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Version: 0.0.1


from aqt import mw
from anki.hooks import wrap, addHook

from anki import version
ANKI21=version.startswith("2.1.")


def getNewCard(sched, _old):
    card=_old(sched)
    if not card or card.odid: return card

    conf=sched.col.decks.confForDid(card.did)
    siblingIvl=conf.get("siblingStage", 0)

    contraction=mw.col.db.first("""select 
sum(case when type in (1,2,3) and queue != -1 
and ivl < ? then 1 else 0 end)
from cards where nid = ? and id != ?""",
siblingIvl, card.nid, card.id)[0] or 0

    if contraction:
        sched.buryCards([card.id])
        return sched._getNewCard() #next card
    return card


import anki.sched
anki.sched.Scheduler._getNewCard = wrap(anki.sched.Scheduler._getNewCard, getNewCard, 'around')
if ANKI21:
    import anki.schedv2
    anki.schedv2.Scheduler._getNewCard = wrap(anki.schedv2.Scheduler._getNewCard, getNewCard, 'around')


##################################################
#
#  GUI stuff, adds deck menu options to enable/disable
#  this addon for specific decks
#
#################################################

import aqt
import aqt.deckconf
from aqt.qt import *

if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


def dconfsetupUi(self, Dialog):
    r=self.gridLayout.rowCount()
    label=QtWidgets.QLabel(self.tab_3)
    label.setText(_("Sibling IVL:"))
    self.gridLayout.addWidget(label, r, 0, 1, 1)

    self.siblingStage=QtWidgets.QSpinBox(self.tab_3)
    self.siblingStage.setMinimum(0)
    self.siblingStage.setMaximum(999)
    self.siblingStage.setSingleStep(5)
    self.gridLayout.addWidget(self.siblingStage, r, 1, 1, 1)

    label=QtWidgets.QLabel(self.tab_3)
    label.setText(_("Bury NC until siblings exceed this. (0=disable)"))
    self.gridLayout.addWidget(label, r, 2, 1, 1)


def loadConf(self):
    lim=self.conf.get("siblingStage", 0)
    self.form.siblingStage.setValue(lim)


def saveConf(self):
    self.conf['siblingStage']=self.form.siblingStage.value()


aqt.forms.dconf.Ui_Dialog.setupUi = wrap(aqt.forms.dconf.Ui_Dialog.setupUi, dconfsetupUi, pos="after")
aqt.deckconf.DeckConf.loadConf = wrap(aqt.deckconf.DeckConf.loadConf, loadConf, pos="after")
aqt.deckconf.DeckConf.saveConf = wrap(aqt.deckconf.DeckConf.saveConf, saveConf, pos="before")
