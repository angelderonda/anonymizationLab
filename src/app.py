from flask import Flask, render_template, request, redirect
import sys
sys.path.append("..")  # Adds higher directory to python modules path.
from database.generateDatabase import GenerateDatabase

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    gen = GenerateDatabase(1000000)
    filename = gen.generate_database()
    return render_template('results.html', filename=filename)


if __name__ == "__main__":
    app.run(debug=True)
