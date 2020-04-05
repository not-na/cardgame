
``cg:party.invite`` - Invite client to party
============================================

.. cg:packet:: cg:party.invite

This packet is used to invite other clients to a :term:`party`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:party.invite`                |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``active`` and ``lobby``                    |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to invite other clients to a :term:`party`. It transmits the username
of the invited user to the server and afterwards tells the inviter whether the client
exists. Additionally, it informs the invited client on the invitation.

Upon accepting the invitation, the server will receive a :cg:packet:`cg:party.invite.accept`
packet from the invited client.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "username":"notna",
   }

``username`` is the name of the invited user.

The server will answer to the inviting client with this: ::

   {
      "user_found":True,
   }
``user_found`` is a boolean informing the inviter whether the invited user has been found.

Additionally, it will send following data to the invited client: ::

   {
      "inviter":"e2639d1f-a7b3-409f-87e4-595a85444d30 ",
   }
``inviter`` is the :term:`UUID` of the inviting user.

.. seealso::
   See the :cg:packet:`cg:party.invite.accept` packet for further information on accepting
   an invitation.
