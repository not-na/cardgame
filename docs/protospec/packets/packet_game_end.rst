
``cg:game.end`` - End game
==============================

.. cg:packet:: cg:game.end

This packet is used to end the game.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.end`                    |
+-----------------------+--------------------------------------------+
|Direction              |Clientbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``game_*``                                  |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used to end the game, either when the predefined amount of rounds has been
reached or when all players decide to exit the game early.

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent by the server: ::

   {
      "next_state": "results"
   }

``next_state`` can either be ``results`` if the game has been ended properly, or ``lobby`` if it was ended
abruptly.
