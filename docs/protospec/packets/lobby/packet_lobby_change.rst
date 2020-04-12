
``cg:lobby.change`` - Lobby data change
=======================================

.. cg:packet:: cg:lobby.change

This packet is used by the server to inform the client on any kind of change in a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.change`                |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``lobby`` only                              |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to inform all the clients in a :term:`lobby` about any kind of change.
This might be a client joining or leaving the lobby, the choice of game or its rules being
changed, players signalising their readiness, and more.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "users":{
         "e2639d1f-a7b3-409f-87e4-595a85444d30": {"ready": true, "role": 1},
         "e70d98cd-a33b-41f2-9cb4-8c6e3aeadbb7": {"ready": false, "role": 2},
         },
      "game":"doppelkopf",
      "gamerules":{
                  "fuechse":true,
                  "feigheit":true,
                  "armut":false,
               },
      "gamerule_validators":{
                  ...
      }
   }

``userlist`` is a dictionary mapping the :term:`UUID`\ s of players to their metadata.
This metadata currently contains the ``ready`` and ``role`` keys. All players must have
their ``ready`` flag set to true to begin the game. ``role`` determines what the player
can do. If the ``role`` is ``-1``\ , the player should be removed.

``game`` is the name of the game that will be played.

``gamerules`` are the rules by which the game will be played. Note that only updated rules will
be sent.

``gamerule_validators`` is a dictionary containing the :term:`validator`\ s for the current game.

.. todo::
   Document the validator concept

.. note::
   All the parameters are optional. However, they should be all sent upon joining so
   the client knows what information to show.

.. note::
   The keywords for the different ``gamerule``\ s will change depending on the ``game``. Also,
   multiple of the games being of german origin, many rules will have german names. All
   gamerule names should be ASCII only for maximum compatibility. This does not however
   apply to the displayed translated names.

