import sys
sys.path.append("..")  # Adds higher directory to python modules path.
from anonymization.anonymization import generalize_numeric_data, perturb_numeric_data, perturb_shuffle_data, perturb_gaussian_data, perturb_binary_data, country_to_continent, masking_data
import chardet
from pandas.api.types import is_numeric_dtype
from pandas.api.types import is_string_dtype
import math
import matplotlib.pyplot as plt
import random
import os
import glob
import signal
from uuid import uuid4
import matplotlib
from deident.deident import encrypt_column, reverse_encryption
from database.generateDatabase import GenerateDatabase
from flask import Flask, redirect, render_template, request, send_file
import pandas as pd

matplotlib.use('Agg')

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename.split('.')[1] != 'csv':
            return render_template('index.html', error="Error reading file <strong>" + file.filename + "</strong>. You must upload a csv file, you uploaded a <strong>" + file.filename.split('.')[1] + "</strong> file. Please try again.")
        file.save('static/'+file.filename)
        # detect encoding, reencode if necessary and read file
        with open('static/'+file.filename, 'rb') as f:
            result = chardet.detect(f.read())
        if result['encoding'] != 'utf-8':  # reencode if necessary
            with open('static/'+file.filename, 'r', encoding=result['encoding']) as f:
                with open('static/'+file.filename+'_utf8', 'w', encoding='utf-8') as f2:
                    for line in f:
                        f2.write(line)
            os.remove('static/'+file.filename)
            os.rename('static/'+file.filename+'_utf8',
                      'static/'+file.filename)  # rename file
        try:
            df = pd.read_csv('static/'+file.filename)  # try to read file
        except:
            os.remove('static/'+file.filename)
            return render_template('index.html', error="Error reading file <strong>" + file.filename + "</strong>, please check if it is a valid csv file and it is properly encoded and try again.")
        return render_template('upload.html', column_names=df.columns.values, filename=file.filename)


@app.route('/upload/result', methods=['POST'])
def generate_upload():
    if request.method == 'POST':
        filename = request.form.get('filename')
        filename_without_ext = filename.split('.')[0]
        df = pd.read_csv('static/'+filename)

        modal_steps = ''

        types = dict()
        for column in df.columns:
            types[column] = request.form.get('column_'+column)

        # Encrypt identifiers
        encrypted_columns = []
        for column in types:
            if types[column] == 'id':
                encrypted_columns.append(column)

        anon, key = encrypt_column(df, encrypted_columns)
        if len(encrypted_columns) > 0:
            print("Key: ", key)
            modal_steps += "<i class='fas fa-check text-success'></i> Encrypt identifiers " + \
                str(encrypted_columns) + "<br>"

        # Generalize numeric data
        generalized_columns = []
        for column in types:
            if types[column] == 'num_gen':
                if anon[column].dtype == 'float64' or anon[column].dtype == 'float32':
                    anon[column] = anon[column].astype(int)
                    modal_steps += "<i class='fas fa-check text-success'></i> Change from float to int column " + \
                        str(column)+"<br>"
                if is_numeric_dtype(anon[column]) == False:
                    modal_steps += "<i class='fas fa-times text-danger'></i> Skipping Generalize numeric (not int nor float), is "+str(
                        anon[column].dtype)+"<br>"
                    continue
                generalized_columns.append(column)

        for column in generalized_columns:
            interval_width = random.randint(math.floor((anon[column].max(
            ) - anon[column].min()) / 10), math.floor((anon[column].max() - anon[column].min()) / 5))
            intervals = list(range(math.floor(anon[column].min()),  math.floor(
                anon[column].max()) + interval_width, interval_width))
            anon[column] = generalize_numeric_data(anon[column], intervals)
            modal_steps += "<i class='fas fa-check text-success'></i> Generalize numeric data ("+column+") using intervals of width: "+str(
                interval_width)+"<br>"

        # Perturb numeric data
        perturbed_columns = []
        for column in types:
            if types[column].startswith('num_data_pert'):
                if is_numeric_dtype(anon[column]) == False:
                    modal_steps += "<i class='fas fa-times text-danger'></i> Skipping Perturb numeric data (not int nor float), is "+str(
                        anon[column].dtype)+"<br>"
                    continue
                perturbed_columns.append(column)

        for column in perturbed_columns:
            perturb_option = types[column].split('_')[3]
            if request.form.get('epsilon_'+column) == None:
                epsilon = random.uniform(0.01, 1)
            else:
                epsilon = float(request.form.get('epsilon_'+column))
            if perturb_option == 'gauss':
                anon[column] = perturb_gaussian_data(anon[column], epsilon)
                modal_steps += "<i class='fas fa-check text-success'></i> Perturb numeric data ("+column+") using gaussian noise with epsilon " + str(
                    round(epsilon, 2))+"<br>"
            elif perturb_option == 'shuff':
                anon[column] = perturb_shuffle_data(anon[column])
                modal_steps += "<i class='fas fa-check text-success'></i> Perturb numeric data (" + \
                    column+") using shuffle<br>"
            else:
                anon[column] = perturb_numeric_data(anon[column], epsilon)
                modal_steps += "<i class='fas fa-check text-success'></i> Perturb numeric data ("+column+") with epsilon "+str(
                    round(epsilon, 2))+"<br>"

        # Perturb binary data
        perturbed_binary = []
        for column in types:
            if types[column] == 'num_data_bin':
                if anon[column].unique().size != 2:
                    modal_steps += "<i class='fas fa-times text-danger'></i> Skipping Perturb binary data (not binary), the are "+str(
                        anon[column].unique().size)+" possible values<br>"
                    continue
                perturbed_binary.append(column)

        for column in perturbed_binary:
            if request.form.get('epsilon_'+column) == None:
                epsilon = random.uniform(0.01, 1)
            else:
                epsilon = float(request.form.get('epsilon_'+column))
            anon[column] = perturb_binary_data(anon[column],epsilon)
            modal_steps += "<i class='fas fa-check text-success'></i> Perturb binary data with epsilon " + str(epsilon)+ " (" + \
                column+")<br>"

        # Country generalization
        country_columns = []
        for column in types:
            if types[column] == 'country':
                if is_string_dtype(anon[column]) == False:
                    modal_steps += "<i class='fas fa-times text-danger'></i> Skipping Generalize country name (not string), is "+str(
                        anon[column].dtype)+"<br>"
                    continue
                country_columns.append(column)

        for column in country_columns:
            for country in anon[column].unique():
                print(country)
                anon[column] = anon[column].replace(
                    country, country_to_continent(country))
            anon.rename(columns={column: 'continent'}, inplace=True)
            modal_steps += "<i class='fas fa-check text-success'></i> Generalize country name to continent (" + \
                column+")<br>"

        # Masking data
        masked_columns = []
        for column in types:
            if types[column] == 'mask':
                masked_columns.append(column)

        for column in masked_columns:
            anon[column] = masking_data(anon[column])
            modal_steps += "<i class='fas fa-check text-success'></i> Mask data (" + \
                column+")<br>"

        # Save anonymized data
        anon.to_csv("static/"+filename_without_ext+"_anonymized.csv", index=False)

        # Save decrypted data
        key, data = reverse_encryption(anon, encrypted_columns, key)
        data.to_csv("static/"+filename_without_ext+"_decrypted.csv", index=False)

        # Print histograms
        # Histogram for generalized data
        histograms = {}
        differences = {}
        num = 0
        for column in generalized_columns:
            # Create a histogram of the original data
            hist_plot = df[column].plot.hist(
                color='blue', alpha=0.5, label='Original ' + column)  # set color and transparency

            # Add a trend line
            mean = df[column].mean()
            # add a vertical line for the mean value
            plt.axvline(mean, color='red', linestyle='--',
                        label='Mean original ' + column)

            # Save the histogram as an image file
            hist_plot.get_figure().savefig('static/histogram'+str(num)+'_'+filename_without_ext+'.png')

            # Create a histogram of the anonymized column
            original = anon[column]
            anon[column] = anon[column].apply(lambda x: x.split(', ')[
                                              0].replace('[', ''))
            anon[column] = anon[column].astype(int)
            interval_width = random.randint(math.floor((anon[column].max(
            ) - anon[column].min()) / 10), math.floor((anon[column].max() - anon[column].min()) / 5))
            anon[column] = anon[column].apply(
                lambda x: x + int(interval_width/2))
            hist_plot = anon[column].plot.hist(
                color='green', alpha=0.5, label='Anonymized ' + column)  # set color and transparency

            # Add a trend line
            mean_age_anon = anon[column].mean()
            # add a vertical line for the mean anonymized age
            plt.axvline(mean_age_anon, color='blue', linestyle='-',
                        label='Mean anonymized ' + column)

            # Print the difference between original and anonymized data
            difference = round(abs(mean - mean_age_anon), 2)
            anon[column] = original

            # add legend
            plt.legend()

            # Save the histogram as an image file
            hist_plot.get_figure().savefig('static/histogram'+str(num)+'_'+filename_without_ext+'.png')
            hist_plot.get_figure().clear()
            histograms[column] = 'histogram'+str(num)+'_'+filename_without_ext+'.png'
            differences[column] = difference
            num += 1
        
        # Histogram for perturbed numeric data
        for column in perturbed_columns:
            # Create a histogram of the original salary column
            hist_plot = df[column].plot.hist(
                color='orange', alpha=0.5, label='Original '+column)  # set color and transparency

            # Add a trend line
            mean = df[column].mean()
            # add a vertical line for the mean salary
            plt.axvline(mean, color='red', linestyle='--',
                        label='Mean original ' + column)

            # Save the histogram as an image file
            hist_plot.get_figure().savefig('static/histogram'+str(num)+'_'+filename_without_ext+'.png')

            # Create a histogram of the anonymized salary column
            hist_plot = anon[column].plot.hist(
                color='purple', alpha=0.5, label='Anonymized ' + column)  # set color and transparency

            # Add a trend line
            mean_salary_anon = anon[column].mean()
            # add a vertical line for the mean anonymized salary
            plt.axvline(mean_salary_anon, color='blue',
                        linestyle='-', label='Mean anonymized ' + column)

            # Print the difference between original and anonymized data
            salary_difference = round(abs(mean - mean_salary_anon), 2)

            # add legend
            plt.legend()

            # Save the histogram as an image file
            hist_plot.get_figure().savefig('static/histogram'+str(num)+'_'+filename_without_ext+'.png')
            hist_plot.get_figure().clear()
            histograms[column] = 'histogram'+str(num)+'_'+filename_without_ext+'.png'
            differences[column] = salary_difference
            num += 1

        # Pie chart for perturbed binary data
        for column in perturbed_binary:
            # Calculate the counts of each unique value in the 'gender' column for original data
            gender_counts = df[column].value_counts()

            # Calculate the counts of each unique value in the 'gender' column for anonymized data
            gender_counts_anon = anon[column].value_counts()

            # Merge the original and anonymized data counts
            merged_counts = gender_counts.to_frame().merge(
                gender_counts_anon.to_frame(), left_index=True, right_index=True)
            merged_counts.columns = ['Original', 'Anonymized']

            # Calculate the counts of each binary value
            male_count_original = merged_counts['Original'][0]
            female_count_original = merged_counts['Original'][1]
            male_count_anonymized = merged_counts['Anonymized'][0]
            female_count_anonymized = merged_counts['Anonymized'][1]
            # Calculate the percentage difference in male and female counts
            dif_v1 = abs(round(
                ((male_count_anonymized - male_count_original) / male_count_original) * 100, 2))
            dif_v2 = abs(round(
                ((female_count_anonymized - female_count_original) / female_count_original) * 100, 2))

            # Create a pie chart with both original and anonymized data counts
            fig, ax = plt.subplots()
            ax.pie(merged_counts['Original'], labels=merged_counts.index,
                autopct='%1.1f%%', startangle=90, colors=['red', 'blue'], pctdistance=0.85)
            ax.pie(merged_counts['Anonymized'], autopct='%1.1f%%', startangle=90, colors=[
                'lightcoral', 'lightblue'], radius=0.75, pctdistance=0.5)
            plt.title(column + ' Distribution (Original vs Anonymized)')

            legend_handles = [
                plt.Rectangle((0, 0), 1, 1, fc='none', edgecolor='red', linewidth=5),
                plt.Rectangle((0, 0), 1, 1, fc='none', edgecolor='blue', linewidth=5),
                plt.Rectangle((0, 0), 1, 1, fc='none',
                            edgecolor='lightcoral', linewidth=5),
                plt.Rectangle((0, 0), 1, 1, fc='none',
                            edgecolor='lightblue', linewidth=5)
            ]
            
            label1 = merged_counts.index[0]
            label2 = merged_counts.index[1]
            legend_labels = [label1 + ' Original', label2 + ' Original', label1 + ' Anonymized', label2 + ' Anonymized']

            # Add legend with custom handles and labels
            ax.legend(legend_handles, legend_labels, loc='upper left')

            plt.savefig('static/piechart'+str(num)+'_'+filename_without_ext+'.png')
            plt.close()
            histograms[column] = 'piechart'+str(num)+'_'+filename_without_ext+'.png'
            differences[column] = label1 + ' difference: ' + str(dif_v1) + '%, ' + label2 + ' difference: ' + str(dif_v2) + '%'
            num += 1

        # Utility explain
        utility_explain = ''
        utility_explain += '<ul style="list-style-type: none; padding: 0;">'
        utility_explain += '<li style="margin-bottom: 10px;"><i class="fas fa-calc"></i> <strong>Utility calculation:</strong></li>'
        original_utility = anon_utility = 100
        utility_explain += '<li style="margin-bottom: 5px;">Original utility: <em>' + \
            str(original_utility) + '</em></li>'
        # Compute utility score
        number_of_columns_encrypted = len(encrypted_columns)
        if number_of_columns_encrypted > 0:
            utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-columns"></i> Number of columns encrypted: <em>' + \
                str(number_of_columns_encrypted) + \
                '</em> (5 points less for each one). Total: -'+str(number_of_columns_encrypted * 5)+' utility points</li>'
            anon_utility = anon_utility - (number_of_columns_encrypted * 5)
        for column in df.columns:
            if column in perturbed_columns:
                # numeric
                utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-sort-numeric-up-alt"></i> Numeric column: <em>' + \
                    column + '</em>. -5 utility points. '
                anon_utility = anon_utility - 5
                # calculate the difference an substract between 0 and 10 points
                max_diff = df[column].mean() / 5
                substracted_points = 5 * (differences[column]/max_diff)
                utility_explain += 'Difference obtained: <em>' + str(differences[column]) + '</em>. Total: -'+str(round(substracted_points,2)+5)+' utility points</li>'
                anon_utility = anon_utility - substracted_points
            elif column in perturbed_binary:
                # binary
                utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-venus-mars"></i> Binary column: <em>' + \
                    column + '</em>. -5 utility points. '
                # Calculate the counts of each unique value in the 'gender' column for original data
                gender_counts = df[column].value_counts()

                # Calculate the counts of each unique value in the 'gender' column for anonymized data
                gender_counts_anon = anon[column].value_counts()

                # Merge the original and anonymized data counts
                merged_counts = gender_counts.to_frame().merge(
                    gender_counts_anon.to_frame(), left_index=True, right_index=True)
                merged_counts.columns = ['Original', 'Anonymized']

                # Calculate the counts of each binary value
                male_count_original = merged_counts['Original'][0]
                female_count_original = merged_counts['Original'][1]
                male_count_anonymized = merged_counts['Anonymized'][0]
                female_count_anonymized = merged_counts['Anonymized'][1]
                # Calculate the percentage difference in male and female counts
                dif_v1 = abs(round(
                    ((male_count_anonymized - male_count_original) / male_count_original), 2))
                dif_v2 = abs(round(
                    ((female_count_anonymized - female_count_original) / female_count_original), 2))
                substracted_points = 5 * (dif_v1 + dif_v2) / 2
                utility_explain += 'Differences obtained: <em>' + str(dif_v1*100) + '% y ' +str(dif_v2*100)+ '%</em>. Total: -'+str(round(substracted_points,2)+5)+' utility points</li>'
                anon_utility = anon_utility - substracted_points
            elif column in generalized_columns:
                # categorical
                utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-sort-numeric-up-alt"></i> Categorical column: <em>' + \
                    column + '</em>. -5 utility points. '
                anon_utility = anon_utility - 5
                max_diff = df[column].mean() / 5
                substracted_points = 5 * (differences[column]/max_diff)
                utility_explain += 'Difference obtained: <em>' + str(differences[column]) + '</em>. Total: -'+str(round(substracted_points,2)+5)+' utility points</li>'
                anon_utility = anon_utility - substracted_points
        
        # continent
        if len(country_columns) > 0:
            anon_utility = anon_utility - (5 * len(country_columns))
            utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-globe"></i> Continent: (5 points less for each column using generalization). Total: -'+str(5 * len(country_columns))+' utility points</li>'
        # security_card
        if len(masked_columns) > 0:
            anon_utility = anon_utility - (5 * len(masked_columns))
            utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-shield-alt"></i> Masking data: (5 points less for each column using masking). Total: -'+str(5 * len(masked_columns))+' utility points</li>'
        # transform utility to usa grading system
        if anon_utility >= 97:
            grade = "A+"
        elif anon_utility >= 93:
            grade = "A"
        elif anon_utility >= 90:
            grade = "A-"
        elif anon_utility >= 87:
            grade = "B+"
        elif anon_utility >= 83:
            grade = "B"
        elif anon_utility >= 80:
            grade = "B-"
        elif anon_utility >= 77:
            grade = "C+"
        elif anon_utility >= 73:
            grade = "C"
        elif anon_utility >= 70:
            grade = "C-"
        elif anon_utility >= 67:
            grade = "D+"
        elif anon_utility >= 63:
            grade = "D"
        elif anon_utility >= 60:
            grade = "D-"
        else:
            grade = "F"

        utility_explain += '<li style="margin-top: 10px;"><i class="fas fa-user-secret"></i> <strong>Anonymized utility: <em>' + \
            str(round(anon_utility,2)) + '</em> ('+grade+')</strong></li>'
        utility_explain += '</ul>'

        return render_template('result.html', original_column_names=df.columns.values, original_row_data=list(df.values.tolist()),
                               enc_column_names=anon.columns.values, enc_row_data=list(anon.values.tolist()), zip=zip, original_file=filename, enc_file=filename_without_ext+"_anonymized.csv",  modal=modal_steps, histograms=histograms, differences=differences, utility_explain=utility_explain)


