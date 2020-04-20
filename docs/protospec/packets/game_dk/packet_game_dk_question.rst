
``cg:game.dk.question`` - Request an answer from a client
=========================================================

.. cg:packet:: cg:game.dk.question

This packet is used to request an answer from a player. It is only
used for the game :term:`Doppelkopf`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.dk.question`            |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server can ask the client on its "opinion" on something.
A question packet will be answered by the client with a :cg:packet:`cg:game.dk.announce`
packet. This packet is only available for the game :term:`Doppelkopf`\ .

It will be used to ask all players about a *reservation* at the begin of each round.
In the course of this, the concerned players will be inquired after *solos*\ ,
*throwing*\ , *pigs*\ , *superpigs*\ , *poverty* and *wedding*\ .
In the cases of a *wedding* or a *poverty*\ , the choice of the trick or of the cards to
exchange are requested by this packet.
.. seealso::
   See :doc:`../../doppelkopf/rules` for further information on special rules.

In case of an accusation concerning an external misconduct, e.g. originating from a chat,
this packet will be used to ask all the players if they support the accusation.

.. seealso::
   See the :cg:packet:`cg:game.dk.complaint` packet for further information on accusations.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "type":"reservation",
      "target":"296f8f9f-40dc-4ef7-b9b5-851d58c9c966",
   }

``type`` is the type of request sent.

.. note::
   Following types are available: ``reservation``, ``solo``, ``throw``, ``pigs``,
   ``superpigs``, ``poverty``, ``poverty_accept``, ``poverty_trump_choice``,
   ``poverty_return_trumps``, ``poverty_return_choice``,    ``wedding``,
   ``wedding_clarification_trick`` and ``accusation_vote``\ .

``target`` is the :term:`UUID` of the player to whom the question is directed. This is
necessary because sometimes all players are supposed to hear a question, though it might not
be directed at all of them.

.. seealso::
   See the :cg:packet:`cg:game.dk.announce` packet for further information on announcements.