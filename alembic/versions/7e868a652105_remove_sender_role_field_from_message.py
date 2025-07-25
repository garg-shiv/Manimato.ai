"""remove sender role field from message

Revision ID: 7e868a652105
Revises: 46a5481cba34
Create Date: 2025-07-14 01:01:27.258249

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7e868a652105"
down_revision: Union[str, Sequence[str], None] = "46a5481cba34"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("codes", "message_id", existing_type=sa.INTEGER(), nullable=False)
    op.drop_column("messages", "sender")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "messages",
        sa.Column(
            "sender",
            postgresql.ENUM("USER", "AI", name="senderrole"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.alter_column("codes", "message_id", existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###
