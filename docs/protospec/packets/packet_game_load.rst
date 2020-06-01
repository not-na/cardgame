
``cg:game.load`` - Load game
============================

.. cg:packet:: cg:game.load

This packet is used to load a game upon continuing an old game.

+-----------------------+--------------------------------------------+
|Internal Name          |:cg:packet:`cg:game.load`                   |
+-----------------------+--------------------------------------------+
|Direction              |Serverbound                                 |
+-----------------------+--------------------------------------------+
|Since Version          |v0.1.0                                      |
+-----------------------+--------------------------------------------+
|Valid States           |``lobby``                                   |
+-----------------------+--------------------------------------------+

Purpose
-------

This packet is used, when a player in a lobby loads an old game. It conveys the game data
to the server so that the server can load this game. The other clients in the lobby will only
receive the game data with the :cg:packet:`cg:game.start` packet

Structure
---------

Note that all examples shown here contain placeholder data and will have different content in actual packets.

This is the data sent to the server: ::

   {
      "game_id": "e8d1e1e2-75c8-4225-ab1a-16dabcc260d1",
      "data": {
         "id": "e8d1e1e2-75c8-4225-ab1a-16dabcc260d1"
         "type": "dk",
         "creation_time": 1591004154.1594243,
         "players": [
            "acb8fa68-5c22-42cc-a4fa-1ba600dcdb9e", "c4db1dfe-9d6c-41c2-9a88-ea7c641738a6",
            "d940a7e4-c19a-4904-abcf-71aab689da11", "ac5085ad-148d-4838-b800-dba3c6a5c91c"
         ],
         "gamerules": {
            "dk.etc": ["and", "so", "on"]
         },
         "round_num": 3,
         "buckrounds": [],
         "scores": [[-3, 3, 3, -3], [2, 2, 2, -6], [5, -5, 5, -5]],
         "current_points": [4, 0, 10, -14],
         "game_summaries": [
            ["re_win", "re"],
            ["kontra_win", "no90"],
            ["kontra_win", "kontra", "no90", "against_cqs"]
         ]
      }
   }

``game_id`` is the game's :term:`UUID`\.

``data`` is a dictionary containing the data of the saved game. It should contain following keys:

``id``\: see ``game_id``

``type`` The game type. It can be ``dk`` (Doppelkopf), ``sk`` (Skat), ``cn`` (Canasta) and ``rm`` (Rummy).

``creation_time`` is the system time at which the game was created.

``players`` is a list of the :term:`UUID`\s of the players.

``gamerules`` is a dictionary containing the game's gamerules.

``round_num`` is the amount of rounds, that have already been played.

``buckrounds`` is a list of the buckrounds, that still have to be played. Its exact structure depends on the buckround
gamerules.

``scores`` is a list containing lists for each round. In these lists, the scores for the round are saved.

``curront_points`` is a list containing the current scores for the players.

``game_summaries`` is a list containing the game summaries for all rounds.
