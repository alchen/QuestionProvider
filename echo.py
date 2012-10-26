from flask import Flask, request
app = Flask(__name__)

@app.route("/", methods=['GET', 'POST', 'DELETE', 'PUT'])
def echo():
    return request.data

if __name__ == "__main__":
    app.run(port=4000)