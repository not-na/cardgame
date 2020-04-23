
``cg:game.dk.round.change`` - Data update on the round
======================================================

.. cg:packet:: cg:game.dk.round.change

This packet is used to update the client's data on a round of :term:`Doppelkopf`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.dk.round.change`        |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server informs the client on change in the round. This packet is
only available for the game :term:`Doppelkopf`\ .

It will be used to signalise the begin or the end of a round. Furthermore, it tells the
client after the end of the reservations about the game type.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "phase": "reservations",
      "player_list": [
         'd5b445bf-8836-4fec-a4a8-a219f6df073e',
         '08e6b252-6f24-4d0f-9d77-be926461874a',
         '9267bb0e-619c-41c6-a3d1-ef7d574ccbdd',
         '9765882f-5763-4373-93a5-f8fd0c643018',
      ],
      "game_type": "solo_hearts",
   }

``phase`` is the current phase of the game.

.. note::
   ``phase`` can have following values: ``loading``, ``dealing``, ``reservations``,
   ``tricks``, ``counting`` and ``end``

``player_list`` is a list of the :term:`UUID`\ s of the players in the game, in the same order as in the server's
game object

``game_type`` is the type of the game.

``modifiers`` are modifiers like a buckround that influence the weight of the game.
