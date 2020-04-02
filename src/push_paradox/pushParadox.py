# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/PushParadox
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from aqt import mw
from anki.hooks import wrap, addHook

from anki import version
ANKI21=version.startswith("2.1.")


def getSibling(card):
    return mw.col.db.list("""select
id from cards where type == 0 and queue == 0
and nid = ? and did = ?""", card.nid, card.did)


def isParadox(card, siblingIvl):
    if not siblingIvl: return False
    return mw.col.db.first("""select 
sum(case when type in (1,2,3) and queue != -1 
and ivl < ? then 1 else 0 end)
from cards where nid = ? and id != ?""",
siblingIvl, card.nid, card.id)[0] or False


def preprocessNewQueue(sched):
    "For those w/ weird study patterns"
    arr=[]
    for id in sched._newQueue:
        card=mw.col.getCard(id)
        if card.queue<0: continue
        if not card.odid:
            conf=sched.col.decks.confForDid(card.did)
            siblingIvl=conf.get("siblingStage", 0)
            if isParadox(card,siblingIvl):
                siblings=getSibling(card)
                sched.buryCards(siblings)
                continue
        arr.append(id)
    sched._newQueue=arr


def getNewCard(sched, _old):
    if not sched._newQueue and sched._fillNew():
        preprocessNewQueue(sched)

    card=_old(sched)
    if not card or card.odid: return card

    #double checks in case of inserts
    conf=sched.col.decks.confForDid(card.did)
    siblingIvl=conf.get("siblingStage", 0)
    if isParadox(card,siblingIvl):
        sched.newCount += 1
        preprocessNewQueue(sched)
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
from anki.lang import _

if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets


def valuechange(self):
    msg='(disabled)'
    n=self.siblingStage.value()
    if n:
        msg="Bury related NC until all siblings exceed IVL of %d"%n
    self.pushParadoxLbl.setText(_(msg))


def dconfsetupUi(self, Dialog):
    r=self.gridLayout.rowCount()
    label=QtWidgets.QLabel(self.tab)
    label.setText(_("Sibling IVL:"))
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
