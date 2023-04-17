import random
import csv
from faker import Faker

# Global variables
NUM_ROWS = 1000
FILENAME = 'data.csv'

# Instantiate the Faker library
fake = Faker()

# Function to generate a random city
def generate_city():
    return fake.city()

# Function to generate a random age
def generate_age():
    return random.randint(18, 80)

# Function to generate a random gender
def generate_gender():
    return random.choice(['M', 'F'])

# Function to generate a random job title
def generate_job_title():
    return fake.job()

# Function to generate a random email address
def generate_email(id, name):
    domain = fake.free_email_domain()
    return f"{name.replace(' ', '.').lower()}{id % NUM_ROWS}@{domain}"

# Function to generate a salary
def generate_salary():
    return fake.pydecimal(left_digits=5, right_digits=2, min_value=20000, max_value=99999)

# Function to generate a credit card security code
def generate_credit_card_security_code():
    return fake.credit_card_security_code()

# Generate random data and write it to a CSV file
with open(FILENAME, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "name", "email", "age", "gender", "city", "job_title",
                    "salary", "credit_card_security_code"])
    for i in range(NUM_ROWS):
        id = random.randint(0, 99999)
        name = fake.name()
        email = generate_email(id, name)
        age = generate_age()
        gender = generate_gender()
        city = generate_city()
        job_title = generate_job_title()
        salary = generate_salary()
        credit_card_security_code = generate_credit_card_security_code()
        writer.writerow([id, name, email, age, gender, city, job_title,
                        salary, credit_card_security_code])
