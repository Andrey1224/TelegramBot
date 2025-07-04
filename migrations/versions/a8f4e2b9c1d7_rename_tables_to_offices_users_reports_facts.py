"""rename tables to offices, users, reports, facts

Revision ID: a8f4e2b9c1d7
Revises: 5eb6f7dbd8a2
Create Date: 2025-07-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = 'a8f4e2b9c1d7'
down_revision = '5eb6f7dbd8a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Production-ready migration to rename tables and update foreign key relationships:
    - brand -> offices
    - manager -> users  
    - report -> reports
    - fact -> facts
    - Update all foreign key references from brand_id -> office_id
    - Add office_id to reports table with proper constraints
    """
    
    # Step 1: Rename tables
    op.rename_table("brand", "offices")
    op.rename_table("manager", "users")
    op.rename_table("report", "reports")
    op.rename_table("fact", "facts")
    
    # Step 2: Update geo table - rename brand_id to office_id and recreate FK
    with op.batch_alter_table("geo", recreate="always") as batch_op:
        # Drop existing FK (SQLite auto-generated, no specific name)
        # Note: batch mode with recreate=always will handle this automatically
        batch_op.alter_column("brand_id", new_column_name="office_id")
        batch_op.create_foreign_key(
            "fk_geo_office", 
            "offices", 
            ["office_id"], 
            ["id"], 
            ondelete="CASCADE"
        )
    
    # Step 3: Update users table - rename brand_id to office_id and recreate FK
    with op.batch_alter_table("users", recreate="always") as batch_op:
        batch_op.alter_column("brand_id", new_column_name="office_id")
        batch_op.create_foreign_key(
            "fk_users_office", 
            "offices", 
            ["office_id"], 
            ["id"], 
            ondelete="CASCADE"
        )
    
    # Step 4: Update reports table - add office_id column and update constraints
    with op.batch_alter_table("reports", recreate="always") as batch_op:
        # Add office_id column (initially nullable)
        batch_op.add_column(sa.Column("office_id", sa.Integer, nullable=True))
    
    # Populate office_id from geo.office_id
    op.execute("""
        UPDATE reports 
        SET office_id = (
            SELECT geo.office_id 
            FROM geo 
            WHERE geo.id = reports.geo_id
        )
    """)
    
    # Make office_id not nullable and add constraints
    with op.batch_alter_table("reports", recreate="always") as batch_op:
        batch_op.alter_column("office_id", nullable=False)
        # Drop old unique constraint
        batch_op.drop_constraint("uq_report_geo_date", type_="unique")
        # Create new unique constraint with office_id
        batch_op.create_unique_constraint(
            "uq_report_office_geo_date", 
            ["office_id", "geo_id", "date"]
        )
        # Add foreign key to offices
        batch_op.create_foreign_key(
            "fk_reports_office", 
            "offices", 
            ["office_id"], 
            ["id"], 
            ondelete="CASCADE"
        )


def downgrade() -> None:
    """
    Reverse the migration: restore original table names and relationships
    """
    
    # Step 1: Remove office_id from reports and restore old constraint
    with op.batch_alter_table("reports", recreate="always") as batch_op:
        batch_op.drop_constraint("fk_reports_office", type_="foreignkey")
        batch_op.drop_constraint("uq_report_office_geo_date", type_="unique")
        batch_op.create_unique_constraint("uq_report_geo_date", ["geo_id", "date"])
        batch_op.drop_column("office_id")
    
    # Step 2: Restore users table
    with op.batch_alter_table("users", recreate="always") as batch_op:
        batch_op.drop_constraint("fk_users_office", type_="foreignkey")
        batch_op.alter_column("office_id", new_column_name="brand_id")
        batch_op.create_foreign_key(None, "offices", ["brand_id"], ["id"])
    
    # Step 3: Restore geo table  
    with op.batch_alter_table("geo", recreate="always") as batch_op:
        batch_op.drop_constraint("fk_geo_office", type_="foreignkey")
        batch_op.alter_column("office_id", new_column_name="brand_id")
        batch_op.create_foreign_key(None, "offices", ["brand_id"], ["id"])
    
    # Step 4: Rename tables back
    op.rename_table("facts", "fact")
    op.rename_table("reports", "report")
    op.rename_table("users", "manager")
    op.rename_table("offices", "brand")