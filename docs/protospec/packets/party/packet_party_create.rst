
``cg:party.create`` - Party creation
====================================

.. cg:packet:: cg:lobby.ready

This packet is used to create a :term:`party`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:party.create`                |
+-----------------------+--------------------------------------------+
|Direction              |Serverbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``active`` only                             |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used by a client to create a :term:`party`\ . Afterwards, the client will
be automatically joined the party using the :cg:packet:`cg:party.join` packet.

Structure
---------

The package ought not to contain any data.

.. seealso::
   See the :cg:packet:`cg:party.join` for further information on joining a party.