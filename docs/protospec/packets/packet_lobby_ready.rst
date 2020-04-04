
``cg:lobby.ready`` - Lobby Ready Packet
=====================================================

.. cg:packet:: cg:lobby.ready

This packet is used by a client to signalise he is ready to start the game.

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

This packet is used by a player to signalise he is ready to begin the game. When all
players in a :term:`lobby` conveyed their readiness, the game begins.

Structure
---------

The package ought not to contain any data.
