
``cg:game.dk.turn`` - Turn Update
=================================

.. cg:packet:: cg:game.dk.turn

This packet is used to inform all players about the next turn. It is only used for the game
:term:`Doppelkopf`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.dk.turn`                |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server informs all clients, whose turn it is to play a card. This
packet is only available for the game :term:`Doppelkopf`\ .

Structure
---------

Note that all examples shown here contain placeholder data and will have different
content in actual packets.

This is the data sent by the server to the client: ::

   {
      "current_trick":1,
      "total_tricks":12,
      "current_player":"7eb1c06d-2f66-46c7-8eef-6aa5a2ff85aa",
   }

``current_trick`` is the trick that is currently being played.

``total_tricks`` is the amount of tricks in one game.

``current_player`` is the :term:`UUID` of the player that should play next.