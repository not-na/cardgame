
``cg:lobby.create`` - Lobby Creation Packet
=====================================================

.. cg:packet:: cg:lobby.create

This packet is used to create a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.create`                |
+-----------------------+--------------------------------------------+
|Direction              |Serverbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``active`` only                             |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server is notified of the creation of a :term:`custom game`\ .
It will create a :term:`lobby` and add the creator and his :term:`party`\ members to it.
After the server receiving this packet, it will send the concerned clients a
:cg:packet:`cg:lobby.join` packet.

Structure
---------

The package should not contain any data.


.. seealso::
   See the :cg:packet:`cg:lobby.join` packet for further information on the response of
   the server.