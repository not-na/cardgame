
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
|Valid States           |``active`` only                             |
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

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "game": "doppelkopf",
      "variant": "c",
   }

``game`` may be a string declaring the type of game the lobby creator wants to play.
This field is optional.

``variant`` may be a string declaring the variant of ``game`` that the lobby creator wants
to play. Available variants differ from game to game. This field is required if ``game``
is given.

.. seealso::
   See the :cg:packet:`cg:lobby.join` packet for further information on the response of
   the server.