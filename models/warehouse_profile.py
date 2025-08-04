from odoo import fields, models, api
from odoo.exceptions import ValidationError

class WarehouseProfile(models.Model):
    _name = 'warehouse.profile'
    _description = 'Warehouse Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # For chatter and tracking

    name = fields.Char(string='Warehouse Name', required=True, tracking=True)
    location = fields.Char(string='Geographic Location / Address', required=True, tracking=True)
    identifier = fields.Char(string='Warehouse Identifier', required=True, copy=False,
                            default=lambda self: self.env['ir.sequence'].next_by_code('warehouse.profile') or '/')
    vehicle_capacity = fields.Integer(string='Vehicle Capacity', required=True, tracking=True)
    available_vehicle_ids = fields.One2many('vehicle.profile', 'warehouse_id', string='Currently Available Vehicles',
                                           domain=[('vehicle_status', '=', 'ready')])
    vehicle_count = fields.Integer(string='Available Vehicle Count', compute='_compute_vehicle_count', store=True)
    daily_movement = fields.Text(string='Daily In/Out Vehicle Movement', tracking=True)
    warehouse_type = fields.Selection(
        [
            ('main', 'Main'),
            ('sub', 'Sub'),
            ('contracted', 'Contracted'),
        ],
        string='Warehouse Type',
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one('hr.department', string='Supervisory Department', tracking=True)
    establishment_date = fields.Date(string='Establishment / Contract Date', tracking=True)
    operational_status = fields.Selection(
        [
            ('active', 'Active'),
            ('under_maintenance', 'Under Maintenance'),
            ('inactive', 'Inactive'),
        ],
        string='Operational Status',
        default='active',
        required=True,
        tracking=True,
    )

    @api.depends('available_vehicle_ids')
    def _compute_vehicle_count(self):
        for warehouse in self:
            warehouse.vehicle_count = len(warehouse.available_vehicle_ids)

    @api.constrains('vehicle_capacity', 'vehicle_count')
    def _check_vehicle_capacity(self):
        for warehouse in self:
            if warehouse.vehicle_count > warehouse.vehicle_capacity:
                raise ValidationError(
                    f"Warehouse {warehouse.name} exceeds capacity: {warehouse.vehicle_count} vehicles "
                    f"assigned, but capacity is {warehouse.vehicle_capacity}."
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('identifier', '/') == '/':
                vals['identifier'] = self.env['ir.sequence'].next_by_code('warehouse.profile') or '/'
        return super(WarehouseProfile, self).create(vals_list)