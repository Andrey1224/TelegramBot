# This file handles Alembic migration script template
# it defines the template for generating migration files

"""change month type from varchar to date

Revision ID: e68d85c6102e
Revises: 65147b26f419
Create Date: 2025-07-09 00:04:36.342471

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e68d85c6102e'
down_revision = '65147b26f419'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN directly, so we need to:
    # 1. Create new column with DATE type
    # 2. Copy data with conversion
    # 3. Drop old column
    # 4. Rename new column
    
    # Add new column with DATE type
    op.add_column('facts', sa.Column('month_new', sa.Date(), nullable=True))
    
    # Update data: convert VARCHAR to DATE (assuming format YYYY-MM-DD or YYYY-MM)
    op.execute("""
        UPDATE facts 
        SET month_new = CASE 
            WHEN length(month) = 7 THEN DATE(month || '-01')
            WHEN length(month) = 10 THEN DATE(month)
            ELSE DATE(substr(month, 1, 7) || '-01')
        END
    """)
    
    # Make the new column NOT NULL
    op.alter_column('facts', 'month_new', nullable=False)
    
    # Drop the old column
    op.drop_column('facts', 'month')
    
    # Rename new column to original name
    op.alter_column('facts', 'month_new', new_column_name='month')
    
    # Recreate the unique constraint
    op.create_unique_constraint('uq_fact_geo_month', 'facts', ['geo_id', 'month'])


def downgrade() -> None:
    # Reverse the process
    op.drop_constraint('uq_fact_geo_month', 'facts', type_='unique')
    op.alter_column('facts', 'month', new_column_name='month_old')
    op.add_column('facts', sa.Column('month', sa.VARCHAR(), nullable=True))
    
    # Convert DATE back to VARCHAR
    op.execute("UPDATE facts SET month = strftime('%Y-%m', month_old)")
    
    op.alter_column('facts', 'month', nullable=False)
    op.drop_column('facts', 'month_old')
    op.create_unique_constraint('uq_fact_geo_month', 'facts', ['geo_id', 'month']) 