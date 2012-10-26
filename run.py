import os
from flask import Flask, render_template, flash, redirect, url_for
from flask.ext.wtf import Form, TextField, Required, TextAreaField
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'somesecretekey')
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
Bootstrap(app)

class QuestionForm(Form):
    xml = TextAreaField('XML code')

@app.route("/")
def hello():
    return render_template('hello.html')

@app.route("/questions")
def listQuestions():
    return render_template('hello.html')

@app.route("/question/new", methods=['GET', 'POST'])
def newQuestion():
    form = QuestionForm()
    if form.validate_on_submit():
        flash("submitted!")
        return redirect(url_for('newQuestion'))
    else:
        return render_template('newQuestion.html', form=form)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
