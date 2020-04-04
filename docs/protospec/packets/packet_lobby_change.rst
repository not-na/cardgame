
``cg:lobby.change`` - Lobby Change Packet
=====================================================

.. cg:packet:: cg:lobby.change

This packet is used to inform the members in a :term:`lobby` of any kind of change.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.change`                |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``lobby`` only                              |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to inform all the users in a :term:`lobby` about any kind of change.
This might be a user joining or leaving the lobby, the choice of game or its rules being
changed, players signalising their readiness, and more.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client, all of it optional: ::

   {
      "userlist":["e2639d1f-a7b3-409f-87e4-595a85444d30", "e2639d1f-a7b3-409f-87e4-595a85444d30"],
      "readylist":["e2639d1f-a7b3-409f-87e4-595a85444d30"],
      "spectators":["e2639d1f-a7b3-409f-87e4-595a85444d30"],
      "game":"doppelkopf",
      "rules":{
                  "fuechse":true,
                  "feigheit":true,
                  "armut":false,
               }
   }
``userlist`` is a list containing the :term:`UUID`s of the users in the :term:`lobby`.
``memberlist`` is a list containing the UUIDs of the users that signalised their
readiness to begin the game.
``spectators`` is a list containing the UUIDs of the users that wont play but only watch.
``game`` is the name of the game that will be played.
``rules`` are the rules by which the game will be played.
