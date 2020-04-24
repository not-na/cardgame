
CardGame Multiplayer Protocol Specification
===========================================

TODO

Protocol Specification Index
----------------------------

.. toctree::
   :maxdepth: 1

   cards
   doppelkopf/rules
   doppelkopf/penalties

   packets/auth
   packets/status
   packets/party
   packets/lobby
   packets/game
   packets/ping

Packets
^^^^^^^

.. toctree::
   :maxdepth: 1

   packets/packet_auth
   packets/packet_auth_precheck

   packets/packet_status_user
   packets/packet_status_message
   packets/packet_status_server_mainscreen

   packets/lobby/packet_lobby_create
   packets/lobby/packet_lobby_join
   packets/lobby/packet_lobby_invite
   packets/lobby/packet_lobby_invite_accept
   packets/lobby/packet_lobby_change
   packets/lobby/packet_lobby_leave
   packets/lobby/packet_lobby_kick
   packets/lobby/packet_lobby_ready

   packets/party/packet_party_create
   packets/party/packet_party_join
   packets/party/packet_party_invite
   packets/party/packet_party_invite_accept
   packets/party/packet_party_change
   packets/party/packet_party_leave
   packets/party/packet_party_kick

   packets/packet_game_start

   packets/game_dk/packet_game_dk_question
   packets/game_dk/packet_game_dk_announce
   packets/game_dk/packet_game_dk_card_intent
   packets/game_dk/packet_game_dk_card_transfer
   packets/game_dk/packet_game_dk_complaint
   packets/game_dk/packet_game_dk_turn
   packets/game_dk/packet_game_dk_round_change
   packets/game_dk/packet_game_dk_scoreboard