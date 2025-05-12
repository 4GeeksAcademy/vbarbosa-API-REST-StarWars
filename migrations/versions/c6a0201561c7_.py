"""empty message

Revision ID: c6a0201561c7
Revises: 
Create Date: 2023-10-31 13:53:01.946815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6a0201561c7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop tables in order respecting foreign key dependencies
    op.drop_table('profile_people')
    op.drop_table('profile_planet')
    op.drop_table('peoples')
    op.drop_table('planets')
    op.drop_table('profiles')
    op.drop_table('users')

    
def downgrade():
    # Normally you would recreate tables here, but this migration is destructive.
    pass
