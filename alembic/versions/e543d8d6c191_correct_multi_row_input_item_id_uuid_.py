"""correct_multi_row_input item id uuid but not unique

Revision ID: e543d8d6c191
Revises: 1ce2d01f7d54
Create Date: 2025-04-06 01:32:54.970903

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e543d8d6c191'
down_revision: Union[str, None] = '1ce2d01f7d54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('to_event_inventory_project_barcode_key', 'to_event_inventory', type_='unique')
    op.drop_constraint('to_event_inventory_project_barcode_unique_code_key', 'to_event_inventory', type_='unique')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('to_event_inventory_project_barcode_unique_code_key', 'to_event_inventory', ['project_barcode_unique_code'])
    op.create_unique_constraint('to_event_inventory_project_barcode_key', 'to_event_inventory', ['project_barcode'])
    # ### end Alembic commands ###
