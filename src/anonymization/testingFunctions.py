from anonymization import generalize_numeric_data, perturb_numeric_data, country_to_continent, perturb_shuffle_data, perturb_gaussian_data
import pandas as pd
import numpy as np
import random
from geopy.geocoders import Nominatim

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
def generate_country():
    geolocator = Nominatim(user_agent="myGeocoder")
    while True:
        latitude = random.uniform(-90, 90)
        longitude = random.uniform(-180, 180)
        location = geolocator.reverse(
            f"{latitude}, {longitude}", language='en')
        if location is not None:
            address = location.raw['address']
            country = address.get('country', '')
            if country not in ['Water', 'Ocean']:
                return country
        else:
            continue


for country in range(2):

    # Ejemplo de uso
    country = generate_country()
    continent = country_to_continent(country)
    if continent:
        print("Country:", country)
        print("Continent:", continent)
    else:
        print("Error with:", country)
