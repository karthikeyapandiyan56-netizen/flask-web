import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Configure SQLite database path to reside in the current working directory
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'todo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database extension
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Define the Todo DB Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    # Use timezone-naive datetime representing UTC to avoid Python 3.12+ deprecation warnings
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    def __repr__(self):
        return f'<Task {self.id}>'

# Automatically initialize database within application context
with app.app_context():
    db.create_all()

# Route: Index (List all tasks and Create task via POST)
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form.get('content', '')
        if task_content.strip():
            new_task = Todo(content=task_content.strip())
            try:
                db.session.add(new_task)
                db.session.commit()
                return redirect('/')
            except Exception as e:
                return f"There was an issue adding your task: {e}", 500
        return redirect('/')
    else:
        # Retrieve tasks sorted by creation date (newest first)
        tasks = Todo.query.order_by(Todo.date_created.desc()).all()
        return render_template('index.html', tasks=tasks)

# Route: Delete a task by ID
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = db.get_or_404(Todo, id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f"There was a problem deleting that task: {e}", 500

# Route: Update a task by ID
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = db.get_or_404(Todo, id)
    if request.method == 'POST':
        task.content = request.form.get('content', '').strip()
        if not task.content:
            return "Task content cannot be empty", 400
        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f"There was an issue updating your task: {e}", 500
    else:
        return render_template('update.html', task=task)

if __name__ == "__main__":
    app.run(debug=True)
