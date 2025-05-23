"""Initial migration

Revision ID: d4d4269aa525
Revises: 
Create Date: 2025-04-02 09:11:56.930810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4d4269aa525'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('entry_inventory',
    sa.Column('uuid', sa.String(), nullable=False),
    sa.Column('sno', sa.String(), nullable=True),
    sa.Column('product_id', sa.String(), nullable=False),
    sa.Column('inventory_id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('material', sa.String(), nullable=True),
    sa.Column('total_quantity', sa.String(), nullable=True),
    sa.Column('manufacturer', sa.String(), nullable=True),
    sa.Column('purchase_dealer', sa.String(), nullable=True),
    sa.Column('purchase_date', sa.Date(), nullable=True),
    sa.Column('purchase_amount', sa.String(), nullable=True),
    sa.Column('repair_quantity', sa.String(), nullable=True),
    sa.Column('repair_cost', sa.String(), nullable=True),
    sa.Column('on_rent', sa.String(), nullable=True),
    sa.Column('vendor_name', sa.String(), nullable=True),
    sa.Column('total_rent', sa.String(), nullable=True),
    sa.Column('rented_inventory_returned', sa.String(), nullable=True),
    sa.Column('returned_date', sa.Date(), nullable=True),
    sa.Column('on_event', sa.String(), nullable=True),
    sa.Column('in_office', sa.String(), nullable=True),
    sa.Column('in_warehouse', sa.String(), nullable=True),
    sa.Column('issued_qty', sa.String(), nullable=True),
    sa.Column('balance_qty', sa.String(), nullable=True),
    sa.Column('submitted_by', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('bar_code', sa.String(), nullable=False),
    sa.Column('unique_code', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('uuid'),
    sa.UniqueConstraint('bar_code'),
    sa.UniqueConstraint('unique_code')
    )
    op.create_index('ix_entry_inventory_created_at', 'entry_inventory', ['created_at'], unique=False)
    op.create_index('ix_entry_inventory_inventory_id', 'entry_inventory', ['inventory_id'], unique=False)
    op.create_index(op.f('ix_entry_inventory_product_id'), 'entry_inventory', ['product_id'], unique=True)
    op.create_index(op.f('ix_entry_inventory_sno'), 'entry_inventory', ['sno'], unique=False)
    op.create_index('ix_entry_inventory_updated_at', 'entry_inventory', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_entry_inventory_updated_at', table_name='entry_inventory')
    op.drop_index(op.f('ix_entry_inventory_sno'), table_name='entry_inventory')
    op.drop_index(op.f('ix_entry_inventory_product_id'), table_name='entry_inventory')
    op.drop_index('ix_entry_inventory_inventory_id', table_name='entry_inventory')
    op.drop_index('ix_entry_inventory_created_at', table_name='entry_inventory')
    op.drop_table('entry_inventory')
    # ### end Alembic commands ###
