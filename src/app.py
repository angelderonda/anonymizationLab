import sys
sys.path.append("..")  # Adds higher directory to python modules path.
import pandas as pd
from flask import Flask, redirect, render_template, request, send_file
from database.generateDatabase import GenerateDatabase
from deident.deident import encrypt_column, reverse_encryption
import matplotlib
matplotlib.use('Agg')
from uuid import uuid4
import signal
import glob
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate')
def generate():

    id = uuid4()
    gen = GenerateDatabase(1000, 'static/'+str(id)+".csv")
    filename = gen.generate_database()
    df = pd.read_csv(filename)
    enc, key = encrypt_column(df, ["id", "name"])
    enc.to_csv("static/"+str(id)+"encrypted.csv", index=False)
    print("Key: ", key)
    key, data = reverse_encryption(enc, ["id", "name"], key)
    data.to_csv("static/"+str(id)+"decrypted.csv", index=False)

    # Create a histogram of a numeric column
    hist_plot = enc['age'].plot.hist()

    # Save the histogram as an image file
    hist_plot.get_figure().savefig('static/histogram_'+str(id)+'.png')
    hist_plot.get_figure().clear()

    # Create a boxplot of a numeric column
    box_plot = enc.boxplot(column='age')

    # Save the boxplot as an image file
    box_plot.get_figure().savefig('static/boxplot_'+str(id)+'.png')
    box_plot.get_figure().clear()

    return render_template('result.html', original_column_names=df.columns.values, original_row_data=list(df.head(10).values.tolist()),
                           enc_column_names=enc.columns.values, enc_row_data=list(enc.head(10).values.tolist()), zip=zip, original_file='static/'+str(id)+".csv", enc_file="static/"+str(id)+"encrypted.csv", dec_file="static/"+str(id)+"decrypted.csv", histogram="static/histogram_"+str(id)+".png", boxplot="static/boxplot_"+str(id)+".png")


@app.route('/download/<string:filename>')
def download(filename):
    return send_file('static/'+filename, as_attachment=True)

def delete_files(signum, frame):
    files = glob.glob('static/*.png') + glob.glob('static/*.csv')
    for f in files:
        os.remove(f)
    exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, delete_files)
    app.run(debug=True)
    
