
``cg:status.server.mainscreen`` - Status Updates for the main screen
====================================================================

.. cg:packet:: cg:status.server.mainscreen

This packet is sent by the server to let the client know about the contents of the main
screen.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:status.message`              |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``active`` only                             |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server can update the client on information shown on the main screen.

Structure
---------

Note that all examples shown here contain placeholder data and will have different
content in actual packets.

This is an example that the server could send to the client: ::

   {
      ...
   }

.. todo::
   Find something to transmit here...

.. seealso::
   See the :cg:packet:`cg:status.user` packet for more information about how user profile
   data is sent to the client.