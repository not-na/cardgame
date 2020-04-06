
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
|Valid Modes            |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, a player can make an announcement. This announcement will be sent to
all the other players. This packet is only available for the game :term:`Doppelkopf`\ .

This packet will be used to answer to a *Vorbehalt*\ , *solo*\ , *Schmeissen*\ , *Schweinchen*\ ,
*Superschweine*\ , *Hyperschweine*\ , *Armut* and *Hochzeit*\ . In case of a *Hochzeit*\ , it will
convey the clarification trick and in case of an *Armut*\ , it will be used to tell the
amount of returned trumps.
As the game goes along, it will be used to announce *Re* and *Kontra* as well as denials
like *Unter 90* etc. Furthermore, it will be used to announce a *Schweinchen*\ . In case of
an accusation with external misconduct it will be used to transmit the votes of the players.

.. seealso::
   See :doc:`../../doppelkopf/rules` for further information on special rules.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the client to the server: ::

   {
      "type":"armut_return_choice",
      "data":{"amount":3},
   }

``type`` is the context in which the announcement is made.

``data`` is an optional argument transmitting further information if required.

.. todo::
   Document the various types and data that are possible.

The server conveys following data to all the clients: ::

   {
      "announcer":"453b1c0c-4742-4ba7-9d42-6f4acec1856a",
      "type":"schweinchen",
      "data":{},
   }

``announcer`` is the :term:`UUID` of the player who made the announcement.

``type`` and ``data`` are similar to arguments the server received.
