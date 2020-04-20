
``cg:game.dk.announce`` - Make an announcement
==============================================

.. cg:packet:: cg:game.dk.announce

This packet is used to announce something. It is only used for the game :term:`Doppelkopf`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.dk.announce`            |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, a player can make an announcement. This announcement will be sent to
all the players. This packet is only available for the game :term:`Doppelkopf`\ .

This packet will be used to answer to a *reservation*\ , *solo*\ , *throwing*\ , *pigs*\ ,
*superpigs*\ , *poverty* and *wedding*\ . In case of a *wedding*\ , it will
transfer the clarification trick and in case of a *poverty*\ , it will be used to tell the
amount of returned trumps.
During the course of the game, it will be used to announce *Re* and *Kontra* as well as
denials like *No 90* etc. Furthermore, it will be used to announce a *pig*\ .
In case of an accusation with external misconduct it will be used to transmit the votes
of the players.

.. seealso::
   See :doc:`../../doppelkopf/rules` for further information on special rules.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the client to the server: ::

   {
      "type":"poverty_return",
      "data":{"amount":3},
   }

``type`` is the context in which the announcement is made.

``data`` is an optional argument transmitting further information if required.

.. note::
   Following types are available: ``reservation_yes``, ``reservation_no``, ``solo_yes``,
   ``solo_no``, ``throw_yes``, ``throw_no``, ``pigs_yes``, ``pigs_no``, ``superpigs_yes``,
   ``superpigs_no``, ``poverty_yes``, ``poverty_no``, ``poverty_accept``, ``poverty_decline``,
   ``poverty_return``, ``wedding_yes``, ``wedding_no``, ``wedding_clarification_trick``,
   ``re``, ``kontra``, ``no90``, ``no_60``, ``no30``, ``black``, ``pig``, ``superpig``

.. note::
   Following types require data:
   ``solo_yes``: ``type`` (the type of the solo),
   ``poverty_return``: ``amount`` (the amount of trumps returned to the poverty player``
   ``wedding_clarification_trick``: ``trick`` (the trick the bride wishes to determine the re party)

The server conveys following data to all the clients: ::

   {
      "announcer":"453b1c0c-4742-4ba7-9d42-6f4acec1856a",
      "type":"pig",
      "data":{},
   }

``announcer`` is the :term:`UUID` of the player who made the announcement.

``type`` and ``data`` are similar to arguments the server received.
