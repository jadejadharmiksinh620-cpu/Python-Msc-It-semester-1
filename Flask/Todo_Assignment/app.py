from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer,String,Boolean,Date
from datetime import datetime

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db=SQLAlchemy(app)

class todo(db.Model):
    id=db.Column(Integer,primary_key=True)
    title=db.Column(String(100),nullable=False)
    description=db.Column(String(500))
    priority=db.Column(String,nullable=False)
    is_complete=db.Column(Boolean,default=False)
    due_date=db.Column(Date,nullable=False)


@app.route("/")
def home():
    pending=todo.query.filter_by(is_complete=False).all()
    complete=todo.query.filter_by(is_complete=True).all()

    print("PENDING:",pending)
    print("COMPLETE:",complete)
    return render_template("index.html",pending=pending,complete=complete)
@app.route('/add',methods=["POST"])
def add():
    title=request.form.get("title")
    description=request.form.get("description")
    priority=request.form.get("priority")
    is_complete=request.form.get("is_completed") == "on"
    due_date=request.form.get("due_date")
    due_date=datetime.strptime(due_date,'%Y-%m-%d')

    t1=todo(title=title,description=description,priority=priority,is_complete=is_complete,due_date=due_date)

    db.session.add(t1)    
    db.session.commit()
    return redirect("/")

@app.route('/edit/<int:id>')
def edit(id):
    t1=todo.query.get(id)
    if t1 is not None:
        return render_template("edit.html",task=t1)
@app.route('/update/<int:id>', methods=["POST"])
def update(id):
    t1 = todo.query.get(id)

    title = request.form.get("title")
    description = request.form.get("description")
    priority = request.form.get("priority")
    due_date = request.form.get("due_date")

    due_date = datetime.strptime(due_date, '%Y-%m-%d')

    t1.title = title
    t1.description = description
    t1.priority = priority
    t1.due_date = due_date

    db.session.commit()

    return redirect("/")
@app.route('/toggle/<int:id>')
def toggle(id):
    t1=todo.query.get(id)

    if t1 is not None:
        t1.is_complete=not t1.is_complete
        db.session.commit()
    return redirect("/")
@app.route("/delete/<int:id>", methods=['POST'])
def delete_todo(id):
    d_id = request.form.get("d_id")
    t1 = todo.query.get(id)
    if t1 is not None:
        db.session.delete(t1)
        db.session.commit()

    return redirect("/")

    return redirect("/")
if __name__=="__main__":
    with app.app_context():
      db.create_all()
    app.run(debug=True)

