from odoo import fields, models, api

class VehicleProfile(models.Model):
    _name = 'vehicle.profile'
    _description = 'Vehicle Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # For chatter and tracking

    name = fields.Char(string='Vehicle Reference', required=True, tracking=True)
    ownership = fields.Selection(
        [
            ('ds_rent', 'DS Rent'),
            ('vendor_x', 'Vendor X'),
            ('vehicle_supplier', 'Vehicle Supplier'),
        ],
        string='Ownership',
        required=True,
        tracking=True,
    )
    warehouse_id = fields.Many2one('warehouse.profile', string='Linked Warehouse', tracking=True)
    chassis_number = fields.Char(string='Chassis Number', required=True, tracking=True)
    plate_number = fields.Char(string='Plate Number', required=True, tracking=True)
    vehicle_type = fields.Selection(
        [
            ('sedan', 'Sedan'),
            ('suv', 'SUV'),
            ('van', 'Van'),
            ('other', 'Other'),
        ],
        string='Vehicle Type',
        required=True,
        tracking=True,
    )
    make_model = fields.Char(string='Make and Model', required=True, tracking=True)
    manufacture_year = fields.Integer(string='Year of Manufacture', tracking=True)
    odometer_reading = fields.Float(string='Current Odometer Reading (km)', tracking=True)
    fuel_type = fields.Selection(
        [
            ('petrol', 'Petrol'),
            ('diesel', 'Diesel'),
            ('electric', 'Electric'),
        ],
        string='Fuel Type',
        required=True,
        tracking=True,
    )
    engine_number = fields.Char(string='Engine Number', tracking=True)
    vehicle_color = fields.Char(string='Vehicle Color', tracking=True)
    operation_start_date = fields.Date(string='Start of Operation Date', tracking=True)
    vehicle_status = fields.Selection(
        [
            ('ready', 'Ready'),
            ('under_maintenance', 'Under Maintenance'),
            ('with_client', 'With Client'),
            ('out_of_service', 'Out of Service'),
        ],
        string='Vehicle Status',
        default='ready',
        required=True,
        tracking=True,
    )
    registration_validity = fields.Date(string='Registration Validity', tracking=True)
    insurance_company = fields.Char(string='Insurance Company', tracking=True)
    insurance_policy_number = fields.Char(string='Policy Number', tracking=True)
    insurance_expiry = fields.Date(string='Insurance Expiry Date', tracking=True)
    last_maintenance_date = fields.Date(string='Last Scheduled Maintenance', tracking=True)
    branch_id = fields.Many2one('operation.point', string='Current Branch/Operation Point', tracking=True)

    @api.constrains('vehicle_status')
    def _check_vehicle_status(self):
        """Ensure only 'Ready' vehicles are available for trips."""
        for vehicle in self:
            if vehicle.vehicle_status != 'ready':
                # This can be linked to trip validation later
                pass

    @api.model
    def _get_ready_vehicles(self):
        """Return vehicles available for trip assignments."""
        return self.search([('vehicle_status', '=', 'ready')])