"""injury claims table

Revision ID: dd9fcc0e9081
Revises: 0323a6fe44b5
Create Date: 2020-05-14 15:59:50.104409

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd9fcc0e9081'
down_revision = '0323a6fe44b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('injury',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company', sa.String(length=50), nullable=True),
    sa.Column('injury_type', sa.String(length=30), nullable=True),
    sa.Column('injury_cause', sa.String(length=30), nullable=True),
    sa.Column('open_or_closed', sa.String(length=1), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('incurred_loss', sa.Float(), nullable=True),
    sa.Column('paid_loss', sa.Float(), nullable=True),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_injury_company'), 'injury', ['company'], unique=False)
    op.create_index(op.f('ix_injury_injury_cause'), 'injury', ['injury_cause'], unique=False)
    op.create_index(op.f('ix_injury_injury_type'), 'injury', ['injury_type'], unique=False)
    op.create_index(op.f('ix_injury_open_or_closed'), 'injury', ['open_or_closed'], unique=False)
    op.create_index(op.f('ix_user_company'), 'user', ['company'], unique=False)
    op.drop_index('ix_user_compnay', table_name='user')
    op.drop_column('user', 'compnay')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('compnay', sa.VARCHAR(length=50), nullable=True))
    op.create_index('ix_user_compnay', 'user', ['compnay'], unique=False)
    op.drop_index(op.f('ix_user_company'), table_name='user')
    op.drop_index(op.f('ix_injury_open_or_closed'), table_name='injury')
    op.drop_index(op.f('ix_injury_injury_type'), table_name='injury')
    op.drop_index(op.f('ix_injury_injury_cause'), table_name='injury')
    op.drop_index(op.f('ix_injury_company'), table_name='injury')
    op.drop_table('injury')
    # ### end Alembic commands ###
