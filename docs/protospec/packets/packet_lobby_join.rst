
``cg:lobby.join`` - Join lobby
==============================

.. cg:packet:: cg:lobby.join

This packet is used to join a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.join`                  |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``active`` only                             |
+-----------------------+--------------------------------------------+

Purpose
-------

After the creation of a :term:`lobby`\ , the creator and all his :term:`party` members
will be joined automatically. Additionally, any client accepting an invitation will receive
this packet.

Upon joining, the server will send a :cg:packet:`cg:lobby.change` packet to the other clients
in the lobby containing the updated user list. The joining client will receive a similar
packet which however will contain all the information on the lobby.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
     "lobby":"397627fa-2aa3-4cef-b403-7658bb8b424d",
   }

``lobby`` is the lobby's :term:`UUID`\ .

.. seealso::
   See the :cg:packet:`cg:lobby.create` packet for further information on how a lobby is created.
