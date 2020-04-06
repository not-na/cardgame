
``cg:game.dk.card.transfer`` - Transfer a card
==============================================

.. cg:packet:: cg:game.dk.card.transfer

This packet is used to transfer a card from one :term:`slot` to another one. It is only
used for the game :term:`Doppelkopf`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.dk.card.transfer`       |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid Modes            |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server can signalise the client that a card is transferred
to another :term:`slot`\ . This packet is only available for the game :term:`Doppelkopf`\ .

This may be used for dealing the cards, where the cards will be moved from the shuffled
deck to the hands of the players. It will also be used when a player plays a card; the
card will be transferred from the player's hand to the table. Furthermore, after all
the players played their card, the four cards on the table will be moved to the trick
stack of the player who won the trick. Moreover, if the rule *Armut* is active,
upon declaring an *Armut*\ , this packet will be used for exchanging three cards from the
concerned players.

.. seealso::
   See :doc:`../../doppelkopf/rules` for further information on special rules.

.. note::
   To minimise the possibilities to cheat, the packet will only transmit the value of the
   card if the client is intended to know about it. Otherwise, the client will only be informed
   on the transfer of an unknown card.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server to the client: ::

   {
      "card_id":"91eb5e2c-b7e8-4d8a-b865-7e9eaf2e6469",
      "card_value":"cq",
      "from_slot":"hand2",
      "to_slot":"table",
   }

``card_id`` is the :term:`UUID` of the transferred card.

``card_value`` is the value of the card. If the client should not know about the card
value, -0 will be transmitted.

``from_slot`` is the :term:`slot` in which the card was before the transfer.

``to_slot`` is the slot to which the card will be transferred.
