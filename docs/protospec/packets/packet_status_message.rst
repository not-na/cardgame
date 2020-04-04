
``cg:status.message`` - Status Messages for Clients
===================================================

.. cg:packet:: cg:status.message

This packet is used by the server to show different notices, warnings and errors on the
client.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:status.message`              |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |All Modes                                   |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server can cause the client to show warnings and other messages
to the user.

Structure
---------

Note that all examples shown here contain placeholder data and will have different
content in actual packets.

This is an example that the server could send to the client: ::

   {
      "type": "notice",

      "msg": "Hello World!",
   }

``type`` is the type of status message and determines the imagery used in the dialog on
the client. Currently, there are the following types: ``notice``\ , ``warning`` and
``error``\ .

``msg`` is the raw message. Currently, no formatting is supported, but this may change in
the future.

.. note::
   Long messages may be cut short by the client, depending on the window size and ``type``\ .