import os
try:
    import simplejson as json
except ImportError:
    import json
import requests
from lxml import etree as ET
from flask import Flask, render_template, flash, redirect, url_for, request
from flask.ext.wtf import Form, TextField, Required, TextAreaField, SelectField, validators, RadioField
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

    def json(self, postQuestion=True, postAnswer=False, correct=True):
        parser = ET.XMLParser(remove_blank_text=True)
        tree = ET.fromstring(self.xml, parser=parser)
        jsonDict = {}

        if postQuestion:
            jsonDict['question'] = ET.tostring(tree)
        else:
            jsonDict['question_id'] = self.id

        if postAnswer:
            if correct == True:
                jsonDict['answer'] = tree.xpath("//choice[@correct='true']")[0][0].text.strip()
                jsonDict['correct'] = True
            else:
                jsonDict['answer'] = tree.xpath("//choice[@correct='false']")[0][0].text.strip()
                jsonDict['correct'] = False

        return json.dumps(jsonDict)

db.create_all()


class QuestionForm(Form):
    xml = TextAreaField('XML code')


class PostForm(Form):
    username = TextField('Username')
    password = TextField('Password')
    method = SelectField('Method', choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')])
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
    """Show the question xml as well as the json format to be posted."""
    questions = Question.query.order_by('id').all()
    question = Question.query.get(id)
    tree = ET.fromstring(question.xml)
    return render_template('viewQuestion.html', questions=questions, id=id, xml=ET.tostring(tree), json=question.json())


def requestMethod(methodString):
    """Return the appropriate request method function."""
    if methodString == 'PUT':
        return requests.put
    elif methodString == 'POST':
        return requests.post
    elif methodString == 'DELETE':
        return requests.delete
    else:
        return requests.get


@app.route("/question/post/<string:toPost>/<int:id>", methods=['GET', 'POST'])
def postQuestion(id, toPost):
    questions = Question.query.order_by('id').all()
    question = Question.query.get(id)
    tree = ET.fromstring(question.xml)
    headers = {'content-type': 'application/json'}
    if toPost == 'question':
        json = question.json()
    elif toPost == 'answer':
        json = question.json(postQuestion=False, postAnswer=True)
    else:
        json = question.json(postAnswer=True)
    form = PostForm(url="http://echoing.herokuapp.com/", payload=json)
    if form.validate_on_submit():
        request = requestMethod(form.method.data)
        response = request(form.url.data, data=form.payload.data, headers=headers)
        return render_template('postQuestion.html', questions=questions, id=id, form=form, response=response)
    else:
        return render_template('postQuestion.html', questions=questions, id=id, form=form)


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
        return render_template('editQuestion.html', questions=questions, id=id, form=form)


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


@app.route("/question/render/<int:id>", methods=['GET', 'POST'])
def renderQuestion(id):
    class questionRender(Form):
        pass
    questions = Question.query.order_by('id').all()
    question = Question.query.get(id)
    tree = ET.fromstring(question.xml)
    text = tree[0].text.strip()
    questionResponse = tree[1]
    if questionResponse.tag == 'multiplechoiceresponse':
        choicegroup = questionResponse[0]
        choiceList = []
        for choice in choicegroup:
            choiceText = choice[0].text.strip() # the text portion of the response
            choiceList.append((choiceText, choiceText))
        setattr(questionRender, 'answer', SelectField('Answer', choices=choiceList))
    else:
        flash("Question type not supported")
        return redirect(url_for('listQuestions'))
    form = questionRender()

    return render_template('renderQuestion.html', questions=questions, id=id, text=text, form=form)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = port == 5000
    app.run(host='0.0.0.0', port=port, debug=debug)
