"""add new field of the table

Revision ID: 51b6524bd897
Revises: 99043bbf7616
Create Date: 2024-12-30 17:45:52.581161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51b6524bd897'
down_revision = '99043bbf7616'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jobs', sa.Column('industry', sa.String(length=150), nullable=True))
    op.add_column('jobs', sa.Column('job_type', sa.String(length=100), nullable=True))
    op.add_column('jobs', sa.Column('industry_function', sa.String(length=250), nullable=True))
    op.add_column('jobs', sa.Column('skill_list', sa.Text(), nullable=True))
    op.add_column('jobs', sa.Column('early_applicant', sa.String(length=50), nullable=True))
    op.add_column('jobs', sa.Column('job_id', sa.String(length=50), nullable=True))
    op.add_column('jobs', sa.Column('job_role', sa.String(length=150), nullable=True))
    op.add_column('jobs', sa.Column('interview_process', sa.String(length=100), nullable=True))
    op.add_column('jobs', sa.Column('education', sa.String(length=250), nullable=True))
    op.add_column('jobs', sa.Column('specialization', sa.String(length=200), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('jobs', 'specialization')
    op.drop_column('jobs', 'education')
    op.drop_column('jobs', 'interview_process')
    op.drop_column('jobs', 'job_role')
    op.drop_column('jobs', 'job_id')
    op.drop_column('jobs', 'early_applicant')
    op.drop_column('jobs', 'skill_list')
    op.drop_column('jobs', 'industry_function')
    op.drop_column('jobs', 'job_type')
    op.drop_column('jobs', 'industry')
    # ### end Alembic commands ###