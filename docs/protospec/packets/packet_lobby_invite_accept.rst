
``cg:lobby.invite.accept`` - Accepting the invitation to a lobby
=====================================================

.. cg:packet:: cg:lobby.invite.accept

This packet is used to accept the invitation to a :term:`lobby`.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:lobby.invite.accept`         |
+-----------------------+--------------------------------------------+
|Direction              |Serverbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``active`` only                             |
+-----------------------+--------------------------------------------+

Purpose
-------

Upon being invited to a :term:`lobby`\ , this packet is used to inform the server on
whether the client has accepted or denied the invitation.

If it accepts the invitation, the client will receive a :cg:packet:`cg:lobby.join` packet.
Furthermore, the inviter will be informed via a :cg:packet:`cg:status.message` packet,
if the invited client accepted the invitation.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "accepted":true,
   }

``accepted`` is a boolean declaring whether the invitation has been accepted.

.. seealso::
   See the :cg:packet:`cg:lobby.invite` packet for further information on inviting to lobbies.
   See the :cg:packet:`cg:lobby.join` packet for further information on joining a lobby.