@app.route('/generate')
def generate():

    # Delete old files
    files = glob.glob('static/*.png') + glob.glob('static/*.csv')
    for f in files:
        os.remove(f)

    id = uuid4()
    # Generate 2000 rows of data
    gen = GenerateDatabase(2000, 'static/'+str(id)+".csv")
    filename = gen.generate_database()
    df = pd.read_csv(filename)  # Read generated data

    modal_steps = ''  # Modal steps

    # Encrypt identifiers
    anon, key = encrypt_column(df, ["id", "name", "email"])
    print("Key: ", key)
    modal_steps += "<i class='fas fa-check text-success'></i> Encrypt identifiers (id, name, email)<br>"

    # Generalize numeric data (age)
    interval_width = random.randint(5, 10)  # Random interval width
    intervals = list(range(anon['age'].min(),  anon['age'].max(
    ) + interval_width, interval_width))  # Create intervals based on min and max age
    anon['age'] = generalize_numeric_data(
        anon['age'], intervals)  # Generalize age
    modal_steps += "<i class='fas fa-check text-success'></i> Generalize numeric data (age) using intervals of width: "+str(
        interval_width)+"<br>"

    # Perturb numeric data (salary)
    perturb_option = random.choice(
        ['gaussian', 'shuffle', 'numeric'])  # Random perturb option
    epsilon = random.uniform(0.1, 0.5)  # Random epsilon
    if perturb_option == 'gaussian':
        anon['salary'] = perturb_gaussian_data(anon['salary'], epsilon)
        modal_steps += "<i class='fas fa-check text-success'></i> Perturb numeric data (salary) using gaussian noise with epsilon " + str(
            round(epsilon, 2))+"<br>"
    elif perturb_option == 'shuffle':
        anon['salary'] = perturb_shuffle_data(anon['salary'])
        modal_steps += "<i class='fas fa-check text-success'></i> Perturb numeric data (salary) using shuffle<br>"
    else:
        anon['salary'] = perturb_numeric_data(anon['salary'], epsilon)
        modal_steps += "<i class='fas fa-check text-success'></i> Perturb numeric data (salary) with epsilon "+str(
            round(epsilon, 2))+"<br>"

    # Perturb binary data (gender)
    epsilon = random.uniform(0.01, 0.1)
    anon['gender'] = perturb_binary_data(anon['gender'], epsilon)
    modal_steps += "<i class='fas fa-check text-success'></i> Perturb binary data (gender) with epsilon "+str(
        round(epsilon, 2))+"<br>"

    # Generalize country name to continent
    for country in anon['country'].unique():
        anon['country'] = anon['country'].replace(
            country, country_to_continent(country))  # Replace country name with continent
    anon.rename(columns={'country': 'continent'},
                inplace=True)  # Rename column
    modal_steps += "<i class='fas fa-check text-success'></i> Generalize country name to continent (country)<br>"

    # Mask security number
    anon['credit_card_security_code'] = masking_data(
        anon['credit_card_security_code'])
    modal_steps += "<i class='fas fa-check text-success'></i> Mask credit card security number (credit_card_security_code)<br>"

    # Save anonymized data
    anon.to_csv("static/"+str(id)+"anonymized.csv", index=False)

    # Save decrypted data
    key, data = reverse_encryption(anon, ["id", "name", "email"], key)
    data.to_csv("static/"+str(id)+"decrypted.csv", index=False)

    # HISTOGRAMS
    histograms = {}
    differences = {}

    # Create a histogram of the original age column
    hist_plot = df['age'].plot.hist(
        color='blue', alpha=0.5, label='Original age')  # set color and transparency

    # Set x and y axis labels
    plt.xlabel('Age')
    plt.ylabel('Frequency')

    # Add a trend line
    mean_age = df['age'].mean()
    # add a vertical line for the mean age
    plt.axvline(mean_age, color='red', linestyle='--',
                label='Mean original age')

    # Save the histogram as an image file
    hist_plot.get_figure().savefig('static/histogram1_'+str(id)+'.png')

    # Create a histogram of the anonymized age column
    original = anon['age']
    anon['age'] = anon['age'].apply(lambda x: x.split(', ')[
                                    0].replace('[', ''))
    anon['age'] = anon['age'].astype(int)
    anon['age'] = anon['age'].apply(lambda x: x + int(interval_width/2))
    hist_plot = anon['age'].plot.hist(
        color='green', alpha=0.5, label='Anonymized age')  # set color and transparency

    # Add a trend line
    mean_age_anon = anon['age'].mean()
    # add a vertical line for the mean anonymized age
    plt.axvline(mean_age_anon, color='blue',
                linestyle='-', label='Mean anonymized Age')

    # Print the difference between original and anonymized data
    age_difference = round(abs(mean_age - mean_age_anon), 2)
    anon['age'] = original

    # add legend
    plt.legend()

    # Save the histogram as an image file
    hist_plot.get_figure().savefig('static/histogram1_'+str(id)+'.png')
    hist_plot.get_figure().clear()
    histograms['age'] = 'histogram1_'+str(id)+'.png'
    differences['age'] = age_difference

    # Create a histogram of the original salary column
    hist_plot = df['salary'].plot.hist(
        color='orange', alpha=0.5, label='Original salary')  # set color and transparency

    # Set x and y axis labels
    plt.xlabel('Salary')
    plt.ylabel('Frequency')

    # Add a trend line
    mean_salary = df['salary'].mean()
    # add a vertical line for the mean salary
    plt.axvline(mean_salary, color='red', linestyle='--',
                label='Mean original salary')

    # Save the histogram as an image file
    hist_plot.get_figure().savefig('static/histogram2_'+str(id)+'.png')

    # Create a histogram of the anonymized salary column
    hist_plot = anon['salary'].plot.hist(
        color='purple', alpha=0.5, label='Anonymized salary')  # set color and transparency

    # Add a trend line
    mean_salary_anon = anon['salary'].mean()
    # add a vertical line for the mean anonymized salary
    plt.axvline(mean_salary_anon, color='blue',
                linestyle='-', label='Mean anonymized salary')

    # Print the difference between original and anonymized data
    salary_difference = round(abs(mean_salary - mean_salary_anon), 2)

    # add legend
    plt.legend()

    # Save the histogram as an image file
    hist_plot.get_figure().savefig('static/histogram2_'+str(id)+'.png')
    hist_plot.get_figure().clear()
    histograms['salary'] = 'histogram2_'+str(id)+'.png'
    differences['salary'] = salary_difference

    # Histogram for binary data

    # Calculate the counts of each unique value in the 'gender' column for original data
    gender_counts = df['gender'].value_counts()

    # Calculate the counts of each unique value in the 'gender' column for anonymized data
    gender_counts_anon = anon['gender'].value_counts()

    # Merge the original and anonymized data counts
    merged_counts = gender_counts.to_frame().merge(
        gender_counts_anon.to_frame(), left_index=True, right_index=True)
    merged_counts.columns = ['Original', 'Anonymized']

    # Calculate the counts of males and females in the original and anonymized datasets
    male_count_original = merged_counts['Original']['M']
    female_count_original = merged_counts['Original']['F']
    male_count_anonymized = merged_counts['Anonymized']['M']
    female_count_anonymized = merged_counts['Anonymized']['F']
    # Calculate the percentage difference in male and female counts
    percentage_male_difference = abs(round(
        ((male_count_anonymized - male_count_original) / male_count_original) * 100, 2))
    percentage_female_difference = abs(round(
        ((female_count_anonymized - female_count_original) / female_count_original) * 100, 2))

    # Create a pie chart with both original and anonymized data counts
    fig, ax = plt.subplots()
    ax.pie(merged_counts['Original'], labels=merged_counts.index,
           autopct='%1.1f%%', startangle=90, colors=['red', 'blue'], pctdistance=0.85)
    ax.pie(merged_counts['Anonymized'], autopct='%1.1f%%', startangle=90, colors=[
           'lightcoral', 'lightblue'], radius=0.75, pctdistance=0.5)
    plt.title('Gender Distribution (Original vs Anonymized)')

    legend_handles = [
        plt.Rectangle((0, 0), 1, 1, fc='none', edgecolor='red', linewidth=5),
        plt.Rectangle((0, 0), 1, 1, fc='none', edgecolor='blue', linewidth=5),
        plt.Rectangle((0, 0), 1, 1, fc='none',
                      edgecolor='lightcoral', linewidth=5),
        plt.Rectangle((0, 0), 1, 1, fc='none',
                      edgecolor='lightblue', linewidth=5)
    ]
    legend_labels = ['Original (M)', 'Original (F)',
                     'Anonymized (F)', 'Anonymized (M)']

    # Add legend with custom handles and labels
    ax.legend(legend_handles, legend_labels, loc='upper left')

    plt.savefig('static/pie_chart'+str(id)+'.png')
    plt.close()
    histograms['gender']='pie_chart'+str(id)+'.png'
    differences['gender'] = 'M' + ' difference: ' + str(percentage_male_difference) + '%, ' + 'F' + ' difference: ' + str(percentage_female_difference) + '%'


    utility_explain = ''
    utility_explain += '<ul style="list-style-type: none; padding: 0;">'
    utility_explain += '<li style="margin-bottom: 10px;"><i class="fas fa-calc"></i> <strong>Utility calculation:</strong></li>'
    original_utility = anon_utility = 100
    utility_explain += '<li style="margin-bottom: 5px;">Original utility: <em>' + \
        str(original_utility) + '</em></li>'
    # Compute utility score
    number_of_columns_encrypted = 3
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-columns"></i> Number of columns encrypted: <em>' + \
        str(number_of_columns_encrypted) + \
        '</em> (5 points less for each one)</li>'
    anon_utility = anon_utility - (number_of_columns_encrypted * 5)
    # age
    anon_utility = anon_utility - age_difference * 5
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-calendar-alt"></i> Age difference: <em>' + \
        str(age_difference) + \
        '</em> (5 points less for each year of difference)</li>'
    # salary
    anon_utility = anon_utility - salary_difference * 0.01
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-dollar-sign"></i> Salary difference: <em>' + \
        str(salary_difference) + \
        '</em> (0.01 points less for each dollar of difference)</li>'
    # gender
    anon_utility = anon_utility - percentage_male_difference
    anon_utility = anon_utility - percentage_female_difference
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-venus-mars"></i> Male/Female difference: <em>' + \
        str(percentage_male_difference) + '%/' + \
        str(percentage_female_difference) + '%</em></li>'

    # continent
    anon_utility = anon_utility - 5
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-globe"></i> Continent: (5 points less for using generalization)</li>'
    # security_card
    anon_utility = anon_utility - 5
    utility_explain += '<li style="margin-bottom: 5px;"><i class="fas fa-shield-alt"></i> Security card: (5 points less for using masking)</li>'
    utility_explain += '<li style="margin-top: 10px;"><i class="fas fa-user-secret"></i> <strong>Anonymized utility: <em>' + \
        str(anon_utility) + '</em></strong></li>'
    utility_explain += '</ul>'

    # Return the result page
    return render_template('result.html', original_column_names=df.columns.values, original_row_data=list(df.values.tolist()),
                           enc_column_names=anon.columns.values, enc_row_data=list(anon.values.tolist()), zip=zip, original_file=str(id)+".csv", enc_file=str(id)+"anonymized.csv", dec_file="static/"+str(id)+"decrypted.csv", modal=modal_steps, utility_explain=utility_explain, histograms = histograms, differences = differences)


@app.route('/download/<string:filename>')
def download(filename):
    # as_attachment=True means that the browser will download the file instead of displaying it
    return send_file('static/'+filename, as_attachment=True)


def delete_files(signum, frame):
    files = glob.glob('static/*.png') + glob.glob('static/*.csv')
    for f in files:
        os.remove(f)
    exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, delete_files)
    app.run(debug=True)
