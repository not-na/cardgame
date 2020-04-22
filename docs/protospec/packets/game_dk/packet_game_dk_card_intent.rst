
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
|Valid States           |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, a player can perform an action with a card. Usually this is playing
the card. Subsequently, the server will send a :cg:packet:`game.dk.card.transfer`
packet to all clients. This packet is only available for the game :term:`Doppelkopf`\ .

In case of a *poverty*\ , this packet will be used to choose the cards that should be
exchanged. Otherwise, it's used to play a card over the course of the game.

.. seealso::
   See :doc:`../../doppelkopf/rules` for further information on special rules.

Structure
---------

Note that all examples shown here contain placeholder data and will have different
content in actual packets.

This is the data sent by the client to the server: ::

   {
      "intent":"play",
      "card":"91eb5e2c-b7e8-4d8a-b865-7e9eaf2e6469",
   }

``intent`` is the action that the player wants performed. It can be ``play``\ , ``pass_card`` or
``return_card``\ .

``card`` is the :term:`UUID` of the card the player wants to use for the given intent. If an intent requires
multiple cards, this field may be a list.

.. seealso::
   See the :cg:packet:`game.dk.card.transfer` for further information on how a card is moved
   from one slot to another.