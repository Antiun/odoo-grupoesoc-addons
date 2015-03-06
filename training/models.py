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

from openerp import _, api, fields, models
from . import exceptions


# Current module domain
_D = "training.%s"


class DurationType(models.Model):
    """Types of the training actions' durations.

    See docs for :class:`~.ActionType`.
    """

    _name = _D % "duration_type"

    name = fields.Char(required=True, index=True, translate=True)

    duration_ids = fields.One2many(
        _D % "duration",
        "type_id",
        "Epected hours of this type",
        help="Expected hours of this type defined in training actions.")

    action_type_ids = fields.Many2many(
        _D % "action_type",
        string="Training action types",
        help="Training action types that expect this hour type.")

    _sql_constraints = [("unique_name",
                         "UNIQUE(name)",
                         "Name must be unique.")]


class Duration(models.Model):
    _name = _D % "duration"

    duration = fields.Float(default=0, required=True)

    type_id = fields.Many2one(
        _D % "duration_type",
        "Type of hours",
        required=True)

    action_id = fields.Many2one(
        _D % "action",
        "Training action",
        required=True)

    @api.one
    @api.constrains("type_id", "action_id")
    def check_right_duration_types(self):
        """Check that the hour types are the right ones."""

        expected_types = (self.action_id.type_id
                          .expected_duration_type_ids)

        if expected_types and self.type_id not in expected_types:
            raise exceptions.WrongDurationType(
                self.type_id,
                expected_types)

    _sql_constraints = [("training_vs_hours_unique",
                         "UNIQUE(type_id, action_id)",
                         "Cannot repeat the hour type in a training action.")]


class ActionType(models.Model):
    """Types of training actions.

    Depending on the training action type, a training action may expect some
    type of hours. For example:

    - If a training action's type is "on-site", it expects on-site hours.
    - If its type is "online", it expects online hours.
    - If its type is "mixed", it expects both on-site and online hours.

    You can configure it as you wish.
    """

    _name = _D % "action_type"

    name = fields.Char(required=True, index=True, translate=True)

    action_ids = fields.One2many(
        _D % "action",
        "type_id",
        "Training actions",
        help="Training actions of this type.")

    expected_duration_type_ids = fields.Many2many(
        _D % "duration_type",
        string="Expected hour types",
        help="These types of hours are expected in this type of training "
             "action. For example, a training of type 'mixed' may expect "
             "hours of types 'on-site' and 'online'.")

    _sql_constraints = [("unique_name",
                         "UNIQUE(name)",
                         "Name must be unique.")]


class Action(models.Model):
    """Define training actions.

    A training action is one course that your company teaches and has in its
    catalog of courses.

    They define some requirements that the corresponding event is expected to
    fulfill. Events linked to training actions are considered training groups.
    """

    _name = _D % "action"

    name = fields.Char(required=True, index=True, translate=True)

    type_id = fields.Many2one(
        _D % "action_type",
        "Training type")

    duration_ids = fields.One2many(
        _D % "duration",
        "action_id",
        "Expected hours",
        help="Expected duration of each type of hours for these training "
             "groups.")

    @api.onchange("type_id")
    def fulfill_expected_duration_types(self):
        """When choosing a type of training action, fulfill the expected hours.

        There will be 0 hours of each type by default.
        """

        # Remove invalid hour expectations
        valid_duration_types = self.type_id.expected_duration_type_ids
        for duration in self.duration_ids:
            if duration.duration_type_id not in valid_duration_types:
                self.duration_ids -= duration

        # Add new hour expectations
        current_duration_types = self.mapped("duration_ids.type_id")
        for duration_type in self.type_id.expected_duration_type_ids:
            if duration_type not in current_duration_types:
                self.duration_ids |= self.duration_ids.new(
                    {"duration_type_id": duration_type.id})


class Event(models.Model):
    """Expand events with training actions.

    Events with a training type and a training action are considered training
    groups.
    """

    _inherit = "event.event"

    training_action_id = fields.Many2one(
        _D % "action",
        "Training action",
        help="Training action of this event, if it is a course.")

    tutor_ids = fields.Many2many(
        "res.partner",
        string="Tutors",
        help="Teachers that are supposed to oversee every track. These will "
             "be available for students to ask them their doubts.")
