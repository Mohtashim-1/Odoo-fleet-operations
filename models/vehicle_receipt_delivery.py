from odoo import fields, models, api
from odoo.exceptions import ValidationError

class VehicleReceiptDelivery(models.Model):
    _name = 'vehicle.receipt.delivery'
    _description = 'Vehicle Receipt and Delivery'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # For chatter and tracking

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('vehicle.receipt.delivery') or '/')
    type = fields.Selection(
        [
            ('receipt', 'Receipt'),
            ('delivery', 'Delivery'),
        ],
        string='Type',
        required=True,
        tracking=True,
    )
    vehicle_id = fields.Many2one('vehicle.profile', string='Vehicle Number', required=True, tracking=True)
    contract_id = fields.Many2one('sale.order', string='Trip / Contract Number', tracking=True)
    client_name = fields.Char(string='Client / Entity Name', tracking=True)
    location = fields.Char(string='Location', required=True, tracking=True)
    staff_id = fields.Many2one('hr.employee', string='Staff Name', required=True, tracking=True)
    datetime = fields.Datetime(string='Date and Time', required=True, default=fields.Datetime.now, tracking=True)
    
    # Inspection fields (common for receipt and delivery)
    body_condition = fields.Selection(
        [
            ('intact', 'Intact'),
            ('scratches', 'Scratches'),
            ('dents', 'Dents'),
        ],
        string='Body Condition',
        tracking=True,
    )
    tire_condition = fields.Char(string='Tire Condition', tracking=True)
    glass_lights_condition = fields.Char(string='Glass & Lights Condition', tracking=True)
    odometer_reading = fields.Float(string='Odometer Reading (km)', tracking=True)
    fuel_level = fields.Selection(
        [
            ('full', 'Full'),
            ('three_quarters', 'Three Quarters'),
            ('half', 'Half'),
            ('quarter', 'Quarter'),
            ('empty', 'Empty'),
        ],
        string='Fuel Level',
        tracking=True,
    )
    cleanliness = fields.Char(string='Cleanliness (Interior & Exterior)', tracking=True)
    
    # Document fields
    vehicle_photos = fields.Many2many('ir.attachment', string='Vehicle Photos', tracking=True)
    odometer_photo = fields.Many2one('ir.attachment', string='Odometer Photo', tracking=True)
    fuel_level_photo = fields.Many2one('ir.attachment', string='Fuel Level Photo', tracking=True)
    accident_report = fields.Many2one('ir.attachment', string='Accident Report', tracking=True)
    maintenance_report = fields.Many2one('ir.attachment', string='Maintenance Report', tracking=True)
    receipt_form = fields.Many2one('ir.attachment', string='Signed Receipt Form', tracking=True)
    
    # Delivery-specific fields
    documentation_complete = fields.Boolean(string='Complete Documentation', tracking=True,
                                           help="Registration, insurance, driver permit if applicable")
    pre_delivery_inspection_report = fields.Many2one('ir.attachment', string='Pre-Delivery Inspection Report', tracking=True)
    
    # Accident/damage handling
    accident_reported = fields.Boolean(string='Accident Reported', tracking=True)
    traffic_report = fields.Many2one('ir.attachment', string='Najm/Traffic Report', tracking=True)
    legal_notified = fields.Boolean(string='Legal/Insurance Department Notified', tracking=True)
    
    # Signature
    signature = fields.Binary(string='Receiving Party Signature', tracking=True)
    signature_date = fields.Date(string='Signature Date', default=fields.Date.today, tracking=True)
    
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )

    @api.constrains('vehicle_id', 'type')
    def _check_vehicle_status(self):
        for record in self:
            if record.type == 'delivery' and record.vehicle_id.vehicle_status != 'ready':
                raise ValidationError(
                    f"Vehicle {record.vehicle_id.name} is not ready for delivery. Current status: {record.vehicle_id.vehicle_status}."
                )
            if record.type == 'receipt' and record.accident_reported:
                record.vehicle_id.vehicle_status = 'under_maintenance'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.receipt.delivery') or '/'
        return super(VehicleReceiptDelivery, self).create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})
        if self.type == 'delivery':
            self.vehicle_id.vehicle_status = 'with_client'
        elif self.type == 'receipt' and not self.accident_reported:
            self.vehicle_id.vehicle_status = 'ready'
        
        # Create trip profile when vehicle receipt/delivery is confirmed
        self._create_trip_profile()
    
    def _create_trip_profile(self):
        """Create a trip profile when vehicle receipt/delivery is confirmed"""
        for record in self:
            # Check if trip profile already exists for this vehicle receipt/delivery
            existing_trip = self.env['trip.profile'].search([
                ('vehicle_receipt_delivery_id', '=', record.id)
            ], limit=1)
            
            if not existing_trip:
                # Create new trip profile
                trip_vals = {
                    'name': self.env['ir.sequence'].next_by_code('trip.profile') or '/',
                    'trip_type': 'individual',
                    'service_type': 'with_driver' if record.type == 'delivery' else 'without_driver',
                    'departure_datetime': record.datetime,
                    'expected_arrival_datetime': record.datetime,  # Can be updated later
                    'driver_id': record.staff_id.id if record.staff_id else False,
                    'trip_status': 'confirm',
                    'notes': f"Auto-created from {record.type} - {record.name}",
                    'vehicle_receipt_delivery_id': record.id,
                    'customer_id': record.contract_id.partner_id.id if record.contract_id else False,
                    'location_from': record.location,
                    'location_to': record.location,
                    'booking_type': 'with_driver',  # Required field
                    'region': 'central',  # Required field - default to central
                }
                
                trip_profile = self.env['trip.profile'].create(trip_vals)
                
                # Create vehicle line for the trip
                vehicle_line_vals = {
                    'trip_id': trip_profile.id,
                    'vehicle_id': False,  # No direct link to fleet.vehicle from vehicle.profile
                    'driver_id': record.staff_id.id if record.staff_id else False,
                    'car_plate_no': record.vehicle_id.name if record.vehicle_id else '',
                    'start_date': record.datetime,
                    'end_date': record.datetime,
                }
                
                self.env['trip.vehicle.line'].create(vehicle_line_vals)

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})
        if self.type == 'delivery':
            self.vehicle_id.vehicle_status = 'ready'

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.odometer_reading = self.vehicle_id.odometer_reading
            self.client_name = self.contract_id.partner_id.name if self.contract_id else False