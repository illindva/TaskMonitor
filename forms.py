from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, DateTimeField, SelectMultipleField, TimeField, SelectField
from wtforms.validators import DataRequired

class TaskForm(FlaskForm):
    task_name = StringField('Task Name', validators=[DataRequired()])
    call_this = StringField('Call This', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])  # Allows only hour and min
    end_time = TimeField('End Time', validators=[DataRequired()])  # Allows only hour and min
    timezone = SelectField(
        'Time Zone',
        choices=[
            ('UTC', 'UTC'),
            ('US/Eastern', 'US/Eastern'),
            ('US/Central', 'US/Central'),
            ('Europe/London', 'Europe/London'),
            ('Asia/Kolkata', 'Asia/Kolkata'),
            ('Asia/Tokyo', 'Asia/Tokyo'),
        ],
        validators=[DataRequired()]
    )
    day_frequency = SelectMultipleField(
        'Day Frequency',
        choices=[
            ('Mon', 'Monday'),
            ('Tue', 'Tuesday'),
            ('Wed', 'Wednesday'),
            ( 'Thu', 'Thursday',),
            ('Fri', 'Friday'),
            ('Sat', 'Saturday'),
            ('Sun', 'Sunday')
        ],
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    submit = SubmitField('Add Task')

class CompleteTaskForm(FlaskForm):
    is_completed = BooleanField('Mark as Completed')
    submit = SubmitField('Update Task')
