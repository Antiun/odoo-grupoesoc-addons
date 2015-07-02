# -*- encoding: utf-8 -*-

# Odoo, Open Source Management Solution
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from openerp import api, fields, models


class Generator(models.TransientModel):
    _inherit = "event_track_generate.generator"

    available_duration_type_ids = fields.Many2many(
        "training.duration_type",
        compute="_compute_available_duration_type_ids",
        store=True)
    duration_type_id = fields.Many2one(
        "training.duration_type",
        "Training hour type",
        domain="[('id', 'in', available_duration_type_ids[0][2])]",
        help="Training hour type of generated tracks, if they belong to a "
             "training group.")
    event_is_training = fields.Boolean(
        compute="_compute_event_is_training",
        store=True)

    @api.one
    @api.depends("event_id")
    def _compute_available_duration_type_ids(self):
        """Get the list of available duration types.

        This list is a :class:`~fields.Many2many`, which in the client side
        has a value like ``[6, False, [<list-of-ids>]]``, that's why
        :attr:`.duration_type_id` has that weird domain.
        """
        self.available_duration_type_ids = self.event_id.mapped(
            'training_action_id.duration_ids.type_id')

    @api.one
    @api.depends("event_id")
    def _compute_event_is_training(self):
        """Know if the related event is a training group."""
        self.event_is_training = bool(self.event_id.training_action_id)

    @api.one
    def create_track(self, **values):
        """Create tracks with duration type."""
        values.setdefault("duration_type_id", self.duration_type_id.id)
        super(Generator, self).create_track(**values)
