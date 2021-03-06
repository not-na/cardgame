
``cg:lobby.invite`` - Invite client to lobby
==============================================

.. cg:packet:: cg:lobby.invite

This packet is used to invite other clients to a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.invite`                |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``active`` and ``lobby``                    |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to invite other clients to a :term:`lobby`. It transmits the username
of the invited user to the server and afterwards tells the inviter whether the client
exists. Additionally, it informs the invited client on the invitation.

Upon accepting the invitation, the server will receive a :cg:packet:`cg:lobby.invite.accept`
packet from the invited client.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the client to the server: ::

   {
      "username":"notna",
   }

``username`` is the name of the invited user.

The server will send following data to the invited client: ::

   {
      "inviter":"e2639d1f-a7b3-409f-87e4-595a85444d30",
      "lobby_id":"g2639d1f-a7b3-409f-87e4-595a85444d30"
   }

``inviter`` is the :term:`UUID` of the inviting user.

``lobby_id`` is the :term:`UUID` of the lobby the user was invited to.

.. seealso::
   See the :cg:packet:`cg:lobby.invite.accept` packet for further information on accepting
   an invitation.
