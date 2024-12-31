"""chnage company link to null

Revision ID: 695e632ef2d4
Revises: 811c71a3f2f7
Create Date: 2024-12-30 19:24:11.307732

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '695e632ef2d4'
down_revision = '811c71a3f2f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('jobs', 'company_link',
               existing_type=mysql.TEXT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('jobs', 'company_link',
               existing_type=mysql.TEXT(),
               nullable=False)
    # ### end Alembic commands ###
