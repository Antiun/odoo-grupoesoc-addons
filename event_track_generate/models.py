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

from datetime import datetime, timedelta
from pytz import timezone
from openerp import api, fields, models
from . import exceptions


class Generator(models.TransientModel):
    _name = "event_track_generate.generator"

    event_id = fields.Many2one(
        "event.event",
        string="Event",
        default=lambda self:
            self.env["event.event"].browse(self.env.context["active_id"]),
        required=True)
    event_date_begin = fields.Datetime(
        related="event_id.date_begin",
        help="Change it in the event form. "
             "No tracks before this date will be generated.")
    event_date_end = fields.Datetime(
        related="event_id.date_end",
        help="Change it in the event form. "
             "No tracks after this date will be generated.")
    event_date_tz = fields.Selection(
        related="event_id.date_tz",
        help="Change it in the event form. Timezone of the generated tracks.")
    name = fields.Char(
        "Track title",
        required=True,
        help="Title that will be assigned to all created tracks.")
    location_id = fields.Many2one("event.track.location", "Location")
    speaker_ids = fields.Many2many(
        "res.partner",
        string="Speakers",
        relation="event_track_generate_generator_speaker_ids")
    tag_ids = fields.Many2many(
        "event.track.tag",
        string="Tags",
        relation="event_track_generate_generator_tag_ids")
    mondays = fields.Boolean(help="Create tracks on Mondays.")
    tuesdays = fields.Boolean(help="Create tracks on Tuesdays.")
    wednesdays = fields.Boolean(help="Create tracks on Wednesdays.")
    thursdays = fields.Boolean(help="Create tracks on Thursdays.")
    fridays = fields.Boolean(help="Create tracks on Fridays.")
    saturdays = fields.Boolean(help="Create tracks on Saturdays.")
    sundays = fields.Boolean(help="Create tracks on Sundays.")
    start_time = fields.Float(
        required=True,
        help="Each track will start at this time (in the event's timezone).")
    duration = fields.Float(
        required=True,
        help="Each track will have this duration.")
    end_time = fields.Float(
        compute="_compute_end_time",
        help="Each track will end at this time.")
    delete_existing_tracks = fields.Boolean()
    publish_tracks_in_website = fields.Boolean()
    adjust_start_time = fields.Boolean(
        default=True,
        help="Make event's start time match the start of the first track.")
    adjust_end_time = fields.Boolean(
        default=True,
        help="Make event's end time match the end of the last track.")

    @api.one
    @api.depends("start_time", "duration")
    def _compute_end_time(self):
        self.end_time = self.start_time + self.duration

    @api.one
    def action_generate(self):
        """Generate event tracks according to received data."""
        # You need at least one weekday
        weekdays = self.weekdays()[0]
        if True not in weekdays:
            raise exceptions.NoWeekdaysError()

        # Delete existing
        if self.delete_existing_tracks:
            self.event_id.track_ids.exists().unlink()

        # Create new
        self.generate_tracks()

        # Adjust event's dates
        self.adjust_dates()

    @api.one
    def adjust_dates(self):
        """Adjust event dates if asked to do so."""
        # Cheek if the user wanted to adjust dates
        if self.event_id.track_ids.exists() and (self.adjust_start_time or
                                                 self.adjust_end_time):
            sorted_ = self.event_id.track_ids.sorted(lambda r: r.date)

            # Start date
            if self.adjust_start_time:
                self.event_id.date_begin = sorted_[0].date

            # End date
            if self.adjust_end_time:
                self.event_id.date_end = fields.Datetime.to_string(
                    fields.Datetime.from_string(sorted_[-1].date) +
                    timedelta(seconds=sorted_[-1].duration * 60 * 60))

    @api.one
    def create_track(self, **values):
        """Create a new track record with the provided values."""
        data = {
            "name": self.name,
            "event_id": self.event_id.id,
            "duration": self.duration,
            "location_id": self.location_id.id,
            "speaker_ids": [(6, False, self.speaker_ids.ids)],
            "tag_ids": [(6, False, self.tag_ids.ids)],
            "user_id": self.event_id.user_id.id,
            "website_published": self.publish_tracks_in_website}
        data.update(values)
        return self.env["event.track"].create(data)

    @api.one
    def datetime_fields(self):
        """Fields converted to Python's Datetime-based objects."""
        result = {
            "event_start": fields.Datetime.from_string(self.event_date_begin),
            "event_end": fields.Datetime.from_string(self.event_date_end),
            "duration_delta": timedelta(seconds=self.duration * 60 * 60),
            "day_delta": timedelta(days=1),
            "start_time":
                datetime.min + timedelta(seconds=self.start_time * 60 * 60),
        }

        # Needed to manually fix timezone offset, for start_time
        result["tzdiff"] = (timezone(self.event_id.date_tz or
                                     self.env.context["tz"] or
                                     self.env.user.tz or
                                     "UTC")
                            .utcoffset(result["event_start"]))
        return result

    @api.one
    def existing_tracks(self, date):
        """Return existing tracks that match some criteria."""
        return self.env["event.track"].search(
            (("event_id", "=", self.event_id.id),
             ("date", "=", date),
             ("duration", "=", self.duration)))

    @api.one
    def generate_tracks(self):
        """Know which tracks must be generated and do it."""
        counter = 0
        dt = self.datetime_fields()[0]
        weekdays = self.weekdays()[0]

        # Check that tracks fit between event start and end dates
        current = dt["event_start"]
        while current <= dt["event_end"]:
            # Get start date and time with fixed timezone offset
            current_start = datetime.combine(
                current.date(),
                dt["start_time"].time()) - dt["tzdiff"]
            if (current_start >= dt["event_start"] and
                    weekdays[current.weekday()]):
                current_end = current_start + dt["duration_delta"]
                if current_end <= dt["event_end"]:
                    # Need string for the ORM
                    current_start = fields.Datetime.to_string(current_start)

                    # Check that no track exists with this data
                    if not self.existing_tracks(current_start)[0]:
                        self.create_track(date=current_start)
                        counter += 1

            # Next day
            current += dt["day_delta"]

    @api.one
    def weekdays(self):
        """Sorted weekdays user selection."""
        return (self.mondays,
                self.tuesdays,
                self.wednesdays,
                self.thursdays,
                self.fridays,
                self.saturdays,
                self.sundays)
