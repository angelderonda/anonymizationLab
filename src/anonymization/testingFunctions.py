from anonymization import generalize_numeric_data,perturb_numeric_data
import pandas as pd
import random

# Example data: heights in centimeters
heights = pd.Series([150, 162, 167, 172, 175, 180, 185, 190, 195, 200])

# Generalization intervals
intervals = [160, 170, 180, 190]

# Call the function to generalize the heights
generalized_heights = generalize_numeric_data(heights, intervals)

# Print the result
print("Generalized heights:")
for interval, count in generalized_heights.value_counts().items():
    print(f"Less than {interval} cm: {count} persons")

# Example data: ages and heights
ages = pd.Series([25, 30, 35, 40, 45])
heights = pd.Series([160, 165, 170, 175, 180])

# Privacy parameter
epsilon = 25

# Perturb the ages and heights
perturbed_ages = perturb_numeric_data(ages, epsilon)
perturbed_heights = perturb_numeric_data(heights, epsilon)

# Print the original and perturbed data
print("Original ages:", ages.tolist())
print("Perturbed ages:", perturbed_ages.tolist())
print("Original heights:", heights.tolist())
print("Perturbed heights:", perturbed_heights.tolist())


