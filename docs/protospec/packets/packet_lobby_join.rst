
``cg:lobby.join`` - Lobby Joining Packet
=====================================================

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

After the creation of a :term:`lobby`\ , the creator and all his :term:`party`\ members
will be joined automatically.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
     "lobby":"397627fa-2aa3-4cef-b403-7658bb8b424d",
   }

``lobby`` is the lobby's :term:`UUID` which is required for sanity checking lest the
information is not sent to the wrong user.

.. seealso::
   See the :cg:packet:`cg:lobby.create` packet for further information on how a lobby is created.
