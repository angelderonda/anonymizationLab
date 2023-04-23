from __future__ import print_function, unicode_literals
import sys
sys.path.append("..")  # Adds higher directory to python modules path.
import pandas as pd
from flask import Flask, redirect, render_template, request, send_file
from database.generateDatabase import GenerateDatabase
from deident.deident import encrypt_column, reverse_encryption
from anonymization.anonymization import generalize_numeric_data, perturb_numeric_data, perturb_shuffle_data, perturb_gaussian_data,perturb_binary_data, country_to_continent, masking_data
import matplotlib
from uuid import uuid4
import signal
import glob
import os
from PyInquirer import style_from_dict, Token, prompt, Separator
from pprint import pprint
import argparse
import random
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use('Agg')

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

    list_of_steps = ''

    # Encrypt identifiers
    anon, key = encrypt_column(df, ["id", "name", "email"])
    print("Key: ", key)
    list_of_steps += "§ Encrypt identifiers (id, name, email)\n"

    # Generalize numeric data (age)
    interval_width = random.randint(5, 10)
    intervals = list(range( anon['age'].min(),  anon['age'].max() + interval_width, interval_width))
    anon['age'] = generalize_numeric_data(anon['age'], intervals)
    list_of_steps+="§ Generalize numeric data (age) using intervals of width: "+str(interval_width)+"\n"

    # Perturb numeric data (salary)
    perturb_option = random.choice(['gaussian', 'shuffle', 'numeric'])
    epsilon = random.uniform(0.1, 0.5)
    if perturb_option == 'gaussian':
        anon['salary'] = perturb_gaussian_data(anon['salary'], epsilon)
        list_of_steps+="§ Perturb numeric data (salary) using gaussian noise with epsilon " + str(round(epsilon,2))+"\n"
    elif perturb_option == 'shuffle':
        anon['salary'] = perturb_shuffle_data(anon['salary'])
        list_of_steps+="§ Perturb numeric data (salary) using shuffle\n"
    else:
        anon['salary'] = perturb_numeric_data(anon['salary'], epsilon)
        list_of_steps+="§ Perturb numeric data (salary) with epsilon "+str(round(epsilon,2))+"\n"
    
    # Perturb binary data (gender)
    epsilon = random.uniform(0.01,0.02)
    anon['gender'] = perturb_binary_data(anon['gender'], epsilon)
    list_of_steps+="§ Perturb binary data (gender) with epsilon "+str(round(epsilon,2))+"\n"

    # Generalize country name to continent
    for country in anon['country'].unique():
        anon['country'] = anon['country'].replace(country, country_to_continent(country))
    anon.rename(columns={'country': 'continent'}, inplace=True)
    list_of_steps+="§ Generalize country name to continent\n"

    # Mask security number
    anon['credit_card_security_code'] = masking_data(anon['credit_card_security_code'])
    list_of_steps+="§ Mask credit card security number\n"
        
    # Save anonymized data
    anon.to_csv("static/"+str(id)+"anonymized.csv", index=False)

    # Save decrypted data
    key, data = reverse_encryption(anon, ["id", "name","email"], key)
    data.to_csv("static/"+str(id)+"decrypted.csv", index=False)
    

    # HISTOGRAMS

    # Create a histogram of the original age column
    hist_plot = df['age'].plot.hist(color='blue', alpha=0.5, label='Original age')  # set color and transparency

    # Set x and y axis labels
    plt.xlabel('Age')
    plt.ylabel('Frequency')

    # Add a trend line
    mean_age = df['age'].mean()
    plt.axvline(mean_age, color='red', linestyle='--', label='Mean original age')  # add a vertical line for the mean age

    # Save the histogram as an image file
    hist_plot.get_figure().savefig('static/histogram1_'+str(id)+'.png')

    # Create a histogram of the anonymized age column
    original = anon['age']
    anon['age'] = anon['age'].apply(lambda x: x.split(', ')[0].replace('[', ''))
    anon['age'] = anon['age'].astype(int)
    anon['age'] = anon['age'].apply(lambda x: x + int(interval_width/2))
    hist_plot = anon['age'].plot.hist(color='green', alpha=0.5, label='Anonymized age')  # set color and transparency

    # Add a trend line
    mean_age_anon = anon['age'].mean()
    plt.axvline(mean_age_anon, color='blue', linestyle='-', label='Mean anonymized Age')  # add a vertical line for the mean anonymized age
    
    # Print the difference between original and anonymized data
    age_difference = round(abs(mean_age - mean_age_anon),2)
    anon['age'] = original

    #add legend
    plt.legend()

    # Save the histogram as an image file
    hist_plot.get_figure().savefig('static/histogram1_'+str(id)+'.png')
    hist_plot.get_figure().clear()

    # Create a histogram of the original salary column
    hist_plot = df['salary'].plot.hist(color='orange', alpha=0.5, label='Original salary')  # set color and transparency

    # Set x and y axis labels
    plt.xlabel('Salary')
    plt.ylabel('Frequency')

    # Add a trend line
    mean_salary = df['salary'].mean()
    plt.axvline(mean_salary, color='red', linestyle='--', label='Mean original salary')  # add a vertical line for the mean salary

    # Save the histogram as an image file
    hist_plot.get_figure().savefig('static/histogram2_'+str(id)+'.png')

    # Create a histogram of the anonymized salary column
    hist_plot = anon['salary'].plot.hist(color='purple', alpha=0.5, label='Anonymized salary')  # set color and transparency

    # Add a trend line
    mean_salary_anon = anon['salary'].mean()
    plt.axvline(mean_salary_anon, color='blue', linestyle='-', label='Mean anonymized salary')  # add a vertical line for the mean anonymized salary

    # Print the difference between original and anonymized data
    salary_difference = round(abs(mean_salary - mean_salary_anon),2)

    #add legend
    plt.legend()

    # Save the histogram as an image file
    hist_plot.get_figure().savefig('static/histogram2_'+str(id)+'.png')
    hist_plot.get_figure().clear()

    # Calculate the counts of each unique value in the 'gender' column for original data
    gender_counts = df['gender'].value_counts()

    # Calculate the counts of each unique value in the 'gender' column for anonymized data
    gender_counts_anon = anon['gender'].value_counts()

    # Merge the original and anonymized data counts
    merged_counts = gender_counts.to_frame().merge(gender_counts_anon.to_frame(), left_index=True, right_index=True)
    merged_counts.columns = ['Original', 'Anonymized']

    # Calculate the counts of males and females in the original and anonymized datasets
    male_count_original = merged_counts['Original']['M']
    female_count_original = merged_counts['Original']['F']
    male_count_anonymized = merged_counts['Anonymized']['M']
    female_count_anonymized = merged_counts['Anonymized']['F']
     # Calculate the percentage difference in male and female counts
    percentage_male_difference = abs(round(((male_count_anonymized - male_count_original) / male_count_original) * 100,2))
    percentage_female_difference = abs(round(((female_count_anonymized - female_count_original) / female_count_original) * 100,2))

        # Print the percentage difference
    print("Percentage difference in male counts: {:.2f}%".format(percentage_male_difference))
    print("Percentage difference in female counts: {:.2f}%".format(percentage_female_difference))

    # Create a pie chart with both original and anonymized data counts
    fig, ax = plt.subplots()
    ax.pie(merged_counts['Original'], labels=merged_counts.index, autopct='%1.1f%%', startangle=90, colors=['red', 'blue'],pctdistance=0.85)
    ax.pie(merged_counts['Anonymized'], autopct='%1.1f%%', startangle=90, colors=['lightcoral', 'lightblue'], radius=0.75, pctdistance=0.5)
    plt.title('Gender Distribution (Original vs Anonymized)')

    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, fc='none', edgecolor='red', linewidth=5),
        plt.Rectangle((0, 0), 1, 1, fc='none', edgecolor='blue', linewidth=5),
        plt.Rectangle((0, 0), 1, 1, fc='none', edgecolor='lightcoral', linewidth=5),
        plt.Rectangle((0, 0), 1, 1, fc='none', edgecolor='lightblue', linewidth=5)
    ]
    legend_labels = ['Original (M)', 'Original (F)', 'Anonymized (F)', 'Anonymized (M)']

    # Add legend with custom handles and labels
    ax.legend(legend_handles, legend_labels, loc='upper left')

    plt.savefig('static/pie_chart'+str(id)+'.png')

    utility_explain = ''
    utility_explain += '<ul style="list-style-type: none; padding: 0;">'
    utility_explain += '<li style="margin-bottom: 10px;"><i class="fas fa-calc"></i> <strong>Utility calculation:</strong></li>'
    original_utility = anon_utility = 100
    utility_explain += '<li style="margin-bottom: 5px;">Original utility: <em>' + str(original_utility) + '</em></li>'
    # Compute utility score
    number_of_columns_encrypted = 3
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-columns"></i> Number of columns encrypted: <em>' + str(number_of_columns_encrypted) + '</em> (5 points less for each one)</li>'
    anon_utility = anon_utility - (number_of_columns_encrypted * 5)
    #age
    anon_utility = anon_utility - age_difference * 5
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-calendar-alt"></i> Age difference: <em>' + str(age_difference) + '</em> (5 points less for each year of difference)</li>'
    #salary
    anon_utility = anon_utility - salary_difference * 0.01
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-dollar-sign"></i> Salary difference: <em>' + str(salary_difference) + '</em> (0.01 points less for each dollar of difference)</li>'
    #gender
    anon_utility = anon_utility - percentage_male_difference
    anon_utility = anon_utility - percentage_female_difference
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-venus-mars"></i> Male/Female difference: <em>' + str(percentage_male_difference) + '%/' + str(percentage_female_difference) + '%</em></li>'

    #continent
    anon_utility = anon_utility - 5
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-globe"></i> Continent: (5 points less for using generalization)</li>'
    #security_card
    anon_utility = anon_utility - 5
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-shield-alt"></i> Security card: (5 points less for using masking)</li>'
    utility_explain += '<li style="margin-top: 10px;"><i class="fas fa-user-secret"></i> <strong>Anonymized utility: <em>' + str(anon_utility) + '</em></strong></li>'
    utility_explain += '</ul>'


    # Return the result page
    return render_template('result.html', original_column_names=df.columns.values, original_row_data=list(df.values.tolist()),
                           enc_column_names=anon.columns.values, enc_row_data=list(anon.values.tolist()), zip=zip, original_file=str(id)+".csv", enc_file=str(id)+"anonymized.csv", dec_file="static/"+str(id)+"decrypted.csv", histogram1="static/histogram1_"+str(id)+".png", histogram2="static/histogram2_"+str(id)+".png", steps=list_of_steps,
                           age_difference=round(age_difference, 2), salary_difference=round(salary_difference, 2), pie_chart="static/pie_chart"+str(id)+".png", percentage_male_difference=percentage_male_difference, percentage_female_difference=percentage_female_difference, utility_explain=utility_explain)


@app.route('/download/<string:filename>')
def download(filename):
    return send_file('static/'+filename, as_attachment=True)


def delete_files(signum, frame):
    files = glob.glob('static/*.png') + glob.glob('static/*.csv')
    for f in files:
        os.remove(f)
    exit(1)


def start_web_interface():
    print("Starting web interface...")
    app.run(debug=True)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, delete_files)

    parser = argparse.ArgumentParser()
    parser.add_argument('--web', action='store_true')
    if parser.parse_args().web:
        start_web_interface()

    print ("Welcome to the Anonymizer Tool CLI!")
    while True:
        questions = [
            {
                'type': 'list',
                'message': 'What database do you want to use?',
                'name': 'db_type',
                'choices': [
                    {
                        'name': 'Use my own database (CSV)'
                    },
                    {
                        'name': 'Generate a random database'
                    },
                ],
                'validate': lambda answer: 'You must choose at least one type.'
                if len(answer) == 0 else True
            }
        ]
        answers = prompt(questions)
        if answers['db_type'] == 'Use my own database (CSV)':
            filename = input("Please enter the path to your CSV file: ")
            df = pd.read_csv(filename)
            print("Your CSV file has the following columns: ")
            print(df.columns.values)
        else:
            num_rows = int(input("How many rows do you want to generate? "))
            filename = input("Please enter the path to save the CSV file: ")
            gen = GenerateDatabase(num_rows, filename)
            filename = gen.generate_database()
            df = pd.read_csv(filename)
            print("Your CSV file has the following columns: ")
            print(df.columns.values)
