"""add subtitle_data to ProcessingTask

Revision ID: 34853918f943
Revises: 9ebe54ae970b
Create Date: 2026-05-10 17:52:19.441961

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34853918f943'
down_revision: Union[str, None] = '9ebe54ae970b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 添加 subtitle_data 可空文本字段到 processing_task 表
    with op.batch_alter_table('processing_task') as batch_op:
        batch_op.add_column(sa.Column('subtitle_data', sa.Text(), nullable=True))

    # 删除废弃的 folder 表
    op.drop_table('folder')


def downgrade() -> None:
    # 恢复 folder 表
    op.create_table('folder',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=100), nullable=False),
    sa.Column('parent_id', sa.INTEGER(), nullable=True),
    sa.Column('color', sa.VARCHAR(length=20), nullable=True),
    sa.Column('icon', sa.VARCHAR(length=50), nullable=True),
    sa.Column('sort_order', sa.INTEGER(), nullable=True),
    sa.Column('created_at', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['folder.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    # 删除 subtitle_data 列
    with op.batch_alter_table('processing_task') as batch_op:
        batch_op.drop_column('subtitle_data')
