#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  cg_ext.py
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

# Based on https://www.sphinx-doc.org/en/master/development/tutorials/recipe.html

from collections import defaultdict

from docutils.parsers.rst import directives

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain
from sphinx.domains import Index
from sphinx.roles import XRefRole
from sphinx.util.nodes import make_refnode


class PacketDirective(ObjectDescription):
    """A custom directive that describes a packet."""

    has_content = True
    required_arguments = 1
    option_spec = {
        'contains': directives.unchanged_required,
    }

    def handle_signature(self, sig, signode):
        signode += addnodes.desc_name(text=sig)
        return sig

    def add_target_and_index(self, name_cls, sig, signode):
        signode['ids'].append('packet' + '-' + sig)
        if 'noindex' not in self.options:
            #ingredients = [
            #    x.strip() for x in self.options.get('contains').split(',')]

            cg = self.env.get_domain('cg')
            cg.add_packet(sig, [])


class PacketIndex(Index):
    """A custom index that creates an recipe matrix."""

    name = 'packet'
    localname = 'Packet Index'
    shortname = 'Packet'

    def generate(self, docnames=None):
        content = defaultdict(list)

        # sort the list of recipes in alphabetical order
        packets = self.domain.get_objects()
        packets = sorted(packets, key=lambda p: p[0])

        # generate the expected output, shown below, from the above using the
        # first letter of the recipe as a key to group thing
        #
        # name, subtype, docname, anchor, extra, qualifier, description
        for name, dispname, typ, docname, anchor, _ in packets:
            content[dispname[0].lower()].append(
                (dispname, 0, docname, anchor, docname, '', typ))

        # convert the dict to the sorted list of tuples expected
        content = sorted(content.items())

        return content, True


class CardgameDomain(Domain):

    name = 'cg'
    label = 'CardGame'
    roles = {
        'packet': XRefRole()
    }
    directives = {
        'packet': PacketDirective,
    }
    indices = {
        PacketIndex,
    }
    initial_data = {
        'packets': [],  # object list
    }

    def get_full_qualified_name(self, node):
        return '{}.{}'.format('packet', node.arguments[0])

    def get_objects(self):
        for obj in self.data['packets']:
            yield(obj)

    def resolve_xref(self, env, fromdocname, builder, typ, target, node,
                     contnode):
        match = [(docname, anchor)
                 for name, sig, typ, docname, anchor, prio
                 in self.get_objects() if sig == target]

        if len(match) > 0:
            todocname = match[0][0]
            targ = match[0][1]

            return make_refnode(builder, fromdocname, todocname, targ,
                                contnode, targ)
        else:
            print('Awww, found nothing')
            return None

    def add_packet(self, signature, d):
        """Add a new packet to the domain."""
        name = '{}.{}'.format('packet', signature)
        anchor = 'packet-{}'.format(signature)

        #self.data['recipe_ingredients'][name] = ingredients
        # name, dispname, type, docname, anchor, priority
        self.data['packets'].append(
            (name, signature, 'Packet', self.env.docname, anchor, 0))


def setup(app):
    app.add_domain(CardgameDomain)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }