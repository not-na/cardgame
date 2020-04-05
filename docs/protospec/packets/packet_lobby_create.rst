
``cg:lobby.create`` - Create lobby
=====================================================

.. cg:packet:: cg:lobby.create

This packet is used to create a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.create`                |
+-----------------------+--------------------------------------------+
|Direction              |Serverbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``active`` only                             |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server is notified of the creation of a :term:`lobby`\ , either
because a :term:`custom game` was created by a client, or because the :term:`matchmaking`
matched enough players together to start a game.

Upon creating the lobby, the creator and his :term:`party` members will be joined using
a :cg:packet:`cg:lobby.join` packet.

Structure
---------

The package should not contain any data.


.. seealso::
   See the :cg:packet:`cg:lobby.join` packet for further information on the response of
   the server.