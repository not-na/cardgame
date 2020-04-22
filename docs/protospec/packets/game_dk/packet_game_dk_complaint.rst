
``cg:game.dk.complaint`` - Point out a wrong move
=================================================

.. cg:packet:: cg:game.dk.complaint

This packet is used to point out a mistake another player has made. It is only used for
the game :term:`Doppelkopf`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.dk.complaint`           |
+-----------------------+--------------------------------------------+
|Direction              |Bidirectional                               |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, a player can denounce a mistake by another player. This packet is
only available for the game :term:`Doppelkopf`\ .

This packet is used when a player makes a mistake by accident or deliberately and another
player denounces this mistake. First, the denouncing player has to accuse, which player
made the mistake and choose the type of the misconduct.
In case of an accusation with *wrong card* or *wrong announcement*, he will receive a
list of all the cards the accused player played and all the announcements he made. The
accusing player must choose from this list, which move was illegal.
In case of an accusation with *played early*, the server will check whether the last card
of the accused player was played before it was his turn.
If the accusation proves to be wrong or if the accusing player decides to cancel the
accusation, he will receive a penalty himself. Otherwise, the accused player will be
punished and the game might be aborted, depending on the penalty settings.

The mistake can also emanate from a chat or voice chat. Since the server cannot automatically
arbitrate such a complaint, the two other players have to confirm it using a
:cg:packet:`cg:game.dk.question` and a :cg:packet:`cg:game.dk.announce` packet. If 3 of
the 4 players back the accusation, the punishment will be undergone by the accused,
otherwise by the accuser.

.. note::
   If the punished player ought to receive demerit points, the :cg:packet:`cg:game.dk.scoreboard`
   will be used.

.. seealso::
   See :doc:`../../doppelkopf/penalties` for further information on penalty settings.

Structure
---------

Note that all examples shown here contain placeholder data and will have different
content in actual packets.

This is the data sent by the client to the server: ::

   {
      "accused":"e421c337-70f6-409a-bdcf-acf1b3c3c6e0",
      "type":"wrong_announcement",
   }

``accused`` is the :term:`UUID` of the accused player.

``type`` is the misconduct the accused is charged with.

.. note::
   Type can have following arguments: ``wrong_card``, ``wrong_announcement``, ``played_early``,
   ``external``

In case of an accusation with ``wrong_card`` or ``wrong_announcement``, the server will
reply like this: ::

   {
      "moves":{
         0:{
            "type":"announcement",
            "data":"reservation_no",
         },
         4:{
            "type":"announcement",
            "data":"kontra",
         },
         5:{
            "type":"card",
            "data":"cq",
         },
         ...
      },
      "accused": "e421c337-70f6-409a-bdcf-acf1b3c3c6e0",
      "type": "wrong_announcement",
   }

``moves`` is a dictionary containing all the moves the player has done so far. Each move is
represented by its move-ID, beginning in each round with 0 and counting up for each announcement
made and each card played. The ID is followed by a dictionary declaring its ``type`` (``announcement``, ``card``
or ``accusation``) and ``data`` specifying the kind of the announcement or the value of the card.

.. note::
   Only the accuser will receive the ``moves`` field. All other clients will still get all
   other fields, however.

The client will respond with the following data: ::

   {
      "accused":"e421c337-70f6-409a-bdcf-acf1b3c3c6e0",
      "type":"wrong_announcement",
      "move":{
         "98fd442d-4ee0-4d96-bf51-12917e36a001":{"type":"announcement", "data":"kontra"},
      },
   }

``accused`` and ``type`` remain the same as in the first packet.

``move`` is the move representing the misconduct, stored as described above.
