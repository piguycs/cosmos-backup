from flask import Flask
app = Flask(__name__)
@app.route('/', methods=['GET'])
def root():
    return "COSMOS IS RUNNING"
app.run(host='0.0.0.0', threaded=True)