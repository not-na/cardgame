
``cg:status.user`` - User Status Update
=======================================

.. cg:packet:: cg:status.user

This packet is used to request and retrieve user information and status updates.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:status.user`                 |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |All States                                  |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the client can request information about a specific user from
the server. The server determines what information to send.

Additionally, the server may send this packet at any to preempt information requests
or notify the client of changes to a users appearance.

Structure
---------

Note that all examples shown here contain placeholder data and will have different
content in actual packets.

This is the data sent by the client to the server to request information on a user: ::

   {
      "username": "notna",

      "uuid": "61cf5d06-8d01-4fb3-a4a8-ea7a0633b0b8",
   }

``username`` is the name of the user that the client wants information on.

``uuid`` is the :term:`UUID` that the client wants more information on.

.. note::
   ``uuid`` and ``username`` are not exclusive, but ``uuid`` will be used preferentially
   before ``username``\ .


The server sends user status updates in the following format, either as a response
to a request or as a notification: ::

   {
      "username": "notna",
      "uuid": "cfde3788-e653-4ef3-8b19-f741e2194e0f",

      "status": "logged_in",
      ...
   }

``status`` is the current status of the user. This may be one of ``online``\ ,
``away``\ , ``busy``\, ``offline`` or ``notexist`` if the user could not be found.

.. note::
   If ``status`` is ``notexist``\ , all other fields will not be populated.

``username`` is the user name to be displayed for the given user.

``uuid`` is the :term:`UUID` of the given user.

.. todo::
   Add more user attributes here.