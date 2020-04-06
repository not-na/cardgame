
``cg:auth`` - Authentication Packet
===================================

.. cg:packet:: cg:auth

This packet is used to perform log-in and sign-up activities.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:auth`                        |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``auth`` only                               |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the client can authenticate itself with the server as a specific
account. It can also create new accounts using this packet.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the client to the server: ::

   {
      "username": "notna",
      "pwd": "...",

      "create": false,
   }

``username`` is the user name of the account to login as or create.

``pwd`` is the encrypted password of the given account.

.. warning::
   Currently, passwords aren't actually encrypted in transmission. In the future,
   all traffic will be either tunneled through SSL or an asymmetric cipher will
   be used to transmit passwords.

``create`` is an optional flag indicating if the client wishes to create a new account.
If it is not given, it will be assumed as ``false``\ . This flag exists to prevent accidental
account creation should a user mistype their username.

The server will respond with a packet of the same type and the following data: ::

   {
      "status": "logged_in",

      "username": "notna",
      "uuid": "cfde3788-e653-4ef3-8b19-f741e2194e0f",
   }

``status`` is the current authentication status. It should be one of ``logged_in``\ ,
``wrong_credentials``\, ``user_exists`` or ``logged_out``\ .

``username`` is the user name the user is logged in as. This field is only sent
if ``status`` is ``logged_in`` or ``user_exists``\ .

``uuid`` is the :term:`UUID` of the current account. It can be used to look up
further information in the :term:`user database`\ . It is only present if ``status``
is ``logged_in``\ .

If the login attempt was successful, the server will already pre-send a :cg:packet:`cg:status.user`
packet with information on the user. It will also send a :cg:packet:`cg:status.server.mainscreen`
packet to update the client on the contents of the main screen. Also, the connection
mode will change to ``active``\ .

.. seealso::
   See the :cg:packet:`cg:status.user` packet for more information on how to get
   User data.

.. seealso::
   See the :cg:packet:`cg:auth.precheck` packet for more information on the
   authentication process.
