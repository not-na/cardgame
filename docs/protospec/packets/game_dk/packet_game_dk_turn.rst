
``cg:game.dk.turn`` - Whose turn is it
======================================

.. cg:packet:: cg:game.dk.turn

This packet is used to inform the players, whose turn it is. It is only used for the game
:term:`Doppelkopf`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.dk.turn`                |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server informs all clients, whose turn it is to play a card. This
packet is only available for the game :term:`Doppelkopf`\ .

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "current_round":0,
      "total_rounds":12,
      "current_player":"7eb1c06d-2f66-46c7-8eef-6aa5a2ff85aa",
   }

``current_round`` is the amount of rounds that have already been finished.

``total_rounds`` is the amount of rounds in one game.

``current_player`` is the :term:`UUID` of the player, whose turn it is to play a card.