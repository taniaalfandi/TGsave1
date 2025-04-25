from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'r_ajput999'


if __name__ == "__main__":
    app.run()
