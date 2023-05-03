from IPython import embed
import pandas as pd

# returns the attributes that violate k-anonymity, and how often they occur
def k_anon_violating_attrs(df, k, grouping_cols):
    grouping_cols_only = df[grouping_cols]
    grouped = grouping_cols_only.groupby(grouping_cols).size().reset_index(name='count')
    return grouped[grouped['count'] < k]

# returns a new dataframe with all rows that violate k-anonymity removed
def ensure_k_anon(df, k, grouping_cols):
    attributes_to_drop = k_anon_violating_attrs(df, k, grouping_cols)
    rows_to_drop = df.merge(attributes_to_drop).drop("count",axis=1)
    return df.drop(rows_to_drop.index)