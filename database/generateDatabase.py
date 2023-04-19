import random
import csv
from faker import Faker

class GenerateDatabase():
    def __init__(self, num_rows):
        self.fake = Faker() # Instantiate the Faker library
        self.num_rows = num_rows
        self.filename = 'data.csv'

    # Function to generate a random city
    def generate_city(self):
        return self.fake.city()

    # Function to generate a random age
    def generate_age(self):
        return random.randint(18, 80)

    # Function to generate a random gender
    def generate_gender(self):
        return random.choice(['M', 'F'])

    # Function to generate a random job title
    def generate_job_title(self):
        return self.fake.job()

    # Function to generate a random email address
    def generate_email(self,id, name):
        domain = self.fake.free_email_domain()
        return f"{name.replace(' ', '.').lower()}{id % 1000}@{domain}"

    def generate_database(self):
        # Generate random data and write it to a CSV file
        with open(self.filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "email", "age", "gender", "city", "job_title"])
            for i in range(self.num_rows):
                id = random.randint(0, 99999)
                name = self.fake.name()
                email = self.generate_email(id, name)
                age = self.generate_age()
                gender = self.generate_gender()
                city = self.generate_city()
                job_title = self.generate_job_title()
                writer.writerow([id, name, email, age, gender, city, job_title])
        return self.filename
