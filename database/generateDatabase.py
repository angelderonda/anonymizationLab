import random
import csv
from faker import Faker
import pycountry


class GenerateDatabase():
    def __init__(self, num_rows, filename):
        self.fake = Faker()  # Instantiate the Faker library
        self.num_rows = num_rows
        self.filename = filename

    # Function to generate a random country
    def generate_countries(self):
        all_countries = list(pycountry.countries)
        return [country.name for country in all_countries]

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
    def generate_email(self, id, name):
        domain = self.fake.free_email_domain()
        return f"{name.replace(' ', '.').lower()}{id % self.num_rows}@{domain}"

    # Function to generate a salary
    def generate_salary(self):
        return self.fake.pydecimal(left_digits=5, right_digits=2, min_value=20000, max_value=99999)

    # Function to generate a credit card security code
    def generate_credit_card_security_code(self):
        return self.fake.credit_card_security_code()

    # Function to generate a random email address
    def generate_email(self, id, name):
        domain = self.fake.free_email_domain()
        return f"{name.replace(' ', '.').lower()}{id % 1000}@{domain}"

    def generate_database(self):
        # Generate random data and write it to a CSV file
        countries = self.generate_countries()
        with open(self.filename, "w", newline="", encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["id", "name", "email", "age", "gender", "country", "job_title",
                            "salary", "credit_card_security_code"])
            for i in range(self.num_rows):
                id = random.randint(0, 99999)
                name = self.fake.name()
                email = self.generate_email(id, name)
                age = self.generate_age()
                gender = self.generate_gender()
                country = random.choice(countries)
                job_title = self.generate_job_title()
                salary = self.generate_salary()
                credit_card_security_code = self.generate_credit_card_security_code()
                writer.writerow([id, name, email, age, gender, country, job_title,
                                salary, credit_card_security_code])
        return self.filename

#db = GenerateDatabase(500, "prueba.csv")
#db.generate_database()
