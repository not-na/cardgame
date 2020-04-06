
``cg:game.dk.scoreboard`` - Update the scoreboard
=================================================

.. cg:packet:: cg:game.dk.scoreboard

This packet is used to update points and pips. It is only used for the game
:term:`Doppelkopf`\ .

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.dk.scoreboard`          |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``game_dk`` only                            |
+-----------------------+--------------------------------------------+

Purpose
-------

Using this packet, the server updates points and pips that players have. This packet is
only available for the game :term:`Doppelkopf`\ .

After each trick, the packet will convey the pips all players received. At the
end of each game and in case of a penalty, the packet will convey the points all the players
received.

Structure
---------

Note that all examples shown here contain placeholder data and will have different
content in actual packets.

This is the data sent by the server to the client: ::

   {
      "player":"dabb43c0-2854-4cb8-aee0-3c3db3a54244",
      "pips":25
      "pip_change":15
      "points":-5
      "point_change":0
   }

``player`` is the :term:`UUID` of the concerned player.

``pips`` is the amount of pips the player has accumulated in this round.

``pip_change`` is the amount of pips the player gained with the last trick.

``points`` is the amount of points the player has accumulated in the play.

``point_change`` is the amount of points the player gained with the last game.

.. note::
   Both ``point_change`` and ``pip_change`` may be zero if nothing has changed.