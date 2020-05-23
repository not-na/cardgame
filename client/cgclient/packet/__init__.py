#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  __init__.py
#  
#  Copyright 2020 contributors of cardgame
#  
#  This file is part of cardgame.
#
#  cardgame is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  cardgame is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with cardgame.  If not, see <http://www.gnu.org/licenses/>.
#


def register_default_packets(reg, peer, cg, add):
    cg.info("Registering packets")

    def r(name: str, packet):
        add(name, packet(reg, peer, c=cg))

    # AUTH CONNECTION STATE

    from . import auth_precheck
    # Auth Precheck Packet
    r("cg:auth.precheck", auth_precheck.AuthPrecheckPacket)

    from . import auth
    # Auth Packet
    r("cg:auth", auth.AuthPacket)

    # STATUS PACKETS

    from . import status_user
    # Status User Packet
    r("cg:status.user", status_user.StatusUserPacket)

    from . import status_message
    # Status Message Packet
    r("cg:status.message", status_message.StatusMessagePacket)

    # LOBBY PACKETS
    from . import lobby

    # Lobby Create Packet
    r("cg:lobby.create", lobby.create.CreatePacket)

    # Lobby Join Packet
    r("cg:lobby.join", lobby.join.JoinPacket)

    # Lobby Change Packet
    r("cg:lobby.change", lobby.change.ChangePacket)

    # Lobby Ready Packet
    r("cg:lobby.ready", lobby.ready.ReadyPacket)

    # Lobby Invite Packet
    r("cg:lobby.invite", lobby.invite.InvitePacket)

    # Lobby Invite Accept Packet
    r("cg:lobby.invite.accept", lobby.invite_accept.InviteAcceptPacket)

    # Lobby Kick Packet
    r("cg:lobby.kick", lobby.kick.KickPacket)

    # Lobby Leave Packet
    r("cg:lobby.leave", lobby.leave.LeavePacket)

    # GAME PACKETS

    from . import game_start

    # Game Starting Packet
    r("cg:game.start", game_start.GameStartPacket)

    from . import game_end

    # Game Ending Packet
    r("cg:game.end", game_end.GameEndPacket)

    # GAME DK PACKETS
    from . import game_dk

    # Request an answer from a client
    r("cg:game.dk.question", game_dk.question.QuestionPacket)

    # Make an announcement
    r("cg:game.dk.announce", game_dk.announce.AnnouncePacket)

    # Do something with a card
    r("cg:game.dk.card.intent", game_dk.card_intent.CardIntentPacket)

    # Transfer a card
    r("cg:game.dk.card.transfer", game_dk.card_transfer.CardTransferPacket)

    # Point out a wrong move
    r("cg:game.dk.complaint", game_dk.complaint.ComplaintPacket)

    # Turn update
    r("cg:game.dk.turn", game_dk.turn.TurnPacket)

    # Update the scoreboard
    r("cg:game.dk.scoreboard", game_dk.scoreboard.ScoreboardPacket)

    # Update data on the round
    r("cg:game.dk.round.change", game_dk.round_change.RoundChangePacket)
