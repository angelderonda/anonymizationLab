from flask import Flask, render_template, request, redirect
import sys
import pandas as pd
from deident.deident import encrypt_column, reverse_encryption
sys.path.append("..")  # Adds higher directory to python modules path.
from database.generateDatabase import GenerateDatabase


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate')
def generate():
    gen = GenerateDatabase(1000)
    filename = gen.generate_database()
    df = pd.read_csv(filename)
    data, key = encrypt_column(df, ["id","name"])
    data.to_csv("encrypted.csv", index=False)
    print("Key: ", key)
    key, data = reverse_encryption(data, ["id","name"], key)
    data.to_csv("decrypted.csv", index=False)
    print("Key: ", key)
    return render_template('results.html', filename=filename)


if __name__ == "__main__":
    app.run(debug=True)
