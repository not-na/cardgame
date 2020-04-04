
``cg:lobby.ready`` - Ready to begin the game
=====================================================

.. cg:packet:: cg:lobby.ready

This packet is used by a client to signalise it is ready to begin the game.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.ready`                 |
+-----------------------+--------------------------------------------+
|Direction              |Serverbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``lobby`` only                              |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used by a client to signalise it is ready to begin the game. When all
clients in a :term:`lobby` conveyed their readiness, the game begins.

When the server receives this packet, it will send a :cg:packet:`cg:lobby.change` packet
to all clients in the lobby containing the updated list of ready players.

Structure
---------

The package ought not to contain any data.
