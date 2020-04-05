
``cg:party.change`` - Party data change
=======================================

.. cg:packet:: cg:party.change

This packet is used by the server to inform the client on any kind of change in a :term:`party`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:party.change`                |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``active`` and ``lobby``                    |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to inform all the clients in a :term:`party` about any kind of change.
This mostly will be a client joining or leaving the party.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "userlist":["e2639d1f-a7b3-409f-87e4-595a85444d30", "e2639d1f-a7b3-409f-87e4-595a85444d30"],
   }
``userlist`` is a list containing the :term:`UUID`s of the users in the :term:`party`\ .
