from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import date

class OperationsDashboard(models.Model):
    _name = 'operations.dashboard'
    _description = 'Operations Dashboard'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # For chatter and tracking

    name = fields.Char(string='Dashboard Reference', required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('operations.dashboard') or '/')
    date = fields.Date(string='Date', default=fields.Date.today, required=True, tracking=True)
    
    # Vehicle KPIs
    total_vehicles = fields.Integer(string='Total Vehicles', compute='_compute_vehicle_kpis', store=True)
    ready_vehicles = fields.Integer(string='Ready Vehicles', compute='_compute_vehicle_kpis', store=True)
    under_maintenance_vehicles = fields.Integer(string='Under Maintenance Vehicles', compute='_compute_vehicle_kpis', store=True)
    out_of_service_vehicles = fields.Integer(string='Out of Service Vehicles', compute='_compute_vehicle_kpis', store=True)
    readiness_percentage = fields.Float(string='Readiness %', compute='_compute_vehicle_kpis', store=True)
    
    # Trip KPIs
    trip_count = fields.Integer(string='Trip Count', compute='_compute_trip_kpis', store=True)
    scheduled_trips = fields.Integer(string='Scheduled Trips', compute='_compute_trip_kpis', store=True)
    ongoing_trips = fields.Integer(string='Ongoing Trips', compute='_compute_trip_kpis', store=True)
    completed_trips = fields.Integer(string='Completed Trips', compute='_compute_trip_kpis', store=True)
    
    # Contract KPIs
    active_contracts = fields.Integer(string='Active Contracts', compute='_compute_contract_kpis', store=True)
    shortage_contracts = fields.Integer(string='Contracts with Shortages', compute='_compute_contract_kpis', store=True)
    
    # Warehouse KPIs
    warehouse_vehicle_count = fields.Integer(string='Vehicles in Warehouses', compute='_compute_warehouse_kpis', store=True)
    warehouse_distribution = fields.Text(string='Warehouse Distribution', compute='_compute_warehouse_kpis', store=True)
    
    # Operation Point KPIs
    operation_point_vehicle_count = fields.Integer(string='Vehicles at Operation Points', compute='_compute_operation_point_kpis', store=True)
    
    # Receipt and Delivery KPIs
    ongoing_receipts_deliveries = fields.Integer(string='Ongoing Receipts/Deliveries', compute='_compute_receipt_delivery_kpis', store=True)
    avg_delivery_time = fields.Float(string='Avg. Delivery Time (hours)', compute='_compute_receipt_delivery_kpis', store=True)
    
    # Alerts and Shortages
    shortage_requests = fields.Integer(string='Vehicle Shortage Requests', compute='_compute_alerts', store=True)
    damage_alerts = fields.Integer(string='Damage/Najm Reports', compute='_compute_alerts', store=True)
    alert_messages = fields.Text(string='Alerts', compute='_compute_alerts', store=True)
    
    @api.depends('date')
    def _compute_vehicle_kpis(self):
        for dashboard in self:
            vehicles = self.env['vehicle.profile'].search([])
            dashboard.total_vehicles = len(vehicles)
            dashboard.ready_vehicles = len(vehicles.filtered(lambda v: v.vehicle_status == 'ready'))
            dashboard.under_maintenance_vehicles = len(vehicles.filtered(lambda v: v.vehicle_status == 'under_maintenance'))
            dashboard.out_of_service_vehicles = len(vehicles.filtered(lambda v: v.vehicle_status == 'out_of_service'))
            dashboard.readiness_percentage = (
                (dashboard.ready_vehicles / dashboard.total_vehicles * 100) if dashboard.total_vehicles else 0
            )

    @api.depends('date')
    def _compute_trip_kpis(self):
        for dashboard in self:
            trips = self.env['trip.profile'].search([('departure_datetime', '>=', dashboard.date)])
            dashboard.trip_count = len(trips)
            dashboard.scheduled_trips = len(trips.filtered(lambda t: t.trip_status == 'scheduled'))
            dashboard.ongoing_trips = len(trips.filtered(lambda t: t.trip_status == 'departed'))
            dashboard.completed_trips = len(trips.filtered(lambda t: t.trip_status == 'completed'))

    @api.depends('date')
    def _compute_contract_kpis(self):
        for dashboard in self:
            contracts = self.env['contract.collection'].search([
                ('start_date', '<=', dashboard.date),
                ('end_date', '>=', dashboard.date),
            ])
            dashboard.active_contracts = len(contracts)
            dashboard.shortage_contracts = len(contracts.filtered(
                lambda c: any(line.driver_shortage > 0 for line in c.mapped('contract_id.trip_ids.vehicle_line_ids'))
            ))

    @api.depends('date')
    def _compute_warehouse_kpis(self):
        for dashboard in self:
            warehouses = self.env['warehouse.profile'].search([])
            dashboard.warehouse_vehicle_count = sum(warehouse.vehicle_count for warehouse in warehouses)
            distribution = '\n'.join(
                f"{w.name}: {w.vehicle_count} vehicles" for w in warehouses
            )
            dashboard.warehouse_distribution = distribution or 'No vehicles in warehouses.'

    @api.depends('date')
    def _compute_operation_point_kpis(self):
        for dashboard in self:
            points = self.env['operation.point'].search([])
            dashboard.operation_point_vehicle_count = sum(point.vehicle_count for point in points)

    @api.depends('date')
    def _compute_receipt_delivery_kpis(self):
        for dashboard in self:
            receipts_deliveries = self.env['vehicle.receipt.delivery'].search([
                ('datetime', '>=', dashboard.date),
                ('state', 'in', ['confirmed', 'done']),
            ])
            dashboard.ongoing_receipts_deliveries = len(receipts_deliveries.filtered(lambda r: r.state == 'confirmed'))
            delivery_times = [
                (r.datetime - r.vehicle_id.operation_start_date).total_seconds() / 3600
                for r in receipts_deliveries.filtered(lambda r: r.type == 'delivery' and r.vehicle_id.operation_start_date)
            ]
            dashboard.avg_delivery_time = sum(delivery_times) / len(delivery_times) if delivery_times else 0

    @api.depends('date')
    def _compute_alerts(self):
        for dashboard in self:
            trips = self.env['trip.profile'].search([('departure_datetime', '>=', dashboard.date)])
            shortages = sum(len(line) for line in trips.mapped('vehicle_line_ids') if line.driver_shortage > 0)
            damages = len(self.env['vehicle.receipt.delivery'].search([
                ('datetime', '>=', dashboard.date),
                ('accident_reported', '=', True),
            ]))
            alerts = []
            if shortages:
                alerts.append(f"Vehicle Shortages: {shortages} requests pending.")
            if damages:
                alerts.append(f"Damage/Najm Reports: {damages} incidents reported.")
            dashboard.shortage_requests = shortages
            dashboard.damage_alerts = damages
            dashboard.alert_messages = '\n'.join(alerts) or 'No active alerts.'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('operations.dashboard') or '/'
        return super(OperationsDashboard, self).create(vals_list)