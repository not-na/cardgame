``cg:party.join`` - Join party
==============================

.. cg:packet:: cg:party.join

This packet is used to join a :term:`party`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:party.join`                  |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``active`` only                             |
+-----------------------+--------------------------------------------+

Purpose
-------

After the creation of a :term:`party`\ , the creator will be joined automatically to
the party. Additionally, if another client accepts an invitation to a party, he will be
joined.

Upon joining, the server will send a :cg:packet:`cg:party.change` packet to the other clients
in the party containing the updated user list. The joining client will receive a similar
packet which however will contain all the information on the party.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
     "party":"397627fa-2aa3-4cef-b403-7658bb8b424d",
   }

``party`` is the party's :term:`UUID`\ .

.. seealso::
   See the :cg:packet:`cg:party.create` packet for further information on how a party is created.
