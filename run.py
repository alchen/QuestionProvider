import os
import simplejson
from flask import Flask, render_template, flash, redirect, url_for
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

    def __init__(self, xml):
        self.xml = xml

    def __repr__(self):
        return '<Question %s>' % self.id

db.create_all()

class QuestionForm(Form):
    xml = TextAreaField('XML code')

@app.route("/")
def hello():
    return render_template('hello.html')

@app.route("/questions")
def listQuestions():
    questions = Question.query.all()
    return render_template('listQuestions.html', questions=questions)

@app.route("/question/new", methods=['GET', 'POST'])
def newQuestion():
    form = QuestionForm()
    if form.validate_on_submit():
        newQuestion = Question(form.xml.data)
        db.session.add(newQuestion)
        db.session.commit()
        return redirect(url_for('newQuestion'))
    else:
        return render_template('newQuestion.html', form=form)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
