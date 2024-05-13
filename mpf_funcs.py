import pandas as pd, numpy as np, os, sys
import re, string, ast, random
from datetime import datetime

#constants
MPF_COLUMNS = ['id_mention_intitule', 'classe', 'recrutement_matricule', 'id_recrutement_bureau_intitule',
                  'id_grade_intitule', 'id_unite_intitule', 'deces_jour_mois_annee', 'id_deces_lieu_intitule',
                  'id_deces_departement_intitule', 'id_deces_pays_intitule']

#funcs

def update_caledonie(row):
    if row['pays'] == 'Nouvelle-Calédonie (zone économique exclusive)':
        row['pays'] = 'France'
    return row

def lowercase_column(df, column_name):
    df[column_name] = df[column_name].str.lower()

def convert_date_format(date_str):
    try:
        # Try to parse the date using datetime.strptime
        date_object = datetime.strptime(date_str, '%Y-%m-%d')
        # If successful, return the date in the desired format
        return date_object.strftime('%d/%m/%Y')
    except ValueError:
        # If parsing fails, split the date string and rearrange the parts
        parts = date_str.split('-')
        # Check if the date string has three parts (year, month, day)
        if len(parts) == 3:
            # Rearrange the parts to form the desired format
            return '/'.join([parts[2], parts[1], parts[0]])
        else:
            # If the format doesn't match, return the original string
            return date_str


def check_labat_ids(merged_df, big_df):
    # Create a set of labat_ids from merged_df for faster lookup
    merged_labat_ids = set(merged_df['labat_id'])

    # Create a new column 'mpf' in big_df and initialize with False
    big_df['mpf'] = False

    # Iterate through each row in big_df
    for index, row in big_df.iterrows():
        labat_id = row['labat_id']
        # Check if labat_id exists in merged_labat_ids
        if labat_id in merged_labat_ids:
            # Set 'mpf' to True if labat_id is found in merged_df
            big_df.at[index, 'mpf'] = True

    return big_df

def extract_classe_and_random(row):
    four_digit_pattern = r'\b(18[89]\d|19[01]\d)\b'
    matches = re.findall(four_digit_pattern, str(row))
    if matches:
        matched_years = [int(match) for match in matches if 1887 <= int(match) <= 1921]
        if matched_years:
            return str(random.choice(matched_years))
    return None

def extract_year(string):
    if pd.isna(string):
        return None
    return extract_classe_and_random(string)

def update_grade(df):
    df.loc[df['mpf'], 'grade'] = df.loc[df['mpf'], 'mpf_grade_normalized']
    return df

