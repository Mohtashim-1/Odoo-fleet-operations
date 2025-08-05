{
    'name': 'Vehicle Rental Operations',
    'version': '18.1',
    'summary': 'Manage vehicle rentals, trips, contracts, warehouses, and operation points',
    'description': """
        A comprehensive module for vehicle rental operations, including:
        - Vehicle profiles with technical and operational data
        - Trip management with contract and individual trip types
        - Warehouse and operation point tracking
        - Vehicle receipt and delivery workflows
        - Contract payment collection and shortage alerts
        - Operations dashboard for managers
    """,
    'author': 'Ahad Rasool OdooSpecialist',
    'category': 'Operations',
               'depends': [
               'fleet',
               'stock',  # For vehicle management
               'sale',   # For contracts
               'account',  # For payment collections
               'hr',     # For driver/employee management
               'aw_car_booking',  # For car booking integration
               'base'   # Core Odoo functionality
           ],
    'data': [
    'security/security.xml',
    'security/ir.model.access.csv',

    # Sequences and other data
    'data/dashboard_sequence.xml',
    'data/shortage_sequence.xml',
    'data/trip_sequence.xml',

    # Views (move operation_point after all models are loaded)
    'views/menu.xml',
    'views/contract_collection_views.xml',
    'views/trip_profile_views.xml',
    'views/trip_vehicle_line_dashboard_views.xml',
    'views/res_users_view.xml',
    'views/vehicle_profile_views.xml',
    'views/vehicle_receipt_delivery_views.xml',
    'views/vehicle_shortage_views.xml',
    'views/warehouse_profile_views.xml',
    'views/system_integration_views.xml',
    'views/trip_vehicle_line_checklist_view.xml',

    # 🔁 Load this last (was causing the issue)
    'views/operation_point_views.xml',
],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}