from odoo import fields, models, api
from odoo.exceptions import ValidationError

class VehicleShortage(models.Model):
    _name = 'vehicle.shortage'
    _description = 'Vehicle Shortage Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # For chatter and tracking

    name = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('vehicle.shortage') or '/')
    trip_id = fields.Many2one('trip.profile', string='Trip', tracking=True)
    contract_id = fields.Many2one('sale.order', string='Contract', tracking=True)
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
    requested_quantity = fields.Integer(string='Requested Quantity', required=True, tracking=True)
    available_quantity = fields.Integer(string='Available Quantity', compute='_compute_available_quantity', store=True)
    shortage_quantity = fields.Integer(string='Shortage Quantity', compute='_compute_shortage_quantity', store=True)
    driver_shortage = fields.Integer(string='Driver Shortage', tracking=True)
    request_date = fields.Date(string='Request Date', default=fields.Date.today, required=True, tracking=True)
    warehouse_id = fields.Many2one('warehouse.profile', string='Source Warehouse', tracking=True)
    operation_point_id = fields.Many2one('operation.point', string='Operation Point', tracking=True)
    status = fields.Selection(
        [
            ('draft', 'Draft'),
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('resolved', 'Resolved'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    resolution_action = fields.Selection(
        [
            ('reduce_quantity', 'Reduce Quantity'),
            ('alternative_vehicle', 'Alternative Vehicle Type'),
            ('inter_branch_transfer', 'Request Reinforcement'),
            ('notify_team', 'Notify Operations Team'),
        ],
        string='Resolution Action',
        tracking=True,
    )
    alternative_vehicle_type = fields.Selection(
        [
            ('sedan', 'Sedan'),
            ('suv', 'SUV'),
            ('van', 'Van'),
            ('other', 'Other'),
        ],
        string='Alternative Vehicle Type',
        tracking=True,
    )
    transfer_warehouse_id = fields.Many2one('warehouse.profile', string='Transfer From Warehouse', tracking=True)
    notes = fields.Text(string='Notes', tracking=True)

    @api.depends('vehicle_type', 'warehouse_id')
    def _compute_available_quantity(self):
        for record in self:
            if record.vehicle_type and record.warehouse_id:
                available_vehicles = self.env['vehicle.profile'].search_count([
                    ('vehicle_type', '=', record.vehicle_type),
                    ('vehicle_status', '=', 'ready'),
                    ('warehouse_id', '=', record.warehouse_id.id),
                ])
                record.available_quantity = available_vehicles
            else:
                record.available_quantity = 0

    @api.depends('requested_quantity', 'available_quantity')
    def _compute_shortage_quantity(self):
        for record in self:
            record.shortage_quantity = max(0, record.requested_quantity - record.available_quantity)

    @api.constrains('requested_quantity', 'available_quantity')
    def _check_shortage(self):
        for record in self:
            if record.shortage_quantity <= 0 and record.status not in ['resolved', 'rejected']:
                raise ValidationError(
                    f"No shortage for {record.vehicle_type}: Requested {record.requested_quantity}, "
                    f"Available {record.available_quantity}."
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.shortage') or '/'
        return super(VehicleShortage, self).create(vals_list)

    def action_submit(self):
        self.write({'status': 'pending'})
        self.message_post(body='Shortage request submitted for review.')

    def action_approve(self):
        self.write({'status': 'approved'})
        self.message_post(body='Shortage request approved.')
        if self.resolution_action == 'notify_team':
            # Placeholder for notifying operations team (e.g., via email or activity)
            self.env['mail.activity'].create({
                'res_model_id': self.env['ir.model']._get('vehicle.shortage').id,
                'res_id': self.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': 'Resolve Vehicle Shortage',
                'user_id': self.env.user.id,
            })

    def action_reject(self):
        self.write({'status': 'rejected'})
        self.message_post(body='Shortage request rejected.')

    def action_resolve(self):
        self.write({'status': 'resolved'})
        self.message_post(body='Shortage request resolved.')