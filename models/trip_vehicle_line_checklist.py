from odoo import models, api, fields
from odoo.exceptions import ValidationError, AccessError, UserError

class TripVehicleLineChecklist(models.Model):
    _name = 'trip.vehicle.line.checklist'
    _description = 'Checklist'

    trip_vehicle_line_id = fields.Many2one('trip.vehicle.line', string="Sale Order Line")
    name = fields.Char(string="Checklist Name", required=True)
    checklist_line_ids = fields.One2many('trip.vehicle.line.checklist.line', 'checklist_id', string="Checklist Items")


class TripVehicleLineChecklistLine(models.Model):
    _name = 'trip.vehicle.line.checklist.line'
    _description = 'Checklist Line Item'
    def _get_item_description_selection(self):
        return [
            ('registration_book', 'Registration Book'),
            ('wipers', 'Wipers'),
            ('rear_view_mirror', 'Rear View Mirror'),
            ('spare_tire_tools', 'Spare Tire & Tools'),
            ('number_plates', 'Number Plates'),
            ('door_locks', 'Door Locks'),
            ('head_lights', 'Head Lights'),
            ('indicators', 'Indicators'),
            ('speedometer', 'Speedometer'),
            ('hubs', 'Hubs'),
            ('tires', 'Tires'),
            ('remote', 'Remote'),
            ('loqo_sticker', 'Loqo Sticker'),
            ('head_seat', 'Head Seat'),
            ('clean_interior', 'Clean Interior'),
            ('clean_exterior', 'Clean Exterior'),
            ('ash_tray', 'Ash Tray Cigarate Lighter'),
            ('audio_system', 'Audio System'),
            ('seat_belts', 'Seat Belts'),
            ('air_condition', 'Air Condition'),
            ('hub_caps', 'Hub Caps'),
            ('engine_oil', 'Engine Oil'),
            ('brakes', 'Brakes'),
        ]

    checklist_id = fields.Many2one('trip.vehicle.line.checklist', string="Checklist", required=True, ondelete='cascade')

    item_description = fields.Selection(selection=_get_item_description_selection, string="Checklist Item", required=True)
    in_status = fields.Boolean(string="In (OK)", default=False)
    out_status = fields.Boolean(string="Out (OK)", default=False)
    remarks = fields.Text(string="Remarks")