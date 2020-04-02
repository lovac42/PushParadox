# -*- coding: utf-8 -*-
# Copyright: (C) 2018-2020 Lovac42
# Support: https://github.com/lovac42/PushParadox
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html


from aqt import mw
from anki.hooks import wrap, addHook

from .lib.com.lovac42.anki.version import ANKI20


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
    if not card or card.odid:
        return card

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
if not ANKI20:
    import anki.schedv2
    anki.schedv2.Scheduler._getNewCard = wrap(anki.schedv2.Scheduler._getNewCard, getNewCard, 'around')
