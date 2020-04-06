
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

Structure
---------

TODO