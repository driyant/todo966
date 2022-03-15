from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), unique=True, nullable=False)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route('/')
def get_all():
    tasks = db.session.query(Task).all()
    return jsonify(tasks=[task.to_dict() for task in tasks])


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    new_task = Task(title=title)
    task = Task.query.filter_by(title=title).first()
    if not task:
        db.session.add(new_task)
        db.session.commit()
        return jsonify(response={"Success": "Task has been added!"})
    else:
        return jsonify(response={"Failed": "Data is already exist!"})


@app.route('/update/<int:id>', methods=['PUT'])
def update(id):
    task = Task.query.filter_by(id=id).first()
    if task:
        task.title = request.args.get("title")
        db.session.commit()
        return jsonify(response={"Success": "Task has been updated!"})
    else:
        return jsonify(response={"Failed": "Task was not found!"})


@app.route('/delete/<int:id>', methods=['DELETE'])
def delete(id):
    task = Task.query.filter_by(id=id).first()
    db.session.delete(task)
    db.session.commit()
    return jsonify(response={"Success": "Task has been deleted!"})
  
@app.route("/api/add_task", methods=["POST"])
def api_add_task():
  # Get json request
  req = request.get_json()
  # Get string from json
  title = req.get("title")
  # Basic validation if string is empty
  if not title:
    return jsonify(message="Bad request"), 400
  # Basic validation if it is already exist
  task = Task.query.filter_by(title=title).first()
  if task:
    return jsonify(message="Task is already exist, try to add another task"), 409
  # Save database
  new_task = Task(title=title)
  db.session.add(new_task)
  db.session.commit()
  # Return jsonify
  return jsonify(message="Success"), 201

@app.route("/api/update_task/<int:id>", methods=["PUT"])
def api_update_task(id):
  task = Task.query.filter_by(id=id).first()
  # Validation
  if not task:
    return jsonify(message="Sorry, task does not exist!"), 404
  # Get json
  req = request.get_json()
  # Save to database
  task.title = req.get("title")
  db.session.commit()
  return jsonify(message="Task has been updated!"), 200

@app.route("/api/delete_task/<int:id>", methods=["DELETE"])
def api_delete_task(id):
  task = Task.query.filter_by(id=id).first()
  # Validation
  if not task:
    return jsonify(message="Task not found"), 400
  db.session.delete(task)
  db.session.commit()
  return jsonify(message="Success, task has been deleted!"), 200