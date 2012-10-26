import os
try:
    import simplejson as json
except ImportError:
    import json
import requests
from lxml import etree as ET
from flask import Flask, render_template, flash, redirect, url_for, request
from flask.ext.wtf import Form, TextField, Required, TextAreaField, SelectField, validators
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'somesecretekey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///test.db')
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
        return json.dumps({'id': self.id, 'xml': ET.tostring(ET.fromstring(self.xml, parser=parser))})

db.create_all()


class QuestionForm(Form):
    xml = TextAreaField('XML code')


class PostForm(Form):
    username = TextField('Username')
    password = TextField('Password')
    method = SelectField('Method', choices=[('GET', 'GET'),('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')])
    url = TextField('URL')
    payload = TextAreaField('Payload')

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

@app.route("/question/post/<int:id>", methods=['GET', 'POST'])
def postQuestion(id):
    questions = Question.query.order_by('id').all()
    question = Question.query.get(id)
    tree = ET.fromstring(question.xml)
    form = PostForm(url="http://127.0.0.1:4000/", payload=question.json())
    if form.validate_on_submit():
        if form.method.data == 'PUT':
            makeRequest = requests.put
        elif form.method.data == 'POST':
            makeRequest = requests.post
        elif form.method.data == 'DELETE':
            makeRequest = requests.delete
        else:
            makeRequest = requests.get
        response = requests.post(form.url.data, data=form.payload.data)
        return render_template('postQuestion.html', questions = questions, id=id, form=form, response=response)
    else:
        return render_template('postQuestion.html', questions = questions, id=id, form=form)

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
    debug = port == 5000
    app.run(host='0.0.0.0', port=port, debug=debug)
