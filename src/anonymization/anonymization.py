import pandas as pd
import random

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
