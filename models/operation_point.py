from odoo import fields, models, api
from odoo.exceptions import ValidationError

class OperationPoint(models.Model):
    _name = 'operation.point'
    _description = 'Operation Point'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # For chatter and tracking

    name = fields.Char(string='Operation Point Name',  tracking=True)
    point_type = fields.Selection(
        [
            ('direct_branch', 'Direct Branch'),
            ('temporary_branch', 'Temporary Branch (By Contract)'),
        ],
        string='Type',
        tracking=True,
    )
    address = fields.Char(string='Full Address', tracking=True)
    google_map_location = fields.Char(string='Google Map Location', tracking=True)
    contract_duration = fields.Char(string='Contract Duration', tracking=True, help="For temporary branches, specify the duration (e.g., 6 months).")
    vehicle_ids = fields.One2many('vehicle.profile', 'branch_id', string='Assigned Vehicles',
                                  domain=[('vehicle_status', '=', 'ready')])
    vehicle_count = fields.Integer(string='Number of Vehicles Assigned', compute='_compute_vehicle_count', store=True)
    responsible_employee_id = fields.Many2one('hr.employee', string='Responsible Employee / Branch Manager',
                                              tracking=True)
    working_hours = fields.Char(string='Working Hours', tracking=True, help="e.g., 08:00-17:00")
    available_services = fields.Many2many(
        'operation.service',
        string='Available Services',
        help="Services like Delivery, Return, Light Maintenance",
    )
    status = fields.Selection(
        [
            ('active', 'Active'),
            ('temporary', 'Temporary'),
            ('closed', 'Closed'),
        ],
        string='Status',
        default='active',
        tracking=True,
    )
    warehouse_id = fields.Many2one('warehouse.profile', string='Linked Warehouse', tracking=True)
    location_id = fields.Many2one('stock.location', string='Location', tracking=True)


    
    department_id = fields.Many2one('hr.department', string='Supervisory Department', tracking=True)

    @api.depends('vehicle_ids')
    def _compute_vehicle_count(self):
        for point in self:
            point.vehicle_count = len(point.vehicle_ids)

    @api.constrains('point_type', 'contract_duration')
    def _check_contract_duration(self):
        for point in self:
            if point.point_type == 'temporary_branch' and not point.contract_duration:
                raise ValidationError("Contract duration is required for temporary branches.")

    @api.model
    def _get_active_points(self):
        """Return active operation points for trip assignments."""
        return self.search([('status', 'in', ['active', 'temporary'])])