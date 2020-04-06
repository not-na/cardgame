
``cg:party.leave`` - Leave party
================================

.. cg:packet:: cg:party.leave

This packet is used to leave a :term:`party`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:party.leave`                 |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``active`` and ``lobby``                    |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to leave a :term:`party`\ , may it be by the clients own decision or
for it being kicked. The server will also confirm the client that it has left the party.

Subsequently, the server will send a :cg:packet:`cg:party.change` packet to all remaining
clients in the lobby containing an updated user list.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

The serverbound packet doesn't contain any data.

.. note::
   If the client is kicked out of the party, the packet will only be clientbound since
   the client didn't choose itself to leave the party.

The server will send following to the client: ::

   {
      "party":"397627fa-2aa3-4cef-b403-7658bb8b424d",
   }

``party`` is the :term:`UUID` of the party that was left.

.. seealso::
   See the :cg:packet:`cg:party.kick` for further information on kicking a user out of a party.
