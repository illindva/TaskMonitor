from flask import Flask, render_template, redirect, url_for, request, flash, Response
from flask_wtf.csrf import CSRFProtect
from datetime import datetime, date
import os
import pytz
import logging
from logging.handlers import TimedRotatingFileHandler
from forms import TaskForm, CompleteTaskForm
from models import SchTasks, Authorizations, db

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'TaskMonApp2025'  # Replace with a secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///EODTasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Ensure logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Set up logging
logger = logging.getLogger('werkzeug')  # Use 'werkzeug' to hijack Flask's default logger
logger.setLevel(logging.INFO)
# Dynamically generate the log file name with the current date
log_filename = datetime.now().strftime('logs/app_%Y-%m-%d.log')
handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1)
handler.suffix = "%Y-%m-%d"  # Adds a date suffix to rotated log files
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialize extensions
csrf = CSRFProtect(app)

# Initialize the database with the app
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    scheduled_tasks = SchTasks.query.filter_by(is_completed=False).all()
    completed_tasks = SchTasks.query.filter(
        SchTasks.is_completed == True,
        SchTasks.date_completed >= date.today()
    ).all()

    # Read today's log file
    log_filename = datetime.now().strftime("logs/app_%Y-%m-%d.log")
    if os.path.exists(log_filename):
        with open(log_filename, 'r') as f:
            logs = f.readlines()
        logs = logs[::-1]  # Reverse log order: Newest at the top
        logs = "".join(logs)  # Convert list to string for display
    else:
        logs = "No logs for today."

    return render_template(
        'index.html',
        scheduled_tasks=scheduled_tasks,
        completed_tasks=completed_tasks,
        logs=logs
    )


@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    form = TaskForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Extract fields from the form
            task_name = form.task_name.data
            call_this = form.call_this.data
            start_time = form.start_time.data
            end_time = form.end_time.data
            timezone = form.timezone.data
            day_frequency = ','.join(form.day_frequency.data)

            # Convert times to timezone-aware datetime objects
            tz_info = pytz.timezone(timezone)
            now_date = datetime.now(tz_info).date()  # Fetch the current date in the selected time zone
            start_time_aware = datetime.combine(now_date, start_time, tz_info)
            end_time_aware = datetime.combine(now_date, end_time, tz_info)

            # Store times in UTC for consistency in the database
            start_time_utc = start_time_aware.astimezone(pytz.utc)
            end_time_utc = end_time_aware.astimezone(pytz.utc)

            # Create a new task
            new_task = SchTasks(
                task_name=task_name,
                call_this=call_this,
                start_time=start_time_utc,
                end_time=end_time_utc,
                orig_start_time=start_time_utc,  # Same as start_time initially
                orig_end_time=end_time_utc,  # Same as end_time initially
                day_frequency=day_frequency,
                is_completed=False,
            )
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding task: {e}', 'danger')
        return redirect(url_for('index'))

    return render_template('add_task.html', form=form)

@app.route('/update_task/<int:task_id>', methods=['GET', 'POST'])
def update_task(task_id):
    task = SchTasks.query.get_or_404(task_id)
    form = CompleteTaskForm(obj=task)
    if form.validate_on_submit():
        task.is_completed = form.is_completed.data
        if task.is_completed:
            task.date_completed = datetime.utcnow()
            logger.info(f"Task completed: {task.task_name}")
        else:
            task.date_completed = None
            logger.info(f"Task marked as incomplete: {task.task_name}")
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('update_task.html', form=form, task=task)

@app.route('/export_tasks/<task_type>')
def export_tasks(task_type):
    if task_type == 'scheduled':
        tasks = SchTasks.query.filter_by(is_completed=False).all()
        filename = 'scheduled_tasks.csv'
    elif task_type == 'completed':
        tasks = SchTasks.query.filter(
            SchTasks.is_completed == True,
            SchTasks.date_completed >= date.today()
        ).all()
        filename = 'completed_tasks.csv'
    else:
        tasks = []
        filename = 'tasks.csv'

    # Generate CSV content
    output = 'Task Name,Date Created,Date Completed\n'
    for task in tasks:
        date_completed = task.date_completed.strftime('%Y-%m-%d %H:%M:%S') if task.date_completed else ''
        output += f"{task.task_name},{task.date_created.strftime('%Y-%m-%d %H:%M:%S')},{date_completed}\n"

    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"},
    )

@app.route('/get_logs', methods=['GET'])
def get_logs():
    log_filename = datetime.now().strftime("logs/app_%Y-%m-%d.log")
    if os.path.exists(log_filename):
        with open(log_filename, 'r') as f:
            logs = f.readlines()  # Read logs line by line
        logs = logs[::-1]  # Reverse the order of logs (latest first)
        logs = "".join(logs)  # Combine back into a single string
    else:
        logs = "No logs for today."
    return logs

@app.route('/refresh_section/<section>')
def refresh_section(section):
    # Implement AJAX calls for refreshing specific sections if needed
    pass

if __name__ == '__main__':
    app.run(debug=True)
