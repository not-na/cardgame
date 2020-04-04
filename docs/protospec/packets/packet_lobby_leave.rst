
``cg:lobby.leave`` - Lobby Leaving Packet
=====================================================

.. cg:packet:: cg:lobby.leave

This packet is used to leave a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.leave`                 |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``lobby`` only                              |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to leave a :term:`lobby`\ . It may contain a part, where the client
informs the server about leaving the lobby, but that decision can also be made by the lobby
creator kicking the implied client. Afterwards, the server informs the client, that it
has left the lobby.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

The first part, where the client informs the server that it is about to leave, is empty.

The server will answer following to the client: ::

   {
      "lobby":"397627fa-2aa3-4cef-b403-7658bb8b424d",
   }
``lobby`` is the :term:`UUID` of the lobby that was left.
