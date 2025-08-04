from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date

class ContractCollection(models.Model):
    _name = 'contract.collection'
    _description = 'Contract Collection'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # For chatter and tracking

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('contract.collection') or '/')
    contract_id = fields.Many2one('sale.order', string='Contract Number', required=True, tracking=True)
    client_id = fields.Many2one('res.partner', string='Client / Contracting Entity', related='contract_id.partner_id',
                                store=True, tracking=True)
    contract_type = fields.Selection(
        [
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        string='Contract Type',
        required=True,
        tracking=True,
    )
    start_date = fields.Date(string='Start Date', required=True, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    total_value = fields.Float(string='Total Contract Value', required=True, tracking=True)
    payment_line_ids = fields.One2many('contract.payment.line', 'collection_id', string='Scheduled Payments')
    collection_status = fields.Selection(
        [
            ('on_time', 'On Time'),
            ('partially_overdue', 'Partially Overdue'),
            ('fully_overdue', 'Fully Overdue'),
            ('on_hold', 'On Hold'),
            ('escalation_needed', 'Escalation Needed'),
        ],
        string='Collection Status',
        compute='_compute_collection_status',
        store=True,
        tracking=True,
    )
    communication_ids = fields.One2many('contract.communication', 'collection_id', string='Communication & Follow-up')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments',
                                      help="Contract copy, payment proofs, email/WhatsApp logs, financial documents")

    @api.depends('payment_line_ids.status', 'payment_line_ids.due_date')
    def _compute_collection_status(self):
        today = date.today()
        for record in self:
            payment_lines = record.payment_line_ids
            if not payment_lines:
                record.collection_status = 'on_time'
                continue
            overdue = any(line.status == 'overdue' for line in payment_lines)
            all_overdue = all(line.status == 'overdue' for line in payment_lines if line.due_date < today)
            on_hold = any(line.status == 'on_hold' for line in payment_lines)
            escalation = any(line.status == 'escalation_needed' for line in payment_lines)
            
            if escalation:
                record.collection_status = 'escalation_needed'
            elif on_hold:
                record.collection_status = 'on_hold'
            elif all_overdue:
                record.collection_status = 'fully_overdue'
            elif overdue:
                record.collection_status = 'partially_overdue'
            else:
                record.collection_status = 'on_time'

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date < record.start_date:
                raise ValidationError('End date must be after start date.')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('contract.collection') or '/'
        return super(ContractCollection, self).create(vals_list)

    @api.onchange('contract_id')
    def _onchange_contract_id(self):
        if self.contract_id:
            self.start_date = self.contract_id.date_order
            self.total_value = self.contract_id.amount_total
            self.client_id = self.contract_id.partner_id

class ContractPaymentLine(models.Model):
    _name = 'contract.payment.line'
    _description = 'Contract Payment Line'

    collection_id = fields.Many2one('contract.collection', string='Collection', required=True, ondelete='cascade')
    installment = fields.Integer(string='Installment', required=True)
    due_date = fields.Date(string='Due Date', required=True)
    amount_required = fields.Float(string='Required', required=True)
    amount_paid = fields.Float(string='Paid')
    actual_payment_date = fields.Date(string='Actual Payment Date')
    payment_method = fields.Selection(
        [
            ('bank_transfer', 'Bank Transfer'),
            ('cash', 'Cash'),
            ('credit_card', 'Credit Card'),
            ('other', 'Other'),
        ],
        string='Method',
    )
    status = fields.Selection(
        [
            ('paid', 'Paid'),
            ('overdue', 'Overdue'),
            ('on_hold', 'On Hold'),
            ('escalation_needed', 'Escalation Needed'),
        ],
        string='Status',
        compute='_compute_status',
        store=True,
    )
    notes = fields.Text(string='Notes')

    @api.depends('amount_paid', 'amount_required', 'due_date')
    def _compute_status(self):
        today = date.today()
        for line in self:
            if line.amount_paid >= line.amount_required:
                line.status = 'paid'
            elif line.due_date and line.due_date < today and line.amount_paid < line.amount_required:
                line.status = 'overdue'
            else:
                line.status = 'on_hold'

    @api.constrains('amount_paid', 'amount_required')
    def _check_amounts(self):
        for line in self:
            if line.amount_paid > line.amount_required:
                raise ValidationError(
                    f"Paid amount ({line.amount_paid}) cannot exceed required amount ({line.amount_required}) "
                    f"for installment {line.installment}."
                )

class ContractCommunication(models.Model):
    _name = 'contract.communication'
    _description = 'Contract Communication'

    collection_id = fields.Many2one('contract.collection', string='Collection', required=True, ondelete='cascade')
    date = fields.Date(string='Date', required=True, default=fields.Date.today)
    method = fields.Selection(
        [
            ('phone', 'Phone'),
            ('email', 'Email'),
            ('whatsapp', 'WhatsApp'),
            ('in_person', 'In Person'),
        ],
        string='Method',
        required=True,
    )
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    result = fields.Text(string='Result')
    recommendation = fields.Text(string='Recommendation')