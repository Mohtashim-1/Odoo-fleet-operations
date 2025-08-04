from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    show_fleet_operations = fields.Boolean(
        string='Show Fleet Operations',
        default=False,
        compute='_compute_show_fleet_operations',
        store=False,
        help='Check this box to show Fleet Operations menu to this user'
    )
    
    def _compute_show_fleet_operations(self):
        """Compute the field value based on group membership"""
        fleet_user_group = self.env.ref('fleet_operations.group_fleet_operations_user', raise_if_not_found=False)
        fleet_manager_group = self.env.ref('fleet_operations.group_fleet_operations_manager', raise_if_not_found=False)
        
        for user in self:
            user.show_fleet_operations = (
                (fleet_user_group and fleet_user_group in user.groups_id) or
                (fleet_manager_group and fleet_manager_group in user.groups_id)
            )
    
    @api.onchange('show_fleet_operations')
    def _onchange_show_fleet_operations(self):
        """Handle checkbox changes to assign/unassign groups"""
        fleet_user_group = self.env.ref('fleet_operations.group_fleet_operations_user', raise_if_not_found=False)
        fleet_manager_group = self.env.ref('fleet_operations.group_fleet_operations_manager', raise_if_not_found=False)
        
        for user in self:
            if user.show_fleet_operations:
                # Add user to fleet operations user group
                if fleet_user_group and fleet_user_group not in user.groups_id:
                    user.groups_id = [(4, fleet_user_group.id)]
            else:
                # Remove user from fleet operations groups
                if fleet_user_group and fleet_user_group in user.groups_id:
                    user.groups_id = [(3, fleet_user_group.id)]
                if fleet_manager_group and fleet_manager_group in user.groups_id:
                    user.groups_id = [(3, fleet_manager_group.id)]
    
 