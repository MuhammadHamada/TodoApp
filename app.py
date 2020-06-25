from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/todoapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = "todos"
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo ID: {self.id}, description: {self.description}, completed:{self.completed}>'

class TodoList(db.Model):
    __tablename__ = "todolists"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship('Todo', backref='list', lazy=True, cascade="all, delete")


@app.route('/todos/create', methods = ['POST'])
def create_todo():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    list_id = request.get_json()['list_id']
    todo = Todo(description=description, list_id=list_id)
    db.session.add(todo)
    db.session.commit()
    body['description']= todo.description
    body['id'] = todo.id
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)

@app.route('/lists/create', methods = ['POST'])
def create_todolist():
  error = False
  body = {}
  try:
    description = request.get_json()['description']
    todolist = TodoList(name=description)
    db.session.add(todolist)
    db.session.commit()
    body['description']= todolist.name
    body['id'] = todolist.id
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)


@app.route('/todos/set-completed-todo/<todo_id>', methods=['POST'])
def set_completed_todo(todo_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    todo = Todo.query.get(todo_id)
    todo.completed = completed
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))

@app.route('/lists/set-completed-list/<list_id>', methods=['POST'])
def set_completed_todolist(list_id):
  try:
    completed = request.get_json()['completed']
    print('completed', completed)
    _list = TodoList.query.get(list_id)
    _list.completed = completed

    todos = _list.todos
    print(todos)
    for t in todos:
      t.completed = completed
    print(todos)

    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('index'))



@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo_item(todo_id):
  error = False
  body = {}
  try:
    id = request.get_json()['id']
    todo = Todo.query.get(id)
    db.session.delete(todo)
    db.session.commit()
    body['id'] = id
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)

@app.route('/lists/<list_id>', methods=['DELETE'])
def delete_list_item(list_id):
  error = False
  body = {}
  try:
    id = request.get_json()['id']
    todolist = TodoList.query.get(id)
    db.session.delete(todolist)
    db.session.commit()
    body['id'] = id
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    return jsonify(body)



@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', 
    lists=TodoList.query.order_by('id').all(),
    active_list=TodoList.query.get(list_id),
    todos=Todo.query.filter_by(list_id=list_id).order_by('id').all())


@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id = 1))

if __name__ == '__main__':
  app.run(debug=True)

