
``cg:auth.precheck`` - Authentication Precheck Packet
=====================================================

.. cg:packet:: cg:auth.precheck

This packet is used to pre-check a login attempt.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:auth.precheck`               |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``auth`` only                               |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the client can check if the account name actually exists and
fetch an encryption key to be used when sending the password.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the client to the server: ::

   {
      "username": "notna",
   }

``username`` is just the user name entered by the user on the prompt displayed by
the client.

The server responds with a packet like this: ::

   {
      "username": "notna",
      "valid": true,
      "exists": true,

      "key": "...",
   }

``username`` is the same name as was sent by the client, but normalized according
to the server. Usually this involves lower-casing the user name.

``valid`` is a boolean flag that determines whether or not the username is valid
on this server. This does not mean that it exists, just that it could exist.

``exists`` is a boolean flag showing whether the account exists or not. This can
be used by the client to ask the user if they want to create a new account.

``key`` is a binary key to be used to encrypt the password before sending it to the
server. It is specific to the connection, user name and will expire after some time.
If the key is the empty string, no encryption should be applied.

.. seealso::
   See the :cg:packet:`cg:auth` packet for further information on password exchange.