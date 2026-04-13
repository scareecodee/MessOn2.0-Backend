"""create pg_trgm and pgcrypto extension

Revision ID: 3d76cede0813
Revises: 
Create Date: 2026-04-13 05:33:10.597709

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d76cede0813'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    op.create_table('colleges',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('domain', sa.String(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('mess',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mess_college_id'), 'mess', ['college_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Enum('platform_admin', 'college_admin', 'mess_admin', 'student', name='user_role'), nullable=False),
    sa.Column('picture', sa.String(), nullable=True),
    sa.Column('google_sub', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_users_name_trgm', 'users', ['name'], unique=False, postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})
    op.create_index(op.f('ix_users_college_id'), 'users', ['college_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_google_sub'), 'users', ['google_sub'], unique=False)
    op.create_table('college_admin',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('meal_price_config',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('mess_id', sa.UUID(), nullable=False),
    sa.Column('per_day_price', sa.Float(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mess_id'], ['mess.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('index_price_config', 'meal_price_config', ['mess_id', 'college_id', 'start_date'], unique=False)
    op.create_index(op.f('ix_meal_price_config_college_id'), 'meal_price_config', ['college_id'], unique=False)
    op.create_index(op.f('ix_meal_price_config_mess_id'), 'meal_price_config', ['mess_id'], unique=False)
    op.create_table('mess_closures',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('mess_id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('reason', sa.String(), nullable=False),
    sa.CheckConstraint('end_date >= start_date', name='check_closure_end_after_start'),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mess_id'], ['mess.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_closure_mess_dates', 'mess_closures', ['mess_id', 'start_date', 'end_date'], unique=False)
    op.create_index(op.f('ix_mess_closures_college_id'), 'mess_closures', ['college_id'], unique=False)
    op.create_index(op.f('ix_mess_closures_mess_id'), 'mess_closures', ['mess_id'], unique=False)
    op.create_table('mess_weeks',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('mess_id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('coupon_generation_status', sa.String(), nullable=False),
    sa.Column('coupon_generation_started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.CheckConstraint('end_date >= start_date', name='check_end_after_start'),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mess_id'], ['mess.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mess_id', 'start_date', name='unique_week_per_mess')
    )
    op.create_index('ix_mess_week_mess_dates', 'mess_weeks', ['mess_id', 'start_date', 'end_date'], unique=False)
    op.create_index(op.f('ix_mess_weeks_college_id'), 'mess_weeks', ['college_id'], unique=False)
    op.create_index(op.f('ix_mess_weeks_mess_id'), 'mess_weeks', ['mess_id'], unique=False)
    op.create_table('rating_analytics',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('mess_id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('meal_slot', sa.Enum('breakfast', 'lunch', 'dinner', name='meal_slot_enum'), nullable=False),
    sa.Column('veg_sum', sa.Integer(), nullable=True),
    sa.Column('veg_count', sa.Integer(), nullable=True),
    sa.Column('non_veg_sum', sa.Integer(), nullable=True),
    sa.Column('non_veg_count', sa.Integer(), nullable=True),
    sa.Column('total_sum', sa.Integer(), nullable=True),
    sa.Column('total_count', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mess_id'], ['mess.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mess_id', 'date', 'meal_slot', name='uq_rating_analytics_slot')
    )
    op.create_index('idx_rating_analytics_lookup', 'rating_analytics', ['mess_id', 'date', 'meal_slot'], unique=False)
    op.create_index(op.f('ix_rating_analytics_college_id'), 'rating_analytics', ['college_id'], unique=False)
    op.create_index(op.f('ix_rating_analytics_date'), 'rating_analytics', ['date'], unique=False)
    op.create_index(op.f('ix_rating_analytics_meal_slot'), 'rating_analytics', ['meal_slot'], unique=False)
    op.create_index(op.f('ix_rating_analytics_mess_id'), 'rating_analytics', ['mess_id'], unique=False)
    op.create_table('students',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('mess_id', sa.UUID(), nullable=False),
    sa.Column('roll_number', sa.String(), nullable=False),
    sa.Column('branch', sa.String(), nullable=False),
    sa.Column('batch', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mess_id'], ['mess.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('roll_number'),
    sa.UniqueConstraint('user_id', name='unique_student_per_mess')
    )
    op.create_index('idx_students_pagination', 'students', ['roll_number', 'created_at', 'user_id'], unique=False)
    op.create_index(op.f('ix_students_mess_id'), 'students', ['mess_id'], unique=False)
    op.create_table('submission_window_templates',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('mess_id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('start_day', sa.Enum('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', name='weekday_enum'), nullable=False),
    sa.Column('end_day', sa.Enum('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', name='weekday_enum'), nullable=False),
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mess_id'], ['mess.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mess_id', name='unique_window_per_mess')
    )
    op.create_index(op.f('ix_submission_window_templates_college_id'), 'submission_window_templates', ['college_id'], unique=False)
    op.create_index(op.f('ix_submission_window_templates_mess_id'), 'submission_window_templates', ['mess_id'], unique=False)
    op.create_table('mess_menu',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('mess_id', sa.UUID(), nullable=False),
    sa.Column('week_id', sa.UUID(), nullable=False),
    sa.Column('day', sa.Enum('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', name='weekday_enum'), nullable=False),
    sa.Column('meal_slot', sa.Enum('breakfast', 'lunch', 'dinner', name='meal_slot_enum'), nullable=False),
    sa.Column('meal_type', sa.Enum('veg', 'nonVeg', name='meal_type_enum'), nullable=False),
    sa.Column('dishes', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mess_id'], ['mess.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['week_id'], ['mess_weeks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mess_id', 'day', 'meal_slot', 'meal_type', 'week_id', name='unique_menu_per_slot')
    )
    op.create_index('ix_menu_lookup', 'mess_menu', ['mess_id', 'week_id', 'day'], unique=False)
    op.create_index(op.f('ix_mess_menu_day'), 'mess_menu', ['day'], unique=False)
    op.create_index(op.f('ix_mess_menu_meal_slot'), 'mess_menu', ['meal_slot'], unique=False)
    op.create_index(op.f('ix_mess_menu_meal_type'), 'mess_menu', ['meal_type'], unique=False)
    op.create_index(op.f('ix_mess_menu_mess_id'), 'mess_menu', ['mess_id'], unique=False)
    op.create_index(op.f('ix_mess_menu_week_id'), 'mess_menu', ['week_id'], unique=False)
    op.create_table('ratings',
    sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
    sa.Column('student_id', sa.UUID(), nullable=False),
    sa.Column('mess_id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('meal_slot', sa.Enum('breakfast', 'lunch', 'dinner', name='meal_slot_enum'), nullable=False),
    sa.Column('meal_type', sa.Enum('veg', 'nonVeg', name='meal_type_enum'), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('rating BETWEEN 1 AND 5', name='check_rating_range'),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mess_id'], ['mess.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['students.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('student_id', 'date', 'meal_slot', 'meal_type', name='uq_student_meal_rating')
    )
    op.create_index('idx_rating_aggregation', 'ratings', ['mess_id', 'college_id', 'date', 'meal_slot'], unique=False)
    op.create_index(op.f('ix_ratings_college_id'), 'ratings', ['college_id'], unique=False)
    op.create_index(op.f('ix_ratings_date'), 'ratings', ['date'], unique=False)
    op.create_index(op.f('ix_ratings_meal_slot'), 'ratings', ['meal_slot'], unique=False)
    op.create_index(op.f('ix_ratings_mess_id'), 'ratings', ['mess_id'], unique=False)
    op.create_index(op.f('ix_ratings_student_id'), 'ratings', ['student_id'], unique=False)
    op.create_table('submission_windows',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('college_id', sa.UUID(), nullable=False),
    sa.Column('mess_id', sa.UUID(), nullable=False),
    sa.Column('week_id', sa.UUID(), nullable=False),
    sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint('end_time >= start_time', name='check_closure_end_after_start'),
    sa.ForeignKeyConstraint(['college_id'], ['colleges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['mess_id'], ['mess.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['week_id'], ['mess_weeks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('mess_id', 'week_id', name='unique_window_per_mess_week')
    )
    op.create_index(op.f('ix_submission_windows_college_id'), 'submission_windows', ['college_id'], unique=False)
    op.create_index(op.f('ix_submission_windows_mess_id'), 'submission_windows', ['mess_id'], unique=False)
    op.create_index(op.f('ix_submission_windows_week_id'), 'submission_windows', ['week_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_submission_windows_week_id'), table_name='submission_windows')
    op.drop_index(op.f('ix_submission_windows_mess_id'), table_name='submission_windows')
    op.drop_index(op.f('ix_submission_windows_college_id'), table_name='submission_windows')
    op.drop_table('submission_windows')
    op.drop_index(op.f('ix_ratings_student_id'), table_name='ratings')
    op.drop_index(op.f('ix_ratings_mess_id'), table_name='ratings')
    op.drop_index(op.f('ix_ratings_meal_slot'), table_name='ratings')
    op.drop_index(op.f('ix_ratings_date'), table_name='ratings')
    op.drop_index(op.f('ix_ratings_college_id'), table_name='ratings')
    op.drop_index('idx_rating_aggregation', table_name='ratings')
    op.drop_table('ratings')
    op.drop_index(op.f('ix_mess_menu_week_id'), table_name='mess_menu')
    op.drop_index(op.f('ix_mess_menu_mess_id'), table_name='mess_menu')
    op.drop_index(op.f('ix_mess_menu_meal_type'), table_name='mess_menu')
    op.drop_index(op.f('ix_mess_menu_meal_slot'), table_name='mess_menu')
    op.drop_index(op.f('ix_mess_menu_day'), table_name='mess_menu')
    op.drop_index('ix_menu_lookup', table_name='mess_menu')
    op.drop_table('mess_menu')
    op.drop_index(op.f('ix_submission_window_templates_mess_id'), table_name='submission_window_templates')
    op.drop_index(op.f('ix_submission_window_templates_college_id'), table_name='submission_window_templates')
    op.drop_table('submission_window_templates')
    op.drop_index(op.f('ix_students_mess_id'), table_name='students')
    op.drop_index('idx_students_pagination', table_name='students')
    op.drop_table('students')
    op.drop_index(op.f('ix_rating_analytics_mess_id'), table_name='rating_analytics')
    op.drop_index(op.f('ix_rating_analytics_meal_slot'), table_name='rating_analytics')
    op.drop_index(op.f('ix_rating_analytics_date'), table_name='rating_analytics')
    op.drop_index(op.f('ix_rating_analytics_college_id'), table_name='rating_analytics')
    op.drop_index('idx_rating_analytics_lookup', table_name='rating_analytics')
    op.drop_table('rating_analytics')
    op.drop_index(op.f('ix_mess_weeks_mess_id'), table_name='mess_weeks')
    op.drop_index(op.f('ix_mess_weeks_college_id'), table_name='mess_weeks')
    op.drop_index('ix_mess_week_mess_dates', table_name='mess_weeks')
    op.drop_table('mess_weeks')
    op.drop_index(op.f('ix_mess_closures_mess_id'), table_name='mess_closures')
    op.drop_index(op.f('ix_mess_closures_college_id'), table_name='mess_closures')
    op.drop_index('ix_closure_mess_dates', table_name='mess_closures')
    op.drop_table('mess_closures')
    op.drop_index(op.f('ix_meal_price_config_mess_id'), table_name='meal_price_config')
    op.drop_index(op.f('ix_meal_price_config_college_id'), table_name='meal_price_config')
    op.drop_index('index_price_config', table_name='meal_price_config')
    op.drop_table('meal_price_config')
    op.drop_table('college_admin')
    op.drop_index(op.f('ix_users_google_sub'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_college_id'), table_name='users')
    op.drop_index('idx_users_name_trgm', table_name='users', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})
    op.drop_table('users')
    op.drop_index(op.f('ix_mess_college_id'), table_name='mess')
    op.drop_table('mess')
    op.drop_table('colleges')
    # ### end Alembic commands ###
