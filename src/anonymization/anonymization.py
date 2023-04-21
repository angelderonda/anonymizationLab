import pandas as pd
import random
import pycountry_convert as pc
import numpy as np


def generalize_numeric_data(data, intervals):
    """
    Generalizes a column of numerical data in a Pandas DataFrame into given intervals.

    Args:
        data (pd.Series): A Pandas Series containing numerical data.
        intervals (list): List of intervals to generalize the data.

    Returns:
        pd.Series: A new Pandas Series that contains the generalized data.
    """
    generalized_data = pd.cut(data, intervals, labels=intervals[:-1], right=False)
    return generalized_data


def perturb_numeric_data(data, epsilon):
    """
    Perturbs a column of numeric data in a Pandas DataFrame by adding random noise.

    Args:
        data (pd.Series): A Pandas Series containing numeric values.
        epsilon (float): Privacy parameter controlling the amount of noise to be added.

    Returns:
        pd.Series: A new Pandas Series that contains the perturbed numeric values.
    """
    perturbed_data = data + pd.Series([random.uniform(-epsilon, epsilon) for _ in range(len(data))])
    return perturbed_data

def perturb_shuffle_data(data):
    """
    Perturbs the order of data in a Pandas DataFrame by randomly shuffling the rows.

    Args:
        data (pd.DataFrame): A Pandas DataFrame containing the data to be perturbed.

    Returns:
        pd.DataFrame: A new Pandas DataFrame that contains the perturbed data with shuffled rows.
    """
    perturbed_data = data.sample(frac=1).reset_index(drop=True)
    return perturbed_data

def perturb_gaussian_data(data, epsilon):
    """
    Perturbs a column of numeric data in a Pandas DataFrame by adding Gaussian noise.

    Args:
        data (pd.Series): A Pandas Series containing numeric values.
        epsilon (float): Privacy parameter controlling the amount of noise to be added.

    Returns:
        pd.Series: A new Pandas Series that contains the perturbed numeric values.
    """
    noise = np.random.normal(0, epsilon, len(data))
    perturbed_data = data + pd.Series(noise)
    return perturbed_data


# Generalization of categorical data (city --> continent)
def country_to_continent(country_name):
    
    country_alpha2 = pc.country_name_to_country_alpha2(country_name)
    country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name




