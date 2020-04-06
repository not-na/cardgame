
``cg:lobby.leave`` - Leave lobby
================================

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

This packet is used to leave a :term:`lobby`\ , may it be by the clients own decision or
for it being kicked. The server will also confirm the client that it has left the lobby.

Subsequently, the server will send a :cg:packet:`cg:lobby.change` packet to all remaining
clients in the lobby containing an updated user list.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

The serverbound packet doesn't contain any data.

.. note::
   If the client is kicked out of the lobby, the packet will only be clientbound since
   the client didn't choose itself to leave the lobby.

The server will send following to the client: ::

   {
      "lobby":"397627fa-2aa3-4cef-b403-7658bb8b424d",
   }

``lobby`` is the :term:`UUID` of the lobby that was left.

.. seealso::
   See the :cg:packet:`cg:lobby.kick` for further information on kicking a user out of a lobby.
