
``cg:lobby.invite.accept`` - Accept invitation to lobby
=======================================================

.. cg:packet:: cg:lobby.invite.accept

This packet is used to accept the invitation to a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.invite.accept`         |
+-----------------------+--------------------------------------------+
|Direction              |Serverbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``active`` only                             |
+-----------------------+--------------------------------------------+

Purpose
-------

Upon being invited to a :term:`lobby`\ , this packet is used to inform the server on
whether the client has accepted or denied the invitation.

If it accepts the invitation, the client will receive a :cg:packet:`cg:lobby.join` packet.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "accepted":true,
      "inviter":"d2639d1f-a7b3-409f-87e4-595a85444d30"
      "lobby_id":"e2639d1f-a7b3-409f-87e4-595a85444d30",
   }

``accepted`` is a boolean declaring whether the invitation has been accepted.

``inviter`` is the :term:`UUID` of inviting user.

``lobby_id`` is the :term:`UUID` of the lobby the user was invited to.

.. seealso::
   See the :cg:packet:`cg:lobby.invite` packet for further information on inviting to lobbies.

.. seealso::
   See the :cg:packet:`cg:lobby.join` packet for further information on joining a lobby.
