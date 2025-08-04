def migrate(cr, version):
    """Add show_fleet_operations column to res_users table"""
    cr.execute("""
        ALTER TABLE res_users 
        ADD COLUMN IF NOT EXISTS show_fleet_operations boolean DEFAULT false
    """) 