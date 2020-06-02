
``cg:game.start`` - Start game
==============================

.. cg:packet:: cg:game.start

This packet is used to start the game.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.start`                  |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``lobby`` and ``active``                    |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to start the game, either when all clients in a lobby conveyed their
readiness or when a client reconnects to the server after exiting from a running game.
Upon receiving this packet, as well as all the card creation packets, the client will send this
packet back to the server so that it knows, when all the players are ready and the cards
can be dealt

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server: ::

   {
      "game_type": "doppelkopf",
      "game_id": 'e613d0cc-1021-46fb-8403-c2b66663cfb6',
      "player_list": [
         'd5b445bf-8836-4fec-a4a8-a219f6df073e',
         '08e6b252-6f24-4d0f-9d77-be926461874a',
         '9267bb0e-619c-41c6-a3d1-ef7d574ccbdd',
         '9765882f-5763-4373-93a5-f8fd0c643018',
      ],
   }

``game_type`` is the type of the game (``skat``, ``doppelkopf``, ``rummy`` or ``canasta``).

``game_id`` is the :term:`UUID` of the game.

``player_list`` is a list of the :term:`UUID`\ s of the players in the game, in the same order as in the server's
game object

The client will send and empty packet to the server.
