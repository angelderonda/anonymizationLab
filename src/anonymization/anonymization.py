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
    generalized_data = pd.cut(data, intervals, labels=[
                              f'[{intervals[i]}, {intervals[i+1]})' for i in range(len(intervals)-1)], right=False)
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
    std_dev = np.std(data)
    epsilon = epsilon * std_dev
    perturbed_data = data + \
        pd.Series([random.uniform(-epsilon, epsilon)
                  for _ in range(len(data))])
    # round to 2 decimal places
    perturbed_data = perturbed_data.round(2)
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
    std_dev = np.std(data)
    epsilon = epsilon * std_dev
    noise = np.random.normal(0, epsilon, len(data))
    perturbed_data = data + pd.Series(noise)
    perturbed_data = perturbed_data.round(2)
    return perturbed_data

# Define a function to mask data


def mask_string(s):
    length = len(s)
    if length < 2:
        return s
    else:
        censor_len = max(length // 2, 1)
        uncensor_start = (length - censor_len) // 2
        uncensor_end = uncensor_start + censor_len
        return '*' * uncensor_start + s[uncensor_start:uncensor_end] + '*' * (length - uncensor_end)

def masking_data(data):
    """
    Masking a column of data in a Pandas DataFrame by censoring some some characters.

    Args:
        data (pd.Series): A Pandas Series containing data.

    Returns:
        pd.Series: A new Pandas Series that contains the masked data.
    """
    # convert to string
    data = data.astype(str)
    masked_data = data.apply(mask_string)
    return masked_data


def perturb_binary_data(data, probability=0.1):
    """
    Perturbs binary data by flipping values with a certain probability.

    Args:
        data (list, array, or Series): The binary data to be perturbed.
        probability (float, optional): The probability of flipping a value. Defaults to 0.1.

    Returns:
        list, array, or Series: The perturbed binary data.
    """
    perturbed_data = data.copy()
    # get the unique values
    unique_values = np.unique(perturbed_data)
    # replace the binary values with 0 and 1
    perturbed_data = np.where(perturbed_data == unique_values[0], 0, 1)
    # flip values with probability
    for i in range(len(perturbed_data)):
        if random.random() < probability:
            if perturbed_data[i] == 0:
                perturbed_data[i] = 1
            else:
                perturbed_data[i] = 0
    # convert back to boolean
    perturbed_data = np.where(
        perturbed_data == 0, unique_values[0], unique_values[1])
    return perturbed_data

# Generalization of categorical data (city --> continent)


def country_to_continent(country_name):
    country_alpha2 = pc.country_name_to_country_alpha2(country_name)
    try:
        country_continent_code = pc.country_alpha2_to_continent_code(
            country_alpha2)
        country_continent_name = pc.convert_continent_code_to_continent_name(
            country_continent_code)
        return country_continent_name
    except:
        return 'Unknown'
