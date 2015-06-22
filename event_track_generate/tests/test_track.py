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

from openerp.tests.common import TransactionCase


class TrainingTrackCase(TransactionCase):
    """Test behavior of training tracks."""

    def test_duration_type_set(self):
        """Set a duration type in a track that has no one."""

        track = self.env.ref("website_event_track.event_track30")
        duration_type = self.env.ref("training.duration_type_online")

        track.duration_type_id = duration_type

        self.assertEqual(track.duration_type_id, duration_type)

    def test_duration_type_unset(self):
        """Remove a duration type from a track that has one."""

        track = self.env.ref("website_event_track.event_track20")

        track.duration_type_id = False

        self.assertFalse(track.duration_type_id)

    def test_duration_type_change(self):
        """Change a duration type to another one."""

        track = self.env.ref("website_event_track.event_track21")
        duration_type = self.env.ref("training.duration_type_on_site")

        track.duration_type_id = duration_type

        self.assertEqual(track.duration_type_id, duration_type)
