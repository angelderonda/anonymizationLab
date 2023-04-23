from anonymization import generalize_numeric_data, perturb_numeric_data, country_to_continent, perturb_shuffle_data, perturb_gaussian_data
import pandas as pd
import random
import requests

# Example data: heights in centimeters
heights = pd.Series([150, 162, 167])

# Generalization intervals
intervals = [150, 155, 160, 165, 170]

# Call the function to generalize the heights
generalized_heights = generalize_numeric_data(heights, intervals)

# Print the result
print("Generalized heights:")
for interval, count in generalized_heights.value_counts().items():
    print(f"Less than {interval} cm: {count} persons")


# Privacy parameter
epsilon = 25

# Perturb the ages and heights using perturb_numeric_data function
perturb_numeric_data = perturb_numeric_data(heights, epsilon)

# Perturb the order of data using perturb_shuffle_data function
perturb_shuffle_data = perturb_shuffle_data(heights)

# Perturb the data using perturb_gaussian_data function
perturb_gaussian_data = perturb_gaussian_data(heights, epsilon)

# Print the original and perturbed data
print("Original heights:", heights.tolist())
print("perturb_numeric_data heights:", perturb_numeric_data.tolist())
print("perturb_shuffle_data heights:", perturb_shuffle_data.tolist())
print("perturb_gaussian_data heights:", perturb_gaussian_data.tolist())


# Copy paste from "generateDatabase.py"
def generate_countries():
    # Fetch country data from the web
    response = requests.get("https://raw.githubusercontent.com/mledoze/countries/master/countries.json")
    if response.status_code == 200:
        countries_data = response.json()
        countries = []
        for country_data in countries_data:
            country_common_name = country_data.get("name", {}).get("common")
            if country_common_name:
                countries.append(country_common_name)     
        return countries
    else:
        print("Failed to fetch country data")

for country in range(10):

    # Ejemplo de uso
    countries = generate_countries()
    country = random.choice(countries)
    continent = country_to_continent(country)
    if continent:
        print("Country:", country)
        print("Continent:", continent)
    else:
        print("Error with:", country)
