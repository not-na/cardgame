
``cg:game.dk.card.intent`` - Do something with a card
=====================================================

.. cg:packet:: cg:game.dk.card.intent

This packet is used to do something with a card. It is only used for the game :term:`Doppelkopf`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.dk.card.intent`         |
+-----------------------+--------------------------------------------+
|Direction              |Serverbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, a player can perform an action with a card, usually play it. Subsequently,
the server will respond with a :cg:packet:`game.dk.card.transfer` packet. This packet
is only available for the game :term:`Doppelkopf`\ .

In case of an *Armut*\ , this packet will be used to choose the cards that should be
exchanged. Otherwise, it's used to play a card over the course of the game.

.. seealso::
   See :doc:`../../doppelkopf/rules` for further information on special rules.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the client to the server: ::

   {
      "intent":"play"
   }

``intent`` is the action that is ought to be performed. It can be either ``play`` or
``exchange``\ .

.. seealso::
   See the :cg:packet:`game.dk.card.transfer` for further information on how a card is moved
   from one slot to another.