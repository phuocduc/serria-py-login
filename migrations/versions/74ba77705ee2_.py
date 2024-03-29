"""empty message

Revision ID: 74ba77705ee2
Revises: f415e3943d34
Create Date: 2019-11-19 12:54:30.139039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74ba77705ee2'
down_revision = 'f415e3943d34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('post_id', sa.Integer(), nullable=False))
    op.drop_column('comment', 'comment_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('comment_id', sa.INTEGER(), nullable=False))
    op.drop_column('comment', 'post_id')
    # ### end Alembic commands ###
