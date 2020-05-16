"""empty message

Revision ID: d93679eddb4f
Revises: d09ebba3e73a
Create Date: 2020-05-10 18:49:33.441573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd93679eddb4f'
down_revision = 'd09ebba3e73a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('company', sa.String(length=50), nullable=True))
    op.create_index(op.f('ix_user_company'), 'user', ['company'], unique=False)
    op.drop_index('ix_user_compnay', table_name='user')
    op.drop_column('user', 'compnay')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('compnay', sa.VARCHAR(length=50), nullable=True))
    op.create_index('ix_user_compnay', 'user', ['compnay'], unique=False)
    op.drop_index(op.f('ix_user_company'), table_name='user')
    op.drop_column('user', 'company')
    # ### end Alembic commands ###