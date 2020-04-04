
``cg:lobby.kick`` - Lobby Kicking Packet
=====================================================

.. cg:packet:: cg:lobby.invite

This packet is used to kick another user out of a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.kick`                  |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``lobby`` only                              |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to kick someone out of a :term:`lobby`\ . It also allows the kicker
to name a reason for the kick and will inform the kickee of this reason. Subsequently
the server will send the concerned client a :cg:packet:`cg:lobby.leave` packet.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "username":"notna",
      "reason":"Pressed Alt-F4 to turn up the volume",
   }

``username`` is the name user that ought to be kicked.
``reason`` is the justification for the kick.

The server will notify the kickee with following data: ::

   {
      "kicker":"kitfisto",
      "reason":"Pressed Alt-F4 to turn up the volume",
   }
``kicker`` is the username of the user that kicked the concerned client out of the lobby.

.. seealso::
   See the :cg:packet:`cg:lobby.leave` packet for further information on leaving a lobby.
