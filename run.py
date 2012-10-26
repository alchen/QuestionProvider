import os
import simplejson
from lxml import etree as ET
from flask import Flask, render_template, flash, redirect, url_for, request
from flask.ext.wtf import Form, TextField, Required, TextAreaField
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'somesecretekey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/questionprovider')
db = SQLAlchemy(app)
Bootstrap(app)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    xml = db.Column(db.String(2000))

    def __init__(self, xml=None):
        if xml is not None:
            self.xml = xml

    def __repr__(self):
        return '<Question %s>' % self.id

    def json(self):
        parser = ET.XMLParser(remove_blank_text=True)
        return simplejson.dumps({'id': self.id, 'xml': ET.tostring(ET.fromstring(self.xml, parser=parser))})

db.create_all()

class QuestionForm(Form):
    xml = TextAreaField('XML code')

@app.route("/")
def hello():
    return render_template('hello.html')

@app.route("/questions")
def listQuestions():
    questions = Question.query.order_by('id').all()
    return render_template('listQuestions.html', questions=questions)

@app.route("/question/<int:id>")
def viewQuestion(id):
    questions = Question.query.order_by('id').all()
    question = Question.query.get(id)
    tree = ET.fromstring(question.xml)
    return render_template('viewQuestion.html', questions = questions, id=id, xml=ET.tostring(tree), json=question.json())

@app.route("/question/edit/<int:id>", methods=['GET', 'POST'])
def editQuestion(id):
    questions = Question.query.order_by('id').all()
    question = Question.query.get(id)
    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()
        flash('Question Edited!')
        return redirect(url_for('listQuestions'))
    else:
        return render_template('editQuestion.html', questions = questions, id=id, form=form)

@app.route("/question/new", methods=['GET', 'POST'])
def newQuestion():
    form = QuestionForm()
    if form.validate_on_submit():
        newQuestion = Question()
        form.populate_obj(newQuestion)
        db.session.add(newQuestion)
        db.session.commit()
        flash('Question Submitted!')
        return redirect(url_for('listQuestions'))
    else:
        return render_template('newQuestion.html', form=form)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
