# This file handles Alembic migration script template
# it defines the template for generating migration files

"""Change month type from string to date

Revision ID: 65147b26f419
Revises: a8f4e2b9c1d7
Create Date: 2025-01-27 21:19:42.066542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65147b26f419'
down_revision: Union[str, None] = 'a8f4e2b9c1d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if there are any invalid month formats before migration
    connection = op.get_bind()
    invalid_months = connection.execute("""
        SELECT month FROM facts 
        WHERE month NOT GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]'
        OR length(month) != 7
        LIMIT 1
    """).fetchone()
    
    if invalid_months:
        raise ValueError(f"Invalid month format found: {invalid_months[0]}. Expected YYYY-MM format.")
    
    # Create a new temporary table with the correct schema
    op.create_table('facts_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('geo_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.Date(), nullable=False),
        sa.Column('amount_fact', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['geo_id'], ['geo.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('geo_id', 'month', name='uq_fact_geo_month_new')
    )
    
    # Copy data from old table to new table, converting string dates to date objects
    # This assumes month strings are in "YYYY-MM" format and converts them to first day of month
    op.execute("""
        INSERT INTO facts_new (id, geo_id, month, amount_fact)
        SELECT id, geo_id, date(month || '-01'), amount_fact
        FROM facts
        WHERE date(month || '-01') IS NOT NULL
    """)
    
    # Verify data integrity
    old_count = connection.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    new_count = connection.execute("SELECT COUNT(*) FROM facts_new").fetchone()[0]
    
    if old_count != new_count:
        raise ValueError(f"Data integrity check failed: {old_count} old records vs {new_count} new records")
    
    # Drop the old table
    op.drop_table('facts')
    
    # Rename the new table to the original name
    op.rename_table('facts_new', 'facts')
    
    # Recreate the index with the correct name
    op.create_index('ix_fact_id', 'facts', ['id'])


def downgrade() -> None:
    # Create a new temporary table with the old schema
    op.create_table('facts_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('geo_id', sa.Integer(), nullable=False),
        sa.Column('month', sa.String(), nullable=False),
        sa.Column('amount_fact', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['geo_id'], ['geo.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('geo_id', 'month', name='uq_fact_geo_month_old')
    )
    
    # Copy data from new table to old table, converting date objects back to strings
    op.execute("""
        INSERT INTO facts_old (id, geo_id, month, amount_fact)
        SELECT id, geo_id, strftime('%Y-%m', month), amount_fact
        FROM facts
    """)
    
    # Drop the new table
    op.drop_table('facts')
    
    # Rename the old table to the original name
    op.rename_table('facts_old', 'facts')
    
    # Recreate the index
    op.create_index('ix_fact_id', 'facts', ['id']) 