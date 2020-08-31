
``cg:version.check`` - Version compatibility check
==================================================

.. cg:packet:: cg:version.check

This packet is used to check client and server compatibility

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:version.check`               |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``versioncheck`` only                       |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the compatibility between server and client is ascertained.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the client to the server: ::

   {
      "protoversion": 1,
      "semver": "0.1.0-dev",

      "flavor": "vanilla",
   }

``protoversion`` is a positive integer number that has to match exactly between all parties.

``semver`` is used for display to the user and may be used in the future for more granular
compatibility checks.

``flavor`` is the "edition" of the client. ``vanilla`` indicates a standard and unmodified
client. Modded versions and special versions should use different flavors. The flavor
must match exactly and is case sensitive.

The server will respond with a packet of the same type and the following data: ::

   {
      "compatible": true,

      "protoversion": 1,
      "semver": "0.1.0-dev",
      "flavor": "vanilla",
   }

``compatible`` indicates whether or not the client and this server are compatible with each
other. If ``compatible`` is false, the server will end the connection immediately after sending
the packet.

``protoversion``\ , ``semver`` and ``flavor`` are the corresponding version information from the server.

.. note::
   Note that ``protoversion`` and ``semver`` may not appear to match to the client. This
   can happen if the server supports a compatibility mode for older/newer clients. The server
   should always report its actual version, not the emulated one.