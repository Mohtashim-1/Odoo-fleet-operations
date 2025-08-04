from odoo import fields, models, api
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class SystemIntegration(models.Model):
    _name = 'system.integration'
    _description = 'System Integration'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # For chatter and tracking

    name = fields.Char(string='Integration Name', required=True, tracking=True)
    system_type = fields.Selection(
        [
            ('najm', 'Najm Portal'),
            ('absher', 'Absher Platform'),
            ('insurance', 'Insurance System'),
        ],
        string='System Type',
        required=True,
        tracking=True,
    )
    api_url = fields.Char(string='API URL', required=True, tracking=True)
    api_key = fields.Char(string='API Key', required=True, tracking=True)
    last_sync_date = fields.Datetime(string='Last Sync Date', tracking=True)
    status = fields.Selection(
        [
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('error', 'Error'),
        ],
        string='Status',
        default='inactive',
        tracking=True,
    )
    error_message = fields.Text(string='Error Message', tracking=True)
    sync_log_ids = fields.One2many('system.integration.log', 'integration_id', string='Sync Logs')

    def action_sync_data(self):
        """Sync data from external system based on system type."""
        for record in self:
            try:
                if record.system_type == 'najm':
                    record._sync_najm_data()
                elif record.system_type == 'absher':
                    record._sync_absher_data()
                elif record.system_type == 'insurance':
                    record._sync_insurance_data()
                record.write({
                    'last_sync_date': fields.Datetime.now(),
                    'status': 'active',
                    'error_message': False,
                })
                record._log_sync('Success', 'Data synchronized successfully.')
            except Exception as e:
                error_msg = str(e)
                record.write({
                    'status': 'error',
                    'error_message': error_msg,
                })
                record._log_sync('Error', error_msg)
                _logger.error(f"Integration {record.name} failed: {error_msg}")
                raise UserError(f"Failed to sync {record.name}: {error_msg}")

    def _sync_najm_data(self):
        """Sync accident reports from Najm portal."""
        # Placeholder for Najm API call
        response = self._make_api_call(self.api_url, {'key': self.api_key})
        for report in response.get('reports', []):
            vehicle = self.env['vehicle.profile'].search([('chassis_number', '=', report.get('chassis_number'))], limit=1)
            if vehicle:
                receipt_delivery = self.env['vehicle.receipt.delivery'].search([
                    ('vehicle_id', '=', vehicle.id),
                    ('accident_reported', '=', False),
                ], limit=1)
                if receipt_delivery:
                    receipt_delivery.write({
                        'accident_reported': True,
                        'traffic_report': self._create_attachment(report.get('report_url'), 'Najm Report'),
                        'legal_notified': True,
                    })
                    vehicle.vehicle_status = 'under_maintenance'

    def _sync_absher_data(self):
        """Sync vehicle data and violations from Absher platform."""
        # Placeholder for Absher API call
        response = self._make_api_call(self.api_url, {'key': self.api_key})
        for vehicle_data in response.get('vehicles', []):
            vehicle = self.env['vehicle.profile'].search([('chassis_number', '=', vehicle_data.get('chassis_number'))], limit=1)
            if vehicle:
                vehicle.write({
                    'registration_validity': vehicle_data.get('registration_expiry'),
                    'plate_number': vehicle_data.get('plate_number'),
                })

    def _sync_insurance_data(self):
        """Sync insurance coverage details."""
        # Placeholder for Insurance API call
        response = self._make_api_call(self.api_url, {'key': self.api_key})
        for insurance_data in response.get('policies', []):
            vehicle = self.env['vehicle.profile'].search([('chassis_number', '=', insurance_data.get('chassis_number'))], limit=1)
            if vehicle:
                vehicle.write({
                    'insurance_company': insurance_data.get('company_name'),
                    'insurance_policy_number': insurance_data.get('policy_number'),
                    'insurance_expiry': insurance_data.get('expiry_date'),
                })

    def _make_api_call(self, url, params):
        """Make API call to external system (placeholder)."""
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise UserError(f"API call failed: {str(e)}")

    def _create_attachment(self, url, name):
        """Create attachment from URL (placeholder)."""
        # Placeholder for downloading and creating attachment
        attachment = self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'datas': 'data:application/pdf;base64,...',  # Replace with actual data
            'res_model': 'vehicle.receipt.delivery',
            'res_id': 0,
        })
        return attachment.id

    def _log_sync(self, result, message):
        """Log sync activity."""
        self.env['system.integration.log'].create({
            'integration_id': self.id,
            'date': fields.Datetime.now(),
            'result': result,
            'message': message,
        })

class SystemIntegrationLog(models.Model):
    _name = 'system.integration.log'
    _description = 'System Integration Log'

    integration_id = fields.Many2one('system.integration', string='Integration', required=True, ondelete='cascade')
    date = fields.Datetime(string='Date', default=fields.Datetime.now, required=True)
    result = fields.Selection(
        [
            ('success', 'Success'),
            ('error', 'Error'),
        ],
        string='Result',
        required=True,
    )
    message = fields.Text(string='Message', required=True)