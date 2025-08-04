from odoo import models, api, fields
from odoo.exceptions import ValidationError, AccessError, UserError
from datetime import timedelta

class TripProfile(models.Model):
    _name = 'trip.profile'
    _description = 'Trip Profile'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Override to prevent email sending
    def _notify_get_groups(self, msg_vals=None):
        """Override to disable email notifications"""
        return []
    
    def _notify_get_recipients_groups(self, msg_vals=None):
        """Override to disable email notifications"""
        return []

    name = fields.Char(string='Trip Number', required=True, copy=False, readonly=True,
                       default=lambda self: self.env['ir.sequence'].next_by_code('trip.profile') or '/')
    
    # customer_id = fields.Many2one('res.partner', string='Customer')
    trip_type = fields.Selection([
        ('contract', 'Contract'),
        ('individual', 'Individual')
    ], string='Trip Type',tracking=True)

    service_type = fields.Selection([
        ('with_driver', 'With Driver'),
        ('without_driver', 'Without Driver')
    ], string='Service Type',  tracking=True)

    departure_datetime = fields.Datetime(string='Departure Date and Time',  tracking=True)
    expected_arrival_datetime = fields.Datetime(string='Expected Arrival Date and Time',  tracking=True)
    departure_point_id = fields.Many2one('operation.point', string='Departure Point',  tracking=True)
    arrival_point_id = fields.Many2one('operation.point', string='Arrival Point',  tracking=True)
    driver_id = fields.Many2one('hr.employee', string='Driver/Responsible Employee', tracking=True)

    

    trip_status = fields.Selection([
        ('confirm', 'confirm'),
        ('scheduled', 'Scheduled'),
        ('departed', 'Departed'),
        ('completed', 'Completed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled')
    ], string='Trip Status', default='confirm', tracking=True)
    
    sync_vehicle_done = fields.Boolean(string='Sync Vehicle Done', default=False, tracking=True)

    notes = fields.Text(string='Additional Notes', tracking=True)
    contract_id = fields.Many2one('sale.order', string='Contract', tracking=True)

    contract_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], string='Contract Type', tracking=True)

    contract_start_date = fields.Date(string='Contract Start Date', tracking=True)
    contract_end_date = fields.Date(string='Contract End Date', tracking=True)
    vehicle_line_ids = fields.One2many('trip.vehicle.line', 'trip_id', string='Vehicle Lines')
    booking_id = fields.Many2one('car.booking', string='Car Booking', ondelete='restrict', copy=False)
    vehicle_receipt_delivery_id = fields.Many2one('vehicle.receipt.delivery', string='Vehicle Receipt/Delivery', copy=False)

    customer_id = fields.Many2one('res.partner', string='Customer')
    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')
    project_id = fields.Many2one('project.project', string='Project')

    # region = fields.Selection([
    #     ('central', 'Central'),
    #     ('eastern', 'Eastern'),
    #     ('western', 'Western'),
    #     ('northern', 'Northern'),
    #     ('southern', 'Southern')
    # ], string='Region')

    # city_id = fields.Many2one('booking.city', string='City')

    # booking_type = fields.Selection([
    #     ('airport', 'Airport'),
    #     ('hotel', 'Hotel'),
    #     ('business', 'Business'),
    #     ('tour', 'Tour')
    # ], string='Booking Type')

    guest_id = fields.Many2one('res.partner', string='Guest')
    # guest_phone = fields.Char(string='Guest Phone')



        # ---------------------------------------------------------------------
    # Basic Information (taken from your XML)
    # ---------------------------------------------------------------------
    booking_type = fields.Selection([
        ('with_driver', 'Car with Driver(Limousine)'),
        ('rental',      'Rental')
    ], string='Type of Booking', required=True)

    invoice_id = fields.Many2one(
        'account.move',
        string='Invoice',
        readonly=True,
        copy=False
    )

    # ---------------------------------------------------------------------
    # Location / Branch
    # ---------------------------------------------------------------------
    region = fields.Selection([
        ('north',   'North'),
        ('south',   'South'),
        ('west',    'West'),
        ('east',    'East'),
        ('central', 'Central'),
    ], string='Region', required=True)

    city = fields.Many2one(
        'booking.city',
        string='City',
        domain="[('region', '=', region)]"
    )

    location_id = fields.Many2one(
        'stock.location',
        string='Branch',
        domain="[('usage', '=', 'internal')]"
    )

    # ---------------------------------------------------------------------
    # Booking Details
    # ---------------------------------------------------------------------
    # name = fields.Char(string='Booking Ref')
    # car_booking_id = fields.Many2one('car.booking', string='Car Booking')
    customer_ref_number = fields.Char(string='Customer Ref Number')

    business_type = fields.Selection([
        ('corporate',   'Corporate'),
        ('hotels',      'Hotels'),
        ('government',  'Government'),
        ('individuals', 'Individuals'),
        ('rental',      'Rental'),
        ('others',      'Others'),
    ], string='Business Type')

    customer_name = fields.Many2one(
        'res.partner',
        string='Customer Name'
    )
    guest_name = fields.Many2one(
        'res.partner',
        string='Guest Name'
    )

    reservation_status = fields.Selection([
        ('created',          'Created'),
        ('invoice_released', 'Invoice Released'),
        ('paid',             'Paid'),
        ('active',           'Active'),
        ('finished',         'Finished'),
        ('cancelled',        'Cancelled'),
    ], string='Reservation Status', readonly=True)

    flight_number = fields.Char(string='Flight Number')

    mobile       = fields.Char(string='Customer Phone')
    guest_phone  = fields.Char(string='Guest Phone')
    hotel_room_number = fields.Char(string='Hotel Room Number')

    # ---------------------------------------------------------------------
    # Service & Attachments
    # ---------------------------------------------------------------------
    date_of_service = fields.Date(string='Date of Service')

    payment_type = fields.Selection([
        ('cash',          'Cash'),
        ('credit',        'Credit'),
        ('bank_transfer', 'Bank Transfer'),
        ('atm',           'ATM'),
        ('cheque',        'Cheque'),
        ('others',        'Others'),
    ], string='Payment')

    attachment_ids = fields.Many2many(
        'ir.attachment',
        'trip_profile_ir_attachments_rel',   # custom M2M table name
        'trip_profile_id',
        'attachment_id',
        string='Attachments',
        domain="[('res_model', '=', 'trip.profile')]",
    )

    # ---------------------------------------------------------------------
    # Airport / Transfer
    # ---------------------------------------------------------------------
    # airport_id = fields.Many2one(
    #     'car.airport',
    #     string='Airport',
    #     domain="[]",
    #     copy=False,
    #     readonly=True
    # )

    location_from = fields.Char(string='Location From')
    location_to   = fields.Char(string='Location To')

    airport_id = fields.Many2one(
        'car.airport',
        string='Airport',
        domain="[]"
    )
    





    def action_sync_booking_lines(self):
        for trip in self:
            for trip_line in trip.vehicle_line_ids:
                booking_line = trip_line.car_booking_line_id
                if booking_line:
                    booking_line.write({
                        'car_year': trip_line.car_year,
                        'car_model': trip_line.car_model,
                        'driver_name': trip_line.driver_id.id,
                        'mobile_no': trip_line.driver_id.phone or '',
                        'id_no': trip_line.driver_id.x_id_number or '',
                    })

    
    def action_set_scheduled(self):
        for record in self:
            record.trip_status = 'scheduled'
            # Update car booking state if linked
            if record.booking_id:
                record.booking_id.state = 'scheduled'
    
    def action_set_departed(self):
        """Set trip status to departed with validation"""
        for record in self:
            # Validate vehicle lines before setting departed
            if record.vehicle_line_ids:
                for line in record.vehicle_line_ids:
                    if not line.vehicle_id:
                        raise ValidationError(f"Vehicle must be assigned in line '{line.name}' before setting status to Departed.")
                    if not line.driver_name:
                        raise ValidationError(f"Driver must be assigned in line '{line.name}' before setting status to Departed.")
            else:
                raise ValidationError("At least one vehicle line must exist before setting status to Departed.")
            
            record.trip_status = 'departed'

    def action_set_completed(self):
        """Set trip status to completed with validation"""
        for record in self:
            # Validate vehicle lines before setting completed
            if record.vehicle_line_ids:
                for line in record.vehicle_line_ids:
                    if not line.end_date:
                        raise ValidationError(f"End date must be set in line '{line.name}' before setting status to Completed.")
            else:
                raise ValidationError("At least one vehicle line must exist before setting status to Completed.")
            
            record.trip_status = 'completed'
            

    def action_set_cancelled(self):
        """Show confirmation dialog before cancelling the trip"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'trip.cancellation.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_trip_id': self.id,
            }
        }

    def action_create_invoice(self):
        """Create invoice from trip profile"""
        if not self.vehicle_line_ids:
            raise UserError("No vehicle lines found for this trip profile.")
        
        # Prepare invoice values
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id or self.customer_name.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': [],
        }
        
        # Set service type from the first vehicle line if available
        if self.vehicle_line_ids and self.vehicle_line_ids[0].service_type_id:
            invoice_vals['service_type'] = self.vehicle_line_ids[0].service_type_id.id
        
        # Create invoice lines from vehicle lines
        for vehicle_line in self.vehicle_line_ids:
            # Get data from vehicle line or linked car booking line
            if vehicle_line.car_booking_line_id:
                # Use data from linked car booking line
                booking_line = vehicle_line.car_booking_line_id
                price_unit = booking_line.unit_price or vehicle_line.price_unit or vehicle_line.unit_price or 0.0
                quantity = booking_line.qty or vehicle_line.quantity or vehicle_line.qty or 1.0
                extra_hour = booking_line.extra_hour or vehicle_line.extra_hour or 0
                extra_hour_charges = booking_line.extra_hour_charges or vehicle_line.extra_hour_charges or 0.0
                vehicle_name = booking_line.fleet_vehicle_id.name if booking_line.fleet_vehicle_id else vehicle_line.vehicle_id.name if vehicle_line.vehicle_id else 'Vehicle'
                driver_name = booking_line.driver_name.name if booking_line.driver_name else vehicle_line.driver_name.name if vehicle_line.driver_name else 'Driver'
                # service_type_id = booking_line.type_of_service_id.id if booking_line.type_of_service_id else vehicle_line.service_type_id.id if vehicle_line.service_type_id else False
                car_type = booking_line.car_model_id.id if booking_line.car_model_id else vehicle_line.car_model_id.id if vehicle_line.car_model_id else False
                start_date = booking_line.start_date or vehicle_line.start_date
                end_date = booking_line.end_date or vehicle_line.end_date
            else:
                # Use data from vehicle line directly
                price_unit = vehicle_line.price_unit or vehicle_line.unit_price or 0.0
                quantity = vehicle_line.quantity or vehicle_line.qty or 1.0
                extra_hour = vehicle_line.extra_hour or 0
                extra_hour_charges = vehicle_line.extra_hour_charges or 0.0
                vehicle_name = vehicle_line.vehicle_id.name if vehicle_line.vehicle_id else 'Vehicle'
                driver_name = vehicle_line.driver_name.name if vehicle_line.driver_name else 'Driver'
                # service_type_id = vehicle_line.service_type_id.id if vehicle_line.service_type_id else False
                car_type = vehicle_line.car_model_id.id if vehicle_line.car_model_id else False
                start_date = vehicle_line.start_date
                end_date = vehicle_line.end_date
            
            # Calculate total amount including extra charges
            base_amount = price_unit * quantity
            # Calculate extra charges directly
            extra_charges = extra_hour * extra_hour_charges
            total_amount = base_amount + extra_charges
            
            print(f"DEBUG: Line calculation for vehicle line {vehicle_line.id}")
            print(f"DEBUG: price_unit={price_unit}, quantity={quantity}")
            print(f"DEBUG: extra_hour={extra_hour}, extra_hour_charges={extra_hour_charges}")
            print(f"DEBUG: base_amount={base_amount}, extra_charges={extra_charges}, total_amount={total_amount}")
            print(f"DEBUG: service_type_id from vehicle_line: {vehicle_line.service_type_id}")
            print(f"DEBUG: service_type_id.id: {vehicle_line.service_type_id.id if vehicle_line.service_type_id else 'None'}")
            print(f"DEBUG: service_type_id.name: {vehicle_line.service_type_id.name if vehicle_line.service_type_id else 'None'}")
            
            # Generate a descriptive name for the invoice line
            line_name = f"Trip: {vehicle_name}"
            if driver_name and driver_name != 'Driver':
                line_name += f" - {driver_name}"
            
            # Add additional details to the line name
            if start_date and end_date:
                start_date_str = start_date.strftime('%Y-%m-%d')
                end_date_str = end_date.strftime('%Y-%m-%d')
                line_name += f" ({start_date_str} to {end_date_str})"
            
            invoice_line_vals = {
                'name': line_name,
                'quantity': quantity,
                'price_unit': price_unit,
                'price_subtotal': base_amount,  # Base amount without additional charges
                'additional_charges': extra_charges,
                # Add car booking line reference if available
                'car_booking_line_id': vehicle_line.car_booking_line_id.id if vehicle_line.car_booking_line_id else False,
                # Add service type, car type, and dates
                'service_type': vehicle_line.service_type_id.id if vehicle_line.service_type_id else False,
                'car_type': car_type,
                'date_start': start_date,
                'date_end': end_date,
            }
            print(f"DEBUG: Invoice line vals: {invoice_line_vals}")
            invoice_vals['invoice_line_ids'].append((0, 0, invoice_line_vals))
        
        # Create the invoice
        invoice = self.env['account.move'].create(invoice_vals)
        
        print(f"DEBUG: Invoice created with ID: {invoice.id}")
        print(f"DEBUG: Initial invoice amounts - Total: {invoice.amount_total}, Untaxed: {invoice.amount_untaxed}")
        
        # Manually update the line amounts to ensure additional_charges are included
        total_untaxed = 0.0
        for line in invoice.line_ids:
            print(f"DEBUG: Processing invoice line: {line.name}")
            print(f"DEBUG: Line quantity: {line.quantity}, price_unit: {line.price_unit}")
            print(f"DEBUG: Line additional_charges: {line.additional_charges}")
            print(f"DEBUG: Line original price_subtotal: {line.price_subtotal}")
            
            # Recalculate the subtotal to include additional charges
            base_subtotal = line.quantity * line.price_unit
            additional_charges = line.additional_charges or 0.0
            new_subtotal = base_subtotal + additional_charges
            
            # Update the line subtotal
            line.write({'price_subtotal': new_subtotal})
            total_untaxed += new_subtotal
            print(f"DEBUG: Line new price_subtotal: {line.price_subtotal}")
        
        # Directly update invoice totals to ensure they are correct
        invoice.write({
            'amount_untaxed': total_untaxed,
            'amount_total': total_untaxed + invoice.amount_tax
        })
        
        print(f"DEBUG: Final invoice amounts - Total: {invoice.amount_total}, Untaxed: {invoice.amount_untaxed}")
        print(f"DEBUG: Expected total: {total_untaxed}, Actual total: {invoice.amount_untaxed}")
        
        print(f"DEBUG: Final invoice amounts - Total: {invoice.amount_total}, Untaxed: {invoice.amount_untaxed}")
        
        # Link invoice to trip profile
        self.invoice_id = invoice.id
        
        # Set trip status to invoiced
        self.trip_status = 'invoiced'
        
        # Update car booking state if linked
        if self.booking_id:
            self.booking_id.state = 'invoiced'
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': invoice.id,
            'target': 'current',
            'context': self.env.context,
        }
    
    def _generate_car_booking_line_name(self, vehicle_line):
        """Generate a proper name for car booking line"""
        name_parts = []
        
        # Add car model
        if vehicle_line.car_model:
            name_parts.append(vehicle_line.car_model)
        elif vehicle_line.vehicle_id:
            name_parts.append(vehicle_line.vehicle_id.name)
        else:
            name_parts.append("Vehicle")
        
        # Add driver name
        if vehicle_line.driver_name:
            name_parts.append(f"- {vehicle_line.driver_name.name}")
        elif vehicle_line.driver_id:
            name_parts.append(f"- {vehicle_line.driver_id.name}")
        else:
            name_parts.append("- Driver")
        
        # Add dates if available
        if vehicle_line.start_date and vehicle_line.end_date:
            name_parts.append(f"({vehicle_line.start_date.strftime('%Y-%m-%d')} to {vehicle_line.end_date.strftime('%Y-%m-%d')})")
        
        return " ".join(name_parts)

    def action_view_invoice(self):
        """Open the linked invoice"""
        self.ensure_one()
        if self.invoice_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'account.move',
                'view_mode': 'form',
                'res_id': self.invoice_id.id,
                'target': 'current',
                'context': self.env.context,
            }
        return False

    def action_view_booking(self):
        """Open the linked car booking"""
        self.ensure_one()
        if self.booking_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'car.booking',
                'view_mode': 'form',
                'res_id': self.booking_id.id,
                'target': 'current',
                'context': self.env.context,
            }
        return False
    




    
    def action_sync_vehicle_details(self):
        """Sync vehicle details and guest information from trip profile to car booking lines"""
        for trip in self:
            booking = trip.booking_id
            if not booking:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Warning',
                        'message': 'No Car Booking linked to this Trip Profile.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }

            # Try to access car.booking.line model
            try:
                car_booking_line_model = self.env['car.booking.line']
            except KeyError:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Error',
                        'message': 'Car Booking module is not available. Please ensure the aw_car_booking module is installed and updated.',
                        'type': 'danger',
                        'sticky': False,
                    }
                }

            print(f"DEBUG: car.booking.line model available, checking vehicle lines")
            sync_count = 0
            linked_count = 0
            guest_sync_count = 0
            total_vehicle_lines = len(trip.vehicle_line_ids)
            booking_lines = booking.car_booking_lines
            
            print(f"DEBUG: Total vehicle lines: {total_vehicle_lines}")
            print(f"DEBUG: Total booking lines: {len(booking_lines)}")
            
            # First, unlink all vehicle lines to start fresh
            for vehicle_line in trip.vehicle_line_ids:
                if vehicle_line.car_booking_line_id:
                    print(f"DEBUG: Unlinking vehicle line from booking line: {vehicle_line.car_booking_line_id}")
                    vehicle_line.car_booking_line_id = False
            
            # Now redistribute vehicle lines to booking lines
            for i, vehicle_line in enumerate(trip.vehicle_line_ids):
                print(f"DEBUG: Processing vehicle line {i+1}: {vehicle_line.name}")
                
                # Find an available booking line (one that doesn't have a vehicle assigned)
                available_booking_lines = booking_lines.filtered(lambda bl: not bl.fleet_vehicle_id)
                print(f"DEBUG: Available booking lines (without vehicles): {len(available_booking_lines)}")
                
                if available_booking_lines:
                    # Link to the next available booking line
                    booking_line_to_link = available_booking_lines[0]
                    vehicle_line.car_booking_line_id = booking_line_to_link.id
                    linked_count += 1
                    print(f"DEBUG: Linked vehicle line to booking line: {booking_line_to_link.name}")
                elif booking_lines and i < len(booking_lines):
                    # If no available booking lines, use booking line by index
                    booking_line_to_link = booking_lines[i]
                    vehicle_line.car_booking_line_id = booking_line_to_link.id
                    linked_count += 1
                    print(f"DEBUG: Linked vehicle line to booking line by index: {booking_line_to_link.name}")
                else:
                    print(f"DEBUG: No suitable booking line found for vehicle line {i+1}")
                
                if vehicle_line.car_booking_line_id:
                    print(f"DEBUG: Vehicle line has car_booking_line_id: {vehicle_line.car_booking_line_id}")
                    booking_line = car_booking_line_model.search([
                        ('id', '=', vehicle_line.car_booking_line_id.id)
                    ], limit=1)
            
                    if booking_line:
                        print(f"DEBUG: Found booking line, updating it")
                        booking_line.write({
                            'end_date': vehicle_line.end_date,
                            'extra_hour': vehicle_line.extra_hour,
                            'fleet_vehicle_id': vehicle_line.vehicle_id.id,
                            'driver_name': vehicle_line.driver_name.id,
                            'mobile_no': vehicle_line.driver_name.customized_mobile or vehicle_line.driver_name.mobile or vehicle_line.driver_name.phone or '',
                            'id_no': vehicle_line.driver_name.national_identity_number or '',
                            'car_model': vehicle_line.car_model,
                            'car_model_id': vehicle_line.car_model_id.id if vehicle_line.car_model_id else False,
                            'car_year': vehicle_line.car_year,
                            # 'product_id': vehicle_line.product_id.id if vehicle_line.product_id else False,
                            # 'product_category_id': vehicle_line.product_category_id.id if vehicle_line.product_category_id else False,
                            # 'qty': vehicle_line.qty,
                            # 'unit_price': vehicle_line.unit_price,
                        })
                        if hasattr(booking_line, '_compute_amount_values'):
                            booking_line._compute_amount_values()
                        sync_count += 1
                        print(f"DEBUG: Updated booking line, sync_count: {sync_count}")
                    else:
                        print(f"DEBUG: Booking line not found")
                else:
                    print(f"DEBUG: Vehicle line has no car_booking_line_id")
            
            # Sync guest information from trip profile to car booking and booking lines
            if trip.guest_name:
                # Sync to main car booking
                if trip.guest_name != booking.guest_name:
                    booking.guest_name = trip.guest_name.id
                    print(f"DEBUG: Synced guest_name to car booking: {trip.guest_name.name}")
                
                # Sync to car booking lines
                for booking_line in booking.car_booking_lines:
                    if trip.guest_name not in booking_line.guest_ids:
                        guest_ids = booking_line.guest_ids.ids + [trip.guest_name.id]
                        booking_line.guest_ids = [(6, 0, guest_ids)]
                        guest_sync_count += 1
                        print(f"DEBUG: Synced guest_name to booking line {booking_line.id}: {trip.guest_name.name}")
            
            print(f"DEBUG: Sync completed, sync_count: {sync_count}, linked_count: {linked_count}, guest_sync_count: {guest_sync_count}")
            
            # Set sync_vehicle_done to True after sync is completed
            trip.sync_vehicle_done = True
            
            message = ""
            if linked_count > 0:
                message += f"Linked {linked_count} vehicle lines to car booking lines. "
            if sync_count > 0:
                message += f"Successfully synced {sync_count} vehicle details to car booking lines. "
            if guest_sync_count > 0:
                message += f"Synced guest information to {guest_sync_count} car booking lines."
            
            if not message:
                if total_vehicle_lines > 0 and len(booking.car_booking_lines) == 0:
                    message = f"No car booking lines found in the booking. Use 'Create Booking Lines' button to create booking lines from vehicle lines. Total vehicle lines: {total_vehicle_lines}"
                else:
                    message = f"No vehicle lines synced. Total vehicle lines: {total_vehicle_lines}, Booking lines: {len(booking.car_booking_lines) if booking else 0}"
            
            # Return action to reload the form
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            } 

    def action_sync_vehicle_line_data(self):
        """Sync vehicle line data from car booking lines"""
        for trip in self:
            sync_count = 0
            for vehicle_line in trip.vehicle_line_ids:
                if vehicle_line.car_booking_line_id:
                    booking_line = vehicle_line.car_booking_line_id
                    
                    # Update vehicle line with latest booking line data
                    update_vals = {
                        'vehicle_id': booking_line.fleet_vehicle_id.id if booking_line.fleet_vehicle_id else False,
                        'driver_name': booking_line.driver_name.id if booking_line.driver_name else False,
                        'car_model': booking_line.car_model,
                        'car_model_id': booking_line.car_model_id.id if booking_line.car_model_id else False,
                        'car_year': booking_line.car_year,
                        'product_id': booking_line.product_id.id if booking_line.product_id else False,
                        'product_category_id': booking_line.product_category_id.id if booking_line.product_category_id else False,
                        'qty': booking_line.qty,
                        'quantity': booking_line.qty,
                        'price_unit': booking_line.unit_price,
                        'unit_price': booking_line.unit_price,
                        'amount': booking_line.amount,
                        'start_date': booking_line.start_date,
                        'end_date': booking_line.end_date,
                        'total_hours': booking_line.total_hours,
                        'duration': booking_line.duration,
                        'extra_hour': booking_line.extra_hour,
                        'extra_hour_charges': booking_line.extra_hour_charges,
                        'mobile_no': booking_line.mobile_no if hasattr(booking_line, 'mobile_no') else '',
                        'id_no': booking_line.id_no if hasattr(booking_line, 'id_no') else '',
                    }
                    
                    # Ensure service_type_id is properly set
                    if booking_line.type_of_service_id:
                        update_vals['service_type_id'] = booking_line.type_of_service_id.id
                        print(f"DEBUG: Setting service_type_id for vehicle line {vehicle_line.id}: {booking_line.type_of_service_id.name}")
                    else:
                        print(f"DEBUG: No type_of_service_id found in booking line {booking_line.id}")
                    
                    vehicle_line.write(update_vals)
                    sync_count += 1
                else:
                    print(f"DEBUG: Vehicle line {vehicle_line.id} has no car_booking_line_id")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Vehicle line data has been synced from car booking lines. {sync_count} lines updated.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_populate_vehicle_line_data(self):
        """Populate vehicle line data with default values if missing"""
        for trip in self:
            for vehicle_line in trip.vehicle_line_ids:
                # Set default values if data is missing
                if not vehicle_line.price_unit and not vehicle_line.unit_price:
                    vehicle_line.price_unit = 100.0  # Default price
                    vehicle_line.unit_price = 100.0
                
                if not vehicle_line.quantity and not vehicle_line.qty:
                    vehicle_line.quantity = 1.0
                    vehicle_line.qty = 1.0
                
                if not vehicle_line.extra_hour_charges:
                    vehicle_line.extra_hour_charges = 50.0  # Default extra hour charges
                
                # Set default dates if missing
                if not vehicle_line.start_date:
                    vehicle_line.start_date = fields.Datetime.now()
                
                if not vehicle_line.end_date:
                    vehicle_line.end_date = fields.Datetime.now() + timedelta(days=1)
                
                # Generate a name if missing
                if not vehicle_line.name:
                    vehicle_name = vehicle_line.vehicle_id.name if vehicle_line.vehicle_id else 'Vehicle'
                    driver_name = vehicle_line.driver_name.name if vehicle_line.driver_name else 'Driver'
                    vehicle_line.name = f"{vehicle_name} - {driver_name}"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Vehicle line data has been populated with default values.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_debug_vehicle_line_data(self):
        """Debug method to check vehicle line data for invoice creation"""
        self.ensure_one()
        debug_info = []
        
        for i, vehicle_line in enumerate(self.vehicle_line_ids):
            line_info = {
                'line_number': i + 1,
                'name': vehicle_line.name,
                'vehicle_id': vehicle_line.vehicle_id.name if vehicle_line.vehicle_id else 'None',
                'driver_name': vehicle_line.driver_name.name if vehicle_line.driver_name else 'None',
                'price_unit': vehicle_line.price_unit,
                'unit_price': vehicle_line.unit_price,
                'quantity': vehicle_line.quantity,
                'qty': vehicle_line.qty,
                'service_type_id': vehicle_line.service_type_id.name if vehicle_line.service_type_id else 'None',
                'car_model_id': vehicle_line.car_model_id.name if vehicle_line.car_model_id else 'None',
                'start_date': vehicle_line.start_date,
                'end_date': vehicle_line.end_date,
                'extra_hour': vehicle_line.extra_hour,
                'extra_hour_charges': vehicle_line.extra_hour_charges,
                'car_booking_line_id': vehicle_line.car_booking_line_id.name if vehicle_line.car_booking_line_id else 'None',
            }
            debug_info.append(line_info)
        
        # Create a formatted message
        message_parts = [f"Vehicle Lines Data for Trip: {self.name}"]
        for info in debug_info:
            message_parts.append(f"\nLine {info['line_number']}:")
            message_parts.append(f"  Name: {info['name']}")
            message_parts.append(f"  Vehicle: {info['vehicle_id']}")
            message_parts.append(f"  Driver: {info['driver_name']}")
            message_parts.append(f"  Price Unit: {info['price_unit']}")
            message_parts.append(f"  Unit Price: {info['unit_price']}")
            message_parts.append(f"  Quantity: {info['quantity']}")
            message_parts.append(f"  Qty: {info['qty']}")
            message_parts.append(f"  Service Type: {info['service_type_id']}")
            message_parts.append(f"  Car Model: {info['car_model_id']}")
            message_parts.append(f"  Start Date: {info['start_date']}")
            message_parts.append(f"  End Date: {info['end_date']}")
            message_parts.append(f"  Extra Hour: {info['extra_hour']}")
            message_parts.append(f"  Extra Hour Charges: {info['extra_hour_charges']}")
            message_parts.append(f"  Car Booking Line: {info['car_booking_line_id']}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Vehicle Line Data Debug',
                'message': '\n'.join(message_parts),
                'type': 'info',
                'sticky': True,
            }
        }

    # @api.constrains('vehicle_line_ids', 'trip_type')
    # def _check_vehicle_availability(self):
    #     for trip in self:
    #         if trip.trip_type == 'contract':
    #             for line in trip.vehicle_line_ids:
    #                 available_vehicles = self.env['vehicle.profile'].search_count([
    #                     ('vehicle_type', '=', line.vehicle_type),
    #                     ('vehicle_status', '=', 'ready'),
    #                 ])
    #                 if line.requested_quantity > available_vehicles:
    #                     raise ValidationError(
    #                         f"Cannot fulfill request: Only {available_vehicles} {line.vehicle_type} vehicles available, "
    #                         f"but {line.requested_quantity} requested."
    #                     )

    @api.model_create_multi
    def create(self, vals_list):
        print(f"DEBUG: TripProfile.create called with vals_list: {vals_list}")
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('trip.profile') or '/'
        records = super(TripProfile, self).create(vals_list)
        
        # Link trip profile to car booking if booking_id is set
        for record in records:
            print(f"DEBUG: Created record {record.name} with booking_id: {record.booking_id}")
            if record.booking_id:
                print(f"DEBUG: Linking trip profile {record.name} to booking {record.booking_id.name}")
                record.booking_id.trip_profile_id = record.id
                print(f"DEBUG: Booking {record.booking_id.name} now has trip_profile_id: {record.booking_id.trip_profile_id}")
        
        return records

    @api.model
    def create_from_booking(self, booking):
        """Create a trip profile from a car booking"""
        print(f"DEBUG: create_from_booking called with booking: {booking.name if booking else 'None'}")
        if not booking:
            print("DEBUG: No booking provided")
            raise UserError("No booking provided")
        
        # Check if trip profile already exists for this booking
        existing_trip = self.search([('booking_id', '=', booking.id)], limit=1)
        if existing_trip:
            print(f"DEBUG: Existing trip profile found: {existing_trip.name}")
            return existing_trip
        
        print(f"DEBUG: Creating new trip profile for booking: {booking.name}")
        
        # Force save the booking first to ensure all data is persisted
        booking = self.env['car.booking'].browse(booking.id)
        booking._invalidate_cache()
        
        # Ensure car booking lines are saved and have service types
        for booking_line in booking.car_booking_lines:
            if not booking_line.type_of_service_id:
                print(f"DEBUG: Booking line {booking_line.id} has no type_of_service_id, setting default")
                # Try to set a default service type
                default_service = self.env['type.of.service'].search([], limit=1)
                if default_service:
                    booking_line.type_of_service_id = default_service.id
                    print(f"DEBUG: Set default service type: {default_service.name}")
        
        # Force save the booking lines
        # Try to compute amounts if method exists
        if hasattr(booking.car_booking_lines, '_compute_amount_values'):
            booking.car_booking_lines._compute_amount_values()
        
        # Create trip profile with booking data - set region first to avoid domain issues
        trip_vals = {
            'booking_id': booking.id,
            'trip_type': 'individual',
            'service_type': 'with_driver' if booking.booking_type == 'with_driver' else 'without_driver',
            'departure_datetime': booking.service_start_date,
            'expected_arrival_datetime': booking.service_end_date,
            'driver_id': booking.driver_name.id if booking.driver_name else False,
            'customer_id': booking.customer_name.id if booking.customer_name else False,
            'project_id': booking.project_name.id if booking.project_name else False,
            'region': booking.region,  # Set region first
            'booking_type': booking.booking_type,
            'flight_number': booking.flight_number,
            'location_from': booking.location_from,
            'location_to': booking.location_to,
            'guest_phone': booking.guest_phone,
            'hotel_room_number': booking.hotel_room_number,
            'mobile': booking.mobile,  # Customer phone
            'customer_ref_number': booking.customer_ref_number,
            'business_type': booking.business_type,
            'customer_name': booking.customer_name.id if booking.customer_name else False,
            'guest_name': booking.guest_name.id if booking.guest_name else False,
            'guest_id': booking.guest_name.id if booking.guest_name else False,  # Set main guest field
            'payment_type': booking.payment_type,
            'date_of_service': booking.date_of_service,
            'notes': booking.notes,
        }
        
        trip_profile = self.create(trip_vals)
        
        # Now set the dependent fields after creation to avoid domain issues
        update_vals = {}
        if booking.city:
            update_vals['city'] = booking.city.id
        if booking.airport_id:
            update_vals['airport_id'] = booking.airport_id.id
        if booking.location_id:
            update_vals['location_id'] = booking.location_id.id
            
        if update_vals:
            trip_profile.write(update_vals)
        
        # Create vehicle lines from booking lines
        for booking_line in booking.car_booking_lines:
            # Generate proper name for car booking line if it's empty
            if not booking_line.name:
                booking_line.name = booking_line._generate_booking_line_name()
            
            vehicle_line_vals = {
                'trip_id': trip_profile.id,
                'name': booking_line.name,
                'vehicle_id': booking_line.fleet_vehicle_id.id if booking_line.fleet_vehicle_id else False,
                'driver_name': booking_line.driver_name.id if booking_line.driver_name else False,
                'driver_id': booking_line.driver_name.id if booking_line.driver_name else False,
                'car_model': booking_line.car_model,
                'car_model_id': booking_line.car_model_id.id if booking_line.car_model_id else False,
                'car_year': booking_line.car_year,
                'product_id': booking_line.product_id.id if booking_line.product_id else False,
                'product_category_id': booking_line.product_category_id.id if booking_line.product_category_id else False,
                'qty': booking_line.qty,
                'quantity': booking_line.qty,  # Set quantity from booking line
                'price_unit': booking_line.unit_price,  # Set price_unit from booking line
                'unit_price': booking_line.unit_price,
                'amount': booking_line.amount,
                'start_date': booking_line.start_date,
                'end_date': booking_line.end_date,
                # Add service type and car booking line reference for invoice creation
                'service_type_id': booking_line.type_of_service_id.id if booking_line.type_of_service_id else False,
                'total_hours': booking_line.total_hours,
                'duration': booking_line.duration,
                'extra_hour': booking_line.extra_hour,
                'extra_hour_charges': booking_line.extra_hour_charges,
                'mobile_no': booking_line.mobile_no if hasattr(booking_line, 'mobile_no') else '',
                'id_no': booking_line.id_no if hasattr(booking_line, 'id_no') else '',
                'car_booking_line_id': booking_line.id,  # Link to car booking line
                'guest_ids': [(6, 0, booking_line.guest_ids.ids if booking_line.guest_ids else [])],  # Copy guest information
                'notes': '',
            }
            
            # Debug: Print the values being set
            print(f"DEBUG: Creating vehicle line for booking line {booking_line.id}")
            print(f"DEBUG: service_type_id: {booking_line.type_of_service_id.id if booking_line.type_of_service_id else 'None'}")
            print(f"DEBUG: car_booking_line_reference: {booking_line.id}")
            print(f"DEBUG: car_booking_line_id: {booking_line.id}")
            print(f"DEBUG: guest_ids: {booking_line.guest_ids.ids if booking_line.guest_ids else 'None'}")
            
            # Ensure service_type_id is properly set
            if booking_line.type_of_service_id:
                vehicle_line_vals['service_type_id'] = booking_line.type_of_service_id.id
                print(f"DEBUG: Set service_type_id to {booking_line.type_of_service_id.name}")
            else:
                print(f"DEBUG: No type_of_service_id found in booking line {booking_line.id}")
            
            self.env['trip.vehicle.line'].create(vehicle_line_vals)
        
        return trip_profile

    def debug_trip_profile(self):
        """Debug method to check trip profile state"""
        self.ensure_one()
        print(f"DEBUG: Trip Profile: {self.name}")
        print(f"DEBUG: booking_id: {self.booking_id}")
        print(f"DEBUG: booking_id.id: {self.booking_id.id if self.booking_id else 'None'}")
        print(f"DEBUG: booking_id.name: {self.booking_id.name if self.booking_id else 'None'}")
        
        if self.booking_id:
            print(f"DEBUG: Booking trip_profile_id: {self.booking_id.trip_profile_id}")
            # Fix the AttributeError by checking if trip_profile_id exists and has an id
            trip_profile_id = self.booking_id.trip_profile_id
            if trip_profile_id and hasattr(trip_profile_id, 'id'):
                print(f"DEBUG: Booking trip_profile_id.id: {trip_profile_id.id}")
            else:
                print(f"DEBUG: Booking trip_profile_id.id: None")
        
        # Debug vehicle lines
        print(f"DEBUG: Number of vehicle lines: {len(self.vehicle_line_ids)}")
        for i, vehicle_line in enumerate(self.vehicle_line_ids):
            print(f"DEBUG: Vehicle line {i+1}: {vehicle_line.name}")
            print(f"DEBUG:   car_booking_line_id: {vehicle_line.car_booking_line_id}")
            print(f"DEBUG:   car_booking_line_id.id: {vehicle_line.car_booking_line_id.id if vehicle_line.car_booking_line_id else 'None'}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Debug Info',
                'message': f'Trip: {self.name}, Booking: {self.booking_id.name if self.booking_id else "None"}, Vehicle Lines: {len(self.vehicle_line_ids)}',
                'type': 'info',
                'sticky': False,
            }
        }

    def action_link_to_booking(self):
        """Link this trip profile to the car booking selected in the form"""
        self.ensure_one()
        
        if not self.booking_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'Please select a Car Booking in the "Car Booking" field first.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Update the booking's trip_profile_id
        self.booking_id.trip_profile_id = self.id
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Trip Profile {self.name} has been linked to Car Booking {self.booking_id.name}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_link_vehicle_lines_to_booking(self):
        """Link vehicle lines to car booking lines"""
        self.ensure_one()
        
        if not self.booking_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No Car Booking linked to this Trip Profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        booking = self.booking_id
        booking_lines = booking.car_booking_lines
        vehicle_lines = self.vehicle_line_ids
        
        if not booking_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No car booking lines found in the booking. Create booking lines first.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        if not vehicle_lines:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No vehicle lines found in this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        linked_count = 0
        for i, vehicle_line in enumerate(vehicle_lines):
            if i < len(booking_lines):
                vehicle_line.car_booking_line_id = booking_lines[i].id
                linked_count += 1
        
        message = f"Successfully linked {linked_count} vehicle lines to car booking lines."
        if linked_count < len(vehicle_lines):
            message += f" {len(vehicle_lines) - linked_count} vehicle lines could not be linked (not enough booking lines)."
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Link Results',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_create_from_booking(self):
        """Open wizard to select a booking and create trip profile from it"""
        self.ensure_one()
        
        # Get all car bookings that don't have a trip profile
        available_bookings = self.env['car.booking'].search([
            ('trip_profile_id', '=', False)
        ])
        
        if not available_bookings:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Information',
                    'message': 'No available car bookings found. All bookings already have trip profiles.',
                    'type': 'info',
                    'sticky': False,
                }
            }
        
        # Create trip profile from the first available booking
        trip_profile = self.create_from_booking(available_bookings[0])
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'trip.profile',
            'view_mode': 'form',
            'res_id': trip_profile.id,
            'target': 'current',
            'context': self.env.context,
        }

    def action_recalculate_invoice_amounts(self):
        """Recalculate invoice amounts including additional charges"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        invoice = self.invoice_id
        
        # Recalculate amounts for all lines
        for line in invoice.line_ids:
            if line.additional_charges:
                # Ensure price_subtotal includes additional_charges
                base_subtotal = line.quantity * line.price_unit
                line.price_subtotal = base_subtotal + line.additional_charges
        
        # Recalculate invoice totals
        invoice._compute_amounts()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Invoice amounts have been recalculated including additional charges.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_force_recalculate_invoice(self):
        """Force recalculation of invoice amounts with debug information"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        invoice = self.invoice_id
        debug_info = []
        
        for i, line in enumerate(invoice.line_ids):
            debug_info.append(f"Line {i+1}: {line.name}")
            debug_info.append(f"  Quantity: {line.quantity}")
            debug_info.append(f"  Price Unit: {line.price_unit}")
            debug_info.append(f"  Additional Charges: {line.additional_charges}")
            debug_info.append(f"  Original Subtotal: {line.price_subtotal}")
            
            # Recalculate
            base_subtotal = line.quantity * line.price_unit
            additional_charges = line.additional_charges or 0.0
            new_subtotal = base_subtotal + additional_charges
            
            line.price_subtotal = new_subtotal
            debug_info.append(f"  New Subtotal: {new_subtotal}")
            debug_info.append("")
        
        # Recalculate invoice totals
        invoice._compute_amounts()
        
        debug_info.append(f"Invoice Total: {invoice.amount_total}")
        debug_info.append(f"Invoice Untaxed: {invoice.amount_untaxed}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Invoice Recalculation Debug',
                'message': '\n'.join(debug_info),
                'type': 'info',
                'sticky': True,
            }
        }

    def action_update_invoice_totals(self):
        """Manually update invoice line subtotals and invoice totals"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        invoice = self.invoice_id
        total_untaxed = 0.0
        
        for line in invoice.line_ids:
            # Calculate new subtotal
            base_subtotal = line.quantity * line.price_unit
            additional_charges = line.additional_charges or 0.0
            new_subtotal = base_subtotal + additional_charges
            
            # Update line subtotal
            line.write({'price_subtotal': new_subtotal})
            total_untaxed += new_subtotal
        
        # Update invoice totals
        invoice.write({
            'amount_untaxed': total_untaxed,
            'amount_total': total_untaxed + invoice.amount_tax
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Invoice totals updated. Untaxed Amount: {total_untaxed}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_force_recompute_invoice(self):
        """Force recomputation of all computed fields in the invoice"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        invoice = self.invoice_id
        
        # Force recomputation of line subtotals
        for line in invoice.line_ids:
            line._compute_price_subtotal()
        
        # Force recomputation of invoice totals
        invoice._compute_amounts()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Invoice recomputed. Untaxed Amount: {invoice.amount_untaxed}, Total: {invoice.amount_total}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_force_update_invoice_amounts(self):
        """Force update invoice amounts including Untaxed Amount"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        invoice = self.invoice_id
        total_untaxed = 0.0
        
        print(f"DEBUG: Force updating invoice amounts for invoice {invoice.id}")
        
        for line in invoice.line_ids:
            print(f"DEBUG: Line {line.name}: quantity={line.quantity}, price_unit={line.price_unit}, additional_charges={line.additional_charges}")
            
            # Calculate new subtotal
            base_subtotal = line.quantity * line.price_unit
            additional_charges = line.additional_charges or 0.0
            new_subtotal = base_subtotal + additional_charges
            
            print(f"DEBUG: Line calculation: base_subtotal={base_subtotal}, additional_charges={additional_charges}, new_subtotal={new_subtotal}")
            
            # Update line subtotal
            line.write({'price_subtotal': new_subtotal})
            total_untaxed += new_subtotal
        
        print(f"DEBUG: Total untaxed amount calculated: {total_untaxed}")
        
        # Update invoice totals
        invoice.write({
            'amount_untaxed': total_untaxed,
            'amount_total': total_untaxed + invoice.amount_tax
        })
        
        print(f"DEBUG: Invoice updated - amount_untaxed={invoice.amount_untaxed}, amount_total={invoice.amount_total}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Invoice amounts updated. Untaxed Amount: {total_untaxed}, Total: {invoice.amount_total}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_refresh_invoice_amounts(self):
        """Refresh invoice amounts by reloading the invoice and recalculating"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        invoice_id = self.invoice_id.id
        
        # Reload the invoice from database
        invoice = self.env['account.move'].browse(invoice_id)
        
        print(f"DEBUG: Refreshing invoice {invoice_id}")
        print(f"DEBUG: Current amounts - Untaxed: {invoice.amount_untaxed}, Total: {invoice.amount_total}")
        
        # Recalculate all line subtotals
        total_untaxed = 0.0
        for line in invoice.line_ids:
            base_subtotal = line.quantity * line.price_unit
            additional_charges = line.additional_charges or 0.0
            new_subtotal = base_subtotal + additional_charges
            
            print(f"DEBUG: Line {line.name} - base_subtotal={base_subtotal}, additional_charges={additional_charges}, new_subtotal={new_subtotal}")
            
            line.write({'price_subtotal': new_subtotal})
            total_untaxed += new_subtotal
        
        print(f"DEBUG: Total untaxed calculated: {total_untaxed}")
        
        # Update invoice amounts
        invoice.write({
            'amount_untaxed': total_untaxed,
            'amount_total': total_untaxed + invoice.amount_tax
        })
        
        # Force recomputation
        invoice._compute_amounts()
        
        print(f"DEBUG: Final amounts - Untaxed: {invoice.amount_untaxed}, Total: {invoice.amount_total}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Invoice refreshed. Untaxed Amount: {invoice.amount_untaxed}, Total: {invoice.amount_total}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_update_all_invoice_amounts(self):
        """Update all invoice line subtotals and invoice totals"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        invoice = self.invoice_id
        total_untaxed = 0.0
        
        print(f"DEBUG: Updating all invoice amounts for invoice {invoice.id}")
        
        # Update all line subtotals
        for line in invoice.line_ids:
            base_subtotal = line.quantity * line.price_unit
            additional_charges = line.additional_charges or 0.0
            new_subtotal = base_subtotal + additional_charges
            
            print(f"DEBUG: Line {line.name} - quantity={line.quantity}, price_unit={line.price_unit}, additional_charges={additional_charges}")
            print(f"DEBUG: Line calculation - base_subtotal={base_subtotal}, additional_charges={additional_charges}, new_subtotal={new_subtotal}")
            
            # Update the line
            line.write({
                'price_subtotal': new_subtotal
            })
            
            total_untaxed += new_subtotal
            print(f"DEBUG: Line updated - price_subtotal={line.price_subtotal}")
        
        print(f"DEBUG: Total untaxed calculated: {total_untaxed}")
        
        # Update invoice totals
        invoice.write({
            'amount_untaxed': total_untaxed,
            'amount_total': total_untaxed + invoice.amount_tax
        })
        
        print(f"DEBUG: Invoice updated - amount_untaxed={invoice.amount_untaxed}, amount_total={invoice.amount_total}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'All invoice amounts updated. Untaxed Amount: {total_untaxed}, Total: {invoice.amount_total}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_force_database_update(self):
        """Force update database and recompute all computed fields"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        invoice = self.invoice_id
        
        print(f"DEBUG: Force updating database for invoice {invoice.id}")
        
        # Force recomputation of all computed fields
        for line in invoice.line_ids:
            print(f"DEBUG: Recomputing line {line.name}")
            line._compute_price_subtotal_with_charges()
        
        # Force recomputation of invoice totals
        invoice._compute_amounts_with_charges()
        
        # Force a write to trigger database update
        invoice.write({})
        
        print(f"DEBUG: Database updated - amount_untaxed={invoice.amount_untaxed}, amount_total={invoice.amount_total}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Database updated. Untaxed Amount: {invoice.amount_untaxed}, Total: {invoice.amount_total}',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_fix_current_invoice_totals(self):
        """Fix the current invoice totals"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Call the invoice's fix method
        result = self.invoice_id.action_fix_invoice_totals()
        
        return result
    
    def action_direct_fix_invoice(self):
        """Directly fix the invoice totals by summing line amounts"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        invoice = self.invoice_id
        total_untaxed = 0.0
        
        print(f"DEBUG: Direct fixing invoice {invoice.id}")
        
        # Sum all line amounts including additional charges
        for line in invoice.line_ids:
            # Calculate line amount including additional charges
            base_subtotal = line.quantity * line.price_unit
            additional_charges = line.additional_charges or 0.0
            line_amount = base_subtotal + additional_charges
            
            # Update line subtotal first
            line.write({'price_subtotal': line_amount})
            
            total_untaxed += line_amount
            print(f"DEBUG: Line {line.name} - quantity={line.quantity}, price_unit={line.price_unit}, additional_charges={additional_charges}, amount={line_amount}")
        
        print(f"DEBUG: Total calculated: {total_untaxed}")
        
        # Update invoice totals
        invoice.write({
            'amount_untaxed': total_untaxed,
            'amount_total': total_untaxed + invoice.amount_tax
        })
        
        print(f"DEBUG: Invoice updated - amount_untaxed={invoice.amount_untaxed}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Invoice totals fixed! Untaxed Amount: {total_untaxed}',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_force_reload_invoice_ui(self):
        """Force reload the invoice UI to update the display"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Call the invoice's reload method
        return self.invoice_id.action_force_reload_invoice()
    
    def action_sql_fix_invoice_totals(self):
        """Fix invoice totals using direct SQL"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Call the invoice's SQL fix method
        return self.invoice_id.action_direct_sql_fix()
    
    def action_complete_refresh_invoice(self):
        """Complete refresh of the invoice"""
        if not self.invoice_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Warning',
                    'message': 'No invoice linked to this trip profile.',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        # Call the invoice's complete refresh method
        return self.invoice_id.action_force_complete_refresh()

    def action_sync_service_type_from_booking(self):
        """Sync service_type_id from car booking lines to vehicle lines"""
        for trip in self:
            if not trip.booking_id:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Warning',
                        'message': 'No Car Booking linked to this Trip Profile.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }
            
            sync_count = 0
            for vehicle_line in trip.vehicle_line_ids:
                if vehicle_line.car_booking_line_id:
                    booking_line = vehicle_line.car_booking_line_id
                    if booking_line.type_of_service_id:
                        vehicle_line.service_type_id = booking_line.type_of_service_id.id
                        sync_count += 1
                        print(f"DEBUG: Synced service_type_id for vehicle line {vehicle_line.id}: {booking_line.type_of_service_id.name}")
                    else:
                        print(f"DEBUG: No type_of_service_id found in booking line {booking_line.id}")
                else:
                    print(f"DEBUG: Vehicle line {vehicle_line.id} has no car_booking_line_id")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Service Type Sync',
                    'message': f'Successfully synced service type for {sync_count} vehicle lines.',
                    'type': 'success',
                    'sticky': False,
                }
            }

    def action_ensure_service_type_sync(self):
        """Ensure service_type_id is properly set in all vehicle lines"""
        for trip in self:
            if not trip.booking_id:
                continue
                
            for vehicle_line in trip.vehicle_line_ids:
                # First try to get from linked car booking line
                if vehicle_line.car_booking_line_id and vehicle_line.car_booking_line_id.type_of_service_id:
                    vehicle_line.service_type_id = vehicle_line.car_booking_line_id.type_of_service_id.id
                    print(f"DEBUG: Set service_type_id from car_booking_line for vehicle line {vehicle_line.id}")
                # If no car booking line, try to find a matching booking line by vehicle
                elif vehicle_line.vehicle_id:
                    matching_booking_line = trip.booking_id.car_booking_lines.filtered(
                        lambda bl: bl.fleet_vehicle_id == vehicle_line.vehicle_id
                    )
                    if matching_booking_line and matching_booking_line[0].type_of_service_id:
                        vehicle_line.service_type_id = matching_booking_line[0].type_of_service_id.id
                        vehicle_line.car_booking_line_id = matching_booking_line[0].id
                        print(f"DEBUG: Set service_type_id from matching booking line for vehicle line {vehicle_line.id}")
                # If still no service type, try to get from any booking line
                elif trip.booking_id.car_booking_lines:
                    first_booking_line = trip.booking_id.car_booking_lines[0]
                    if first_booking_line.type_of_service_id:
                        vehicle_line.service_type_id = first_booking_line.type_of_service_id.id
                        vehicle_line.car_booking_line_id = first_booking_line.id
                        print(f"DEBUG: Set service_type_id from first booking line for vehicle line {vehicle_line.id}")
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Service Type Sync',
                'message': 'Service types have been ensured for all vehicle lines.',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_debug_service_type_sync(self):
        """Debug method to check service type synchronization status"""
        self.ensure_one()
        debug_info = []
        
        debug_info.append(f"Trip Profile: {self.name}")
        debug_info.append(f"Car Booking: {self.booking_id.name if self.booking_id else 'None'}")
        debug_info.append("")
        
        if self.booking_id:
            debug_info.append("Car Booking Lines:")
            for i, booking_line in enumerate(self.booking_id.car_booking_lines):
                debug_info.append(f"  Line {i+1}: {booking_line.name}")
                debug_info.append(f"    type_of_service_id: {booking_line.type_of_service_id.name if booking_line.type_of_service_id else 'None'}")
                debug_info.append(f"    fleet_vehicle_id: {booking_line.fleet_vehicle_id.name if booking_line.fleet_vehicle_id else 'None'}")
                debug_info.append("")
        
        debug_info.append("Vehicle Lines:")
        for i, vehicle_line in enumerate(self.vehicle_line_ids):
            debug_info.append(f"  Line {i+1}: {vehicle_line.name}")
            debug_info.append(f"    service_type_id: {vehicle_line.service_type_id.name if vehicle_line.service_type_id else 'None'}")
            debug_info.append(f"    car_booking_line_id: {vehicle_line.car_booking_line_id.name if vehicle_line.car_booking_line_id else 'None'}")
            debug_info.append("")
        
        # Show debug info in notification
        debug_text = "\n".join(debug_info)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Service Type Debug Info',
                'message': debug_text,
                'type': 'info',
                'sticky': True,
            }
        }

    def action_sync_guest_from_booking(self):
        """Sync guest information from car booking to trip profile"""
        for trip in self:
            if trip.booking_id:
                booking = trip.booking_id
                trip_update_vals = {}
                
                # Sync guest information from car booking to trip profile
                if booking.guest_name and booking.guest_name != trip.guest_name:
                    trip_update_vals['guest_name'] = booking.guest_name.id
                    trip_update_vals['guest_id'] = booking.guest_name.id
                    print(f"DEBUG: Syncing guest_name from car booking: {booking.guest_name.name}")
                
                if booking.guest_phone and booking.guest_phone != trip.guest_phone:
                    trip_update_vals['guest_phone'] = booking.guest_phone
                    print(f"DEBUG: Syncing guest_phone from car booking: {booking.guest_phone}")
                
                # Update trip profile with guest information
                if trip_update_vals:
                    trip.write(trip_update_vals)
                    print(f"DEBUG: Updated trip profile with guest information")
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Success',
                            'message': f'Guest information synced from car booking: {booking.guest_name.name if booking.guest_name else "N/A"}',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Info',
                            'message': 'No guest information to sync or guest information is already up to date.',
                            'type': 'info',
                            'sticky': False,
                        }
                    }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Warning',
                        'message': 'No car booking linked to this trip profile.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }

    @api.model
    def create_from_booking_with_save(self, booking):
        """Create a trip profile from a car booking with forced save"""
        print(f"DEBUG: create_from_booking_with_save called with booking: {booking.name if booking else 'None'}")
        if not booking:
            print("DEBUG: No booking provided")
            raise UserError("No booking provided")
        
        # Check if trip profile already exists for this booking
        existing_trip = self.search([('booking_id', '=', booking.id)], limit=1)
        if existing_trip:
            print(f"DEBUG: Existing trip profile found: {existing_trip.name}")
            return existing_trip
        
        print(f"DEBUG: Creating new trip profile for booking: {booking.name}")
        
        # Force save the booking and all its lines
        booking = self.env['car.booking'].browse(booking.id)
        
        # Ensure all car booking lines are saved
        for booking_line in booking.car_booking_lines:
            if not booking_line.type_of_service_id:
                print(f"DEBUG: Booking line {booking_line.id} missing type_of_service_id")
                
                # Try to find appropriate service type based on booking context
                service_type = None
                
                # First try to find by booking type
                if booking.booking_type == 'with_driver':
                    service_type = self.env['type.of.service'].search([
                        '|', ('name', 'ilike', 'transfer'),
                        ('name', 'ilike', 'with driver')
                    ], limit=1)
                elif booking.booking_type == 'rental':
                    service_type = self.env['type.of.service'].search([
                        '|', ('name', 'ilike', 'rental'),
                        ('name', 'ilike', 'without driver')
                    ], limit=1)
                
                # If not found by booking type, try to find by product
                if not service_type and booking_line.product_id:
                    service_type = self.env['type.of.service'].search([
                        ('name', 'ilike', booking_line.product_id.name)
                    ], limit=1)
                
                # If still not found, get the first available service type
                if not service_type:
                    service_type = self.env['type.of.service'].search([], limit=1)
                
                if service_type:
                    booking_line.type_of_service_id = service_type.id
                    print(f"DEBUG: Set service type for booking line {booking_line.id}: {service_type.name}")
                else:
                    print(f"DEBUG: No service type found for booking line {booking_line.id}")
        
        # Force save all booking lines
        # Try to compute amounts if method exists
        if hasattr(booking.car_booking_lines, '_compute_amount_values'):
            booking.car_booking_lines._compute_amount_values()
        
        # Force a write to ensure everything is saved
        booking.write({})
        
        # Now create the trip profile
        return self.create_from_booking(booking)

    @api.onchange('guest_name')
    def _onchange_guest_name(self):
        """Auto-sync guest information when guest_name changes"""
        if self.guest_name and self.booking_id:
            # Sync to main car booking
            if self.guest_name != self.booking_id.guest_name:
                self.booking_id.guest_name = self.guest_name.id
                print(f"DEBUG: Auto-synced guest_name to car booking: {self.guest_name.name}")
            
            # Sync to car booking lines
            for booking_line in self.booking_id.car_booking_lines:
                if self.guest_name not in booking_line.guest_ids:
                    guest_ids = booking_line.guest_ids.ids + [self.guest_name.id]
                    booking_line.guest_ids = [(6, 0, guest_ids)]
                    print(f"DEBUG: Auto-synced guest_name to booking line {booking_line.id}: {self.guest_name.name}")

    def action_sync_guest_to_booking(self):
        """Sync guest information from trip profile back to car booking"""
        for trip in self:
            if trip.booking_id:
                booking = trip.booking_id
                booking_update_vals = {}
                
                # Sync guest information from trip profile to car booking
                if trip.guest_name and trip.guest_name != booking.guest_name:
                    booking_update_vals['guest_name'] = trip.guest_name.id
                    print(f"DEBUG: Syncing guest_name to car booking: {trip.guest_name.name}")
                
                if trip.guest_phone and trip.guest_phone != booking.guest_phone:
                    booking_update_vals['guest_phone'] = trip.guest_phone
                    print(f"DEBUG: Syncing guest_phone to car booking: {trip.guest_phone}")
                
                # Update car booking with guest information
                if booking_update_vals:
                    booking.write(booking_update_vals)
                    print(f"DEBUG: Updated car booking with guest information")
                    
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Success',
                            'message': f'Guest information synced to car booking: {trip.guest_name.name if trip.guest_name else "N/A"}',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Info',
                            'message': 'No guest information to sync or guest information is already up to date.',
                            'type': 'info',
                            'sticky': False,
                        }
                    }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Warning',
                        'message': 'No car booking linked to this trip profile.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }

    def action_sync_guest_to_booking_lines(self):
        """Sync guest information from trip profile to car booking lines"""
        for trip in self:
            if trip.booking_id:
                booking = trip.booking_id
                sync_count = 0
                
                # Sync guest information from trip profile to car booking lines
                for booking_line in booking.car_booking_lines:
                    booking_line_update_vals = {}
                    
                    # Sync guest_ids from trip profile to car booking line
                    if trip.guest_name and trip.guest_name not in booking_line.guest_ids:
                        # Add the guest to the booking line's guest_ids
                        guest_ids = booking_line.guest_ids.ids + [trip.guest_name.id]
                        booking_line_update_vals['guest_ids'] = [(6, 0, guest_ids)]
                        print(f"DEBUG: Adding guest to booking line {booking_line.id}: {trip.guest_name.name}")
                    
                    # Update car booking line with guest information
                    if booking_line_update_vals:
                        booking_line.write(booking_line_update_vals)
                        sync_count += 1
                        print(f"DEBUG: Updated car booking line {booking_line.id} with guest information")
                
                if sync_count > 0:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Success',
                            'message': f'Guest information synced to {sync_count} car booking lines: {trip.guest_name.name if trip.guest_name else "N/A"}',
                            'type': 'success',
                            'sticky': False,
                        }
                    }
                else:
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'Info',
                            'message': 'No guest information to sync or guest information is already up to date.',
                            'type': 'info',
                            'sticky': False,
                        }
                    }
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Warning',
                        'message': 'No car booking linked to this trip profile.',
                        'type': 'warning',
                        'sticky': False,
                    }
                }

class TripCancellationWizard(models.TransientModel):
    _name = 'trip.cancellation.wizard'
    _description = 'Trip Cancellation Confirmation'

    trip_id = fields.Many2one('trip.profile', string='Trip Profile', required=True)

    def action_confirm_cancellation(self):
        """Confirm the trip cancellation"""
        self.ensure_one()
        
        # Cancel the trip
        self.trip_id.trip_status = 'cancelled'
        
        # Update car booking state if linked
        if self.trip_id.booking_id:
            self.trip_id.booking_id.state = 'cancelled'
        
        # Return action to reload the form and show notification
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

class TripProfileLinkWizard(models.TransientModel):
    _name = 'trip.profile.link.wizard'
    _description = 'Link Trip Profile to Car Booking'

    trip_profile_id = fields.Many2one('trip.profile', string='Trip Profile', required=True)
    booking_id = fields.Many2one('car.booking', string='Car Booking', required=True)

    def action_link(self):
        """Link the trip profile to the selected car booking"""
        self.ensure_one()
        
        # Update trip profile
        self.trip_profile_id.booking_id = self.booking_id.id
        
        # Update car booking
        self.booking_id.trip_profile_id = self.trip_profile_id.id
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'Trip Profile {self.trip_profile_id.name} has been linked to Car Booking {self.booking_id.name}',
                'type': 'success',
                'sticky': False,
            }
        }

class TripVehicleLine(models.Model):
    _name = 'trip.vehicle.line'
    _description = 'Trip Vehicle Line'

    trip_id = fields.Many2one('trip.profile', string='Trip',  ondelete='cascade')
    vehicle_type = fields.Selection([
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('van', 'Van'),
        ('other', 'Other'),
    ], string='Vehicle Type', )

    # requested_quantity = fields.Integer(string='Requested Quantity',)
    # used_quantity = fields.Integer(string='Used Quantity', compute='_compute_used_quantity', store=True)
    vehicle_ids = fields.Many2many('vehicle.profile', string='Vehicle Numbers')

    delivery_date = fields.Date(string='Delivery Date')
    expected_return_date = fields.Date(string='Expected Return Date')
    notes = fields.Text(string='Notes')

    # car_booking_line_id = fields.Many2one('car.booking.line', string='Car Booking', copy=False, readonly=True)

    # Driver assignment
    # required_drivers = fields.Integer(string='Required Drivers')
    # available_drivers = fields.Integer(string='Available Drivers')
    # driver_shortage = fields.Integer(string='Driver Shortage', compute='_compute_driver_shortage', store=True)

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    driver_id = fields.Many2one('res.partner', string='Driver')
    car_model = fields.Char(string='Car Model')
    car_year = fields.Char(string='Car Year')
    car_plate_no = fields.Char(string='Car Plate No')

    product_id = fields.Many2one('product.product')
    product_category_id = fields.Many2one('product.category')
    qty = fields.Float(string='Qty')
    quantity = fields.Float(string='Quantity', default=1.0)  # Add missing quantity field
    price_unit = fields.Float(string='Price Unit', default=0.0)  # Add missing price_unit field
    unit_price = fields.Float(string='Unit Price')
    amount = fields.Float(
        string='Amount',
        compute='_compute_amount',
        store=True,
        help='Amount calculated as unit_price * qty + extra_hour_charges * extra_hour'
    )

    car_booking_line_id = fields.Many2one('car.booking.line', string='Car Booking Line', copy=False)
    
    # Service Type and Car Booking Line fields for invoice creation
    service_type_id = fields.Many2one(
        'type.of.service',
        string='Service Type',
        help='Service type copied from car booking for invoice creation'
    )
    
    # car_booking_line_reference = fields.Many2one(
    #     'car.booking.line',
    #     string='Car Booking Line Reference',
    #     help='Reference to the car booking line for invoice creation'
    # )



    kilometer_in = fields.Float(string="Kilometer In")
    kilometer_out = fields.Float(string="Kilometer Out")

    kilometer_difference = fields.Float(
        string="Kilometer Difference",
        compute="_compute_kilometer_difference",
        store=True,
        help="Difference between Kilometer Out and Kilometer In"
    )



    name = fields.Char(
        string="Name",
    )

    # type_of_service_id = fields.Many2one(
    #     'type.of.service',
    #     string="Type of Service",
    #     help="Type of service for the car booking, e.g., transfer, full day, hourly, etc.",
    #     copy=False,
    #     readonly=True
    # )

    start_date = fields.Datetime(
        string="Start Date",
        help="Start date of the car booking or service period."
    )

    end_date = fields.Datetime(
        string="End Date",
        help="End date of the car booking or service period."
    )

    total_hours = fields.Float(
        string="Total Hours",
        compute="_compute_total_hours",
        store=True
    )

    duration = fields.Float(
        string='Duration (Days)',
        compute='_compute_duration',
        store=True,
        help="Total number of days between start and end date."
    )

    extra_hour = fields.Integer(
        string='Extra Hour',
        help="Extra Hour"
    )

    extra_hour_charges = fields.Float(
        string='Extra Hour Charges',
        help="Extra Hour Charges"
    )
    


    driver_name = fields.Many2one(
        'res.partner',
        string='Driver Name',
        help="Select the driver assigned to this booking."
    )

    mobile_no = fields.Char(
        string='Driver Mobile No',
        help="Mobile phone number of the assigned driver."
    )



    id_no = fields.Char(
        string='Driver ID No',
        help="Identification number of the driver."
    )


    @api.onchange('driver_name')
    def _onchange_driver_name(self):
        if self.driver_name:
            self.mobile_no = self.driver_name.customized_mobile or self.driver_name.mobile or self.driver_name.phone or ''
            self.id_no = self.driver_name.national_identity_number or ''
        else:
            self.mobile_no = ''

    @api.onchange('car_booking_line_id')
    def _onchange_car_booking_line_id(self):
        """Auto-sync service_type_id when car_booking_line_id changes"""
        if self.car_booking_line_id and self.car_booking_line_id.type_of_service_id:
            self.service_type_id = self.car_booking_line_id.type_of_service_id.id
            print(f"DEBUG: Auto-synced service_type_id from car_booking_line: {self.car_booking_line_id.type_of_service_id.name}")
        else:
            print(f"DEBUG: No type_of_service_id found in car_booking_line")

    car_model_id = fields.Many2one(
        'fleet.vehicle.model',
        string='Car Model',
        help="Model name of the car being used."
    )

    car_year = fields.Selection(
        selection=[
            ('2018', '2018'),
            ('2019', '2019'),
            ('2020', '2020'),
            ('2021', '2021'),
            ('2022', '2022'),
            ('2023', '2023'),
            ('2024', '2024'),
            ('2025', '2025'),
        ],
        string='Car Year',
        help="Manufacturing year of the car."
    )

    guest_ids = fields.Many2many(
        'res.partner')
    
    # Computed fields for dashboard
    trip_status = fields.Selection(
        related='trip_id.trip_status',
        string='Trip Status',
        store=True,
        readonly=True
    )
    
    trip_type = fields.Selection(
        related='trip_id.trip_type',
        string='Trip Type',
        store=True,
        readonly=True
    )
    
    service_type = fields.Selection(
        related='trip_id.service_type',
        string='Service Type',
        store=True,
        readonly=True
    )
    
    customer_name = fields.Many2one(
        related='trip_id.customer_name',
        string='Customer',
        store=True,
        readonly=True
    )
    
    guest_name = fields.Many2one(
        related='trip_id.guest_name',
        string='Guest',
        store=True,
        readonly=True
    )
    
    region = fields.Selection(
        related='trip_id.region',
        string='Region',
        store=True,
        readonly=True
    )
    
    city = fields.Many2one(
        related='trip_id.city',
        string='City',
        store=True,
        readonly=True
    )
    
    location_from = fields.Char(
        related='trip_id.location_from',
        string='Location From',
        store=True,
        readonly=True
    )
    
    location_to = fields.Char(
        related='trip_id.location_to',
        string='Location To',
        store=True,
        readonly=True
    )

    @api.depends('start_date', 'end_date')
    def _compute_total_hours(self):
        for record in self:
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                record.total_hours = delta.total_seconds() / 3600.0
            else:
                record.total_hours = 0.0

    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                # Convert datetime to date for proper calculation
                start_date = record.start_date.date()
                end_date = record.end_date.date()
                delta = end_date - start_date
                # Ensure duration is non-negative and add 1 for inclusive counting
                record.duration = max(delta.days + 1, 1)
            else:
                record.duration = 0.0
    


    @api.depends('kilometer_in', 'kilometer_out')
    def _compute_kilometer_difference(self):
        for record in self:
            if record.kilometer_in and record.kilometer_out:
                record.kilometer_difference = record.kilometer_in - record.kilometer_out
            else:
                record.kilometer_difference = 0.0
    
    @api.depends('unit_price', 'qty', 'extra_hour_charges', 'extra_hour')
    def _compute_amount(self):
        """Compute amount as unit_price * qty + extra_hour_charges * extra_hour"""
        for record in self:
            unit_price = record.unit_price or 0.0
            qty = record.qty or 1.0
            extra_hour_charges = record.extra_hour_charges or 0.0
            extra_hour = record.extra_hour or 0
            
            # Calculate base amount: unit_price * qty
            base_amount = unit_price * qty
            
            # Calculate extra hour amount: extra_hour_charges * extra_hour
            extra_amount = extra_hour_charges * extra_hour
            
            # Total amount
            record.amount = base_amount + extra_amount
            
            print(f"DEBUG: Trip vehicle line amount calculation:")
            print(f"DEBUG: unit_price={unit_price}, qty={qty}")
            print(f"DEBUG: extra_hour_charges={extra_hour_charges}, extra_hour={extra_hour}")
            print(f"DEBUG: base_amount={base_amount}, extra_amount={extra_amount}")
            print(f"DEBUG: total_amount={record.amount}")
            print(f"DEBUG: Formula: ({unit_price} × {qty}) + ({extra_hour_charges} × {extra_hour}) = {record.amount}")
    
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        if self.vehicle_id:
            self.car_model = self.vehicle_id.model_id.name
            self.car_year = str(self.vehicle_id.model_year) if self.vehicle_id.model_year else ''
            self.car_plate_no = self.vehicle_id.license_plate
        else:
            self.car_model = ''
            self.car_year = ''
            self.car_plate_no = ''

    @api.constrains('vehicle_id', 'driver_name', 'end_date')
    def _check_required_fields_based_on_status(self):
        """Validate required fields based on trip status"""
        for record in self:
            if record.trip_id:
                # Before departed state, vehicle and driver are mandatory
                if record.trip_id.trip_status == 'scheduled':
                    if not record.vehicle_id:
                        raise ValidationError(f"Vehicle must be assigned in line '{record.name}' before trip can be marked as Departed.")
                    if not record.driver_name:
                        raise ValidationError(f"Driver must be assigned in line '{record.name}' before trip can be marked as Departed.")
                
                # Only check end_date when trip status is departed (before completed)
                if record.trip_id.trip_status == 'departed':
                    if not record.end_date:
                        raise ValidationError(f"End date must be set in line '{record.name}' before trip can be marked as Completed.")

    def action_open_checklist(self):
        self.ensure_one()
        checklist = self.env['trip.vehicle.line.checklist'].search([
            ('trip_vehicle_line_id', '=', self.id)
        ], limit=1)

        if not checklist:
            checklist = self.env['trip.vehicle.line.checklist'].create({
                'trip_vehicle_line_id': self.id,
                'name': f"Checklist for {self.id}",
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Checklist',
            'res_model': 'trip.vehicle.line.checklist',
            'view_mode': 'form',
            'res_id': checklist.id,
            'target': 'new',
        }
    
    def action_view_trip(self):
        """Open the related trip profile"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Trip Profile',
            'res_model': 'trip.profile',
            'view_mode': 'form',
            'res_id': self.trip_id.id,
            'target': 'current',
        }
    
    def action_view_car_booking_line(self):
        """Open the related car booking line"""
        self.ensure_one()
        if self.car_booking_line_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Car Booking Line',
                'res_model': 'car.booking.line',
                'view_mode': 'form',
                'res_id': self.car_booking_line_id.id,
                'target': 'current',
            }
        return False
    
    def action_view_trip_from_list(self):
        """Open the trip profile when clicking on trip_id in list view"""
        self.ensure_one()
        if self.trip_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Trip Profile',
                'res_model': 'trip.profile',
                'view_mode': 'form',
                'res_id': self.trip_id.id,
                'target': 'current',
            }
        return False

    # @api.depends('vehicle_ids')
    # def _compute_used_quantity(self):
    #     for line in self:
    #         line.used_quantity = len(line.vehicle_ids)

    # @api.depends('required_drivers', 'available_drivers')
    # def _compute_driver_shortage(self):
    #     for line in self:
    #         line.driver_shortage = line.required_drivers - line.available_drivers

    # @api.constrains('requested_quantity', 'used_quantity')
    # def _check_quantity(self):
    #     for line in self:
    #         if line.used_quantity > line.requested_quantity:
    #             raise ValidationError(
    #                 f"Used quantity ({line.used_quantity}) cannot exceed requested quantity ({line.requested_quantity})."
                # )