
``cg:lobby.ready`` - Lobby readiness conveyance
===============================================

.. cg:packet:: cg:lobby.ready

This packet is used by a client to signalise it is ready to begin the game.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.ready`                 |
+-----------------------+--------------------------------------------+
|Direction              |Serverbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``lobby`` only                              |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used by a client to signalise it is ready to begin the game. When all
clients in a :term:`lobby` conveyed their readiness, the game begins.

When the server receives this packet, it will send a :cg:packet:`cg:lobby.change` packet
to all clients in the lobby containing the updated list of ready players.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the client to the server: ::

   {
      "ready": true,
   }

``ready`` defines whether or not the client is ready to play.
