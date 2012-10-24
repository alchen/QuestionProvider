from flask import Flask, render_template
app = Flask(__name__)
app.config['DEBUG']                 = True
app.config['SECRET_KEY']            = 'somesecretkey'

@app.route("/")
def hello():
    return render_template("hello.html")
