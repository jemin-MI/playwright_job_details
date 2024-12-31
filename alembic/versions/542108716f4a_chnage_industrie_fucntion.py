"""chnage industrie fucntion

Revision ID: 542108716f4a
Revises: 695e632ef2d4
Create Date: 2024-12-30 19:25:38.868520

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '542108716f4a'
down_revision = '695e632ef2d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('jobs', 'industry_function',
               existing_type=mysql.VARCHAR(length=250),
               type_=sa.Text(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('jobs', 'industry_function',
               existing_type=sa.Text(),
               type_=mysql.VARCHAR(length=250),
               existing_nullable=True)
    # ### end Alembic commands ###