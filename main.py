from flask import Flask, render_template, request
import requests
from src import rhyme_detect

app = Flask(__name__)

@app.route('/')
def index():
    
    return render_template('index.html', value=rhyme_detect.get_sample())


@app.route('/', methods=['POST'])
def output():
    input_text = request.form.get('input_text')
    output = rhyme_detect.rhyme_detect(input_text)

    return render_template("index.html", value=output)

if __name__ == "__main__":
    app.run(debug=True)