
``cg:lobby.kick`` - Kick user from lobby
========================================

.. cg:packet:: cg:lobby.kick

This packet is used to kick another client from a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.kick`                  |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``lobby`` only                              |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to kick a client from a :term:`lobby`\ . It also allows the kicker
to name a reason for why the other client has been kicked.

This client will receive a :cg:packet:`cg:status.message` packet informing it on the
reason. Subsequently, the server will send it a :cg:packet:`cg:lobby.leave` packet.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "uuid":"dc71e5dd-5d4b-4809-8546-068e2628f115",
      "reason":"Pressed Alt-F4 to turn up the volume",
   }

``uuid`` is the :term:`UUID` of the user that ought to be kicked.

``reason`` is the justification for the kick.

.. seealso::
   See the :cg:packet:`cg:lobby.leave` packet for further information on leaving a lobby.
