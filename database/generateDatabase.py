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
    return f"{name.replace(' ', '.').lower()}{id % 1000}@{domain}"

# Generate random data and write it to a CSV file
with open(FILENAME, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "name", "email", "age", "gender", "city", "job_title"])
    for i in range(NUM_ROWS):
        id = random.randint(0, 99999)
        name = fake.name()
        email = generate_email(id, name)
        age = generate_age()
        gender = generate_gender()
        city = generate_city()
        job_title = generate_job_title()
        writer.writerow([id, name, email, age, gender, city, job_title])
