# top of your file
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!', 200

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# run Flask in background thread
threading.Thread(target=run_flask).start()


#from flask import Flask
#app = Flask(__name__)

#@app.route('/')
#def hello_world():
 #   return 'r_ajput999'


#if __name__ == "__main__":
#    app.run()
