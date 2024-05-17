import pandas as pd, numpy as np, os, sys
import re, string, ast
from datetime import datetime

def unlist_all_rows(df):
    for column in df.columns:
        df[column] = df[column].apply(
            lambda x: ' '.join(ast.literal_eval(x)) if isinstance(x, str) and x.startswith('[') and x.endswith(']') else
                      ' '.join(x) if isinstance(x, list) else x)
    return df


def merge_rows(df):
    # Group by labat_id
    grouped = df.groupby('labat_id')

    # Initialize an empty list to store merged rows
    merged_rows = []

    for _, group in grouped:
        # Initialize a dictionary to store merged row information
        merged_row = {}

        # Merge rows according to rules
        for col in group.columns:
            max_length = 0
            merged_value = None
            for val in group[col]:
                if pd.notnull(val):
                    if isinstance(val, str):
                        if len(val) > max_length:
                            max_length = len(val)
                            merged_value = val
                    else:
                        val_str = str(val)
                        if len(val_str) > max_length:
                            max_length = len(val_str)
                            merged_value = val_str

            merged_row[col] = merged_value

        # Append the merged row to the list of merged rows
        merged_rows.append(merged_row)

    # Create a DataFrame from the list of merged rows
    merged_df = pd.DataFrame(merged_rows)

    return merged_df

def extract_height(df):
    # Regular expression pattern to find the highest two-digit number
    pattern = r'\b(4[0-9]|[5-9][0-9]|100)\b'

    # Extract numbers from the "signalement" column for each row
    def extract_numbers(row):
        matches = re.findall(pattern, str(row))
        numbers = [int(match) for match in matches] if matches else []
        return max(numbers) + 100 if numbers else None

    # Apply the extraction function to each row
    df['taille (cm)'] = df['signalement'].apply(extract_numbers)

    # Convert dtype of "taille (cm)" column to int
    df['taille (cm)'] = pd.to_numeric(df['taille (cm)'], errors='coerce').astype('Int64')

    return df

def extract_inst(row):
    pattern = r'\b[0-5xX]\b'  # Regular expression pattern to match single-digit numbers or 'x' (case insensitive)
    match = re.search(pattern, row, re.IGNORECASE)
    if match:
        return match.group()
    return None

def extract_inst_militaire(row):
    # Regular expression pattern to match 'non' or 'exerce' (case insensitive)
    pattern = r'\b(non|exerce)\b'
    match = re.search(pattern, row, re.IGNORECASE)
    if match:
        # If 'non' is matched, return 'non exercé'
        if match.group() == 'non':
            return 'non exercé'
        # If 'exerce' is matched, return 'exercé'
        else:
            return 'exercé'
    return None

def extract_classe(row):
     four_digit_pattern = r'\b(18[89]\d|19[01]\d)\b'
     match = re.search(four_digit_pattern, str(row))
     if match:
        matched_year = int(match.group())
        if 1887 <= matched_year <= 1921:
            return match.group()
     return None

def extract_certificat(text):
    words_to_find = ["certificat", "bonne", "conduite"]
    found_words = [word for word in words_to_find if re.search(r'[^\w\s]'.format(word), text)]
    if "certificat" in found_words and len(found_words) > 1:
         accorded_words = ["a reçu", "a recu", "accordé", "accorde", "Accorde", "Accordé"]
         refused_words = ["refuse", "refusé", "n'a pas", "n a pas", "Refusé", "Refuse"]
         for word in text.split():
              word_stripped = re.sub(r'[^\w\s]', '', word)
              if any(word_stripped.startswith(acc_word) for acc_word in accorded_words):
                    return "accordé"
              elif word_stripped in refused_words:
                    return "refusé"
    return None


def extract_decision(text, CONSTANT):
     count = {key: 0 for key in CONSTANT}
     for keyword in CONSTANT:
          for word in text.split():
               for keyword_value in CONSTANT[keyword]:
                    if keyword_value in word:
                         count[keyword] += 1
     max_count = max(count.values())
     if max_count == 0 and ('bon' in text.split()):
          return 'bon pour le service armé'
     percentage_digits = sum(c.isdigit() for c in text.strip()) / max(len(text.strip()), 1)
     threshold = 0.4
     if max_count == 0 and percentage_digits > threshold and '1' in text.strip():
        return 'bon pour le service armé'
     if max_count == 0 and percentage_digits > threshold and '2' in text.strip():
        return 'bon pour le service auxiliaire'
     if max_count == 0 and percentage_digits > threshold and '3' in text.strip():
        return 'engagé volontaire'
     if max_count == 0 and percentage_digits > threshold and '5' in text.strip():
        return 'ajourné'
     max_keys = [key for key, value in count.items() if value == max_count]
     if len(max_keys) == 1:
          return max_keys[0]
     else:
          last_key = None
          for word in text.split():
               for key in max_keys:
                    if any(keyword_value in word for keyword_value in CONSTANT[key]):
                         last_key = key
          return last_key

def categorize_country(country):
    if country == 'France':
        return 'France'
    elif country:
        return 'Etranger'
    else:
        return None

def fill_classe(row):
    # Check if the "classe" column is empty
    if pd.isnull(row['année_classe']):
        # Extract the year from the "Date de naissance" column if it's not NaN
        if not pd.isnull(row['Date de naissance']):
            year = int(row['Date de naissance'].split('/')[-1])
            # Add twenty to the year
            classe = year + 20
            # Fill the "classe" column with the calculated value
            row['année_classe'] = classe
    return row

def extract_prenom(df):
    # Create a new column for the first name
    df['prenom1'] = ""

    # Iterate over each row in the 'Prénom(s)' column
    for index, row in df.iterrows():
        # Check if the value in the 'Prénom(s)' column is a string
        if isinstance(row['Prénom(s)'], str):
            # Split the string into words
            names = row['Prénom(s)'].split()
            # If there is at least one word, assign the first word as the first name
            if len(names) >= 1:
                df.at[index, 'prenom1'] = names[0]

    return df

def extract_junior(row):
    # Check if either column is empty
    if pd.isnull(row['Prénom(s)']) or pd.isnull(row['etat_civil']):
        return None

    # Extract names from the "Prénom(s)" column
    names = row['Prénom(s)'].split()

    # Extract etat_civil and remove punctuation and extra spaces
    etat_civil = re.sub(r'[^\w\s]', '', row['etat_civil']).strip()

    # Check if any of the names appear in etat_civil
    for name in names:
        if re.search(r'\b{}\b'.format(re.escape(name)), etat_civil, re.IGNORECASE):
            return True

    # If no matching names found
    return False

def extract_famille(row):
    # Check if decision column is empty
    if pd.isnull(row['decision']):
        return None

    # Extract decision and remove extra spaces
    decision = row['decision'].strip()

    # Check for the occurrence of "veuve" or "orphelin"
    veuve_match = re.search(r'\b(la )?veuve\b', decision, re.IGNORECASE)
    orphelin_match = re.search(r'\b(la )?d\'?orphelin\w*\b', decision, re.IGNORECASE)
    etranger_match = re.search(r'\b(la )?etranger\b', decision, re.IGNORECASE)
    soutien_match = re.search(r'\b(la )?soutien\b', decision, re.IGNORECASE)

    # If both "veuve" and "orphelin" are found or only "orphelin" is found
    if (veuve_match and orphelin_match) or orphelin_match:
        return 'orphelin'

    # If only "veuve" is found
    elif veuve_match:
        return 'veuve'

    elif etranger_match:
        return 'etranger'

    elif soutien_match:
        return 'soutien'

    # If neither "veuve" nor "orphelin" is found
    else:
        return None

def update_colony(row):
    if row['pays'] == 'Nouvelle-Calédonie (zone économique exclusive)':
        row['pays'] = 'France'
    elif row['pays'] == "Sénégal":
        row['pays'] = 'France'
    elif row['pays'] == 'République démocratique du Congo':
        row['pays'] = 'France'
    elif row['pays'] == 'Mali':
         row['pays'] = 'France'
    elif row['pays'] == 'Algérie ⵍⵣⵣⴰⵢⴻⵔ الجزائر':
        row['pays'] = 'France'
    return row

def update_vienne(row):
    if row['Lieu de naissance'] == 'Vienne' :
        row['pays'] = 'France'
    return row

def extract_permis(row):
    # Check if decision column is empty
    if pd.isnull(row['decision']):
        return None

    # Extract decision and remove extra spaces
    decision = row['decision'].strip()

    # Check for the occurrence of "permis"
    permis_match = re.search(r'\bpermis\b', decision, re.IGNORECASE)
    # If "permis" is found
    if permis_match:
        return 'permis'

    else:
        return None

def extract_cm(row):
    # Check if arme column is infantry
    if row['arme'] == 'Infanterie':
        affectation = row['affectation'].strip()
        cm_match = re.search(r'\bcm\b', affectation, re.IGNORECASE)
        if cm_match:
            return True
        else:
            return False
    else:
        False

def check_criminel(row):
    if pd.isnull(row['details']):
        return None

    details = row['details'].strip()

    details_prison = re.search(r'\bprison\b', details, re.IGNORECASE)
    details_condamné = re.search(r'\bcondamné\b', details, re.IGNORECASE)
    details_cond = re.search(r'\bcond^né\b', details, re.IGNORECASE)
    details_amende = re.search(r'\bamende\b', details, re.IGNORECASE)

    if details_prison or details_condamné or details_cond or details_amende:
        return 'condamné'
    if pd.isnull(row['cassier']):
        return None
    casier = row['cassier'].strip()
    casier_prison = re.search(r'\bprison\b', casier, re.IGNORECASE)
    casier_condamné = re.search(r'\bcondamné\b', casier, re.IGNORECASE)
    casier_cond = re.search(r'\bcond^né\b', casier, re.IGNORECASE)
    casier_amende = re.search(r'\bamende\b', casier, re.IGNORECASE)

    if casier_prison or casier_condamné or casier_cond or casier_amende:
        return 'condamné'

    else:
        return None

def check_conseil(row):
    if pd.isnull(row['details']):
        return None

    details = row['details'].strip()

    details1 = re.search(r'\bconseil de guerre\b', details, re.IGNORECASE)
    details2 = re.search(r'\bconseildeguerre\b', details, re.IGNORECASE)
    details3 = re.search(r'\bconseil deguerre\b', details, re.IGNORECASE)
    details4 = re.search(r'\bconseilde guerre\\b', details, re.IGNORECASE)

    if details1 or details2 or details3 or details4:
        return 'conseil'
    if pd.isnull(row['cassier']):
        return None
    casier = row['cassier'].strip()
    casier1 = re.search(r'\bconseil de guerre\b', casier, re.IGNORECASE)
    casier2 = re.search(r'\bconseildeguerre\b', casier, re.IGNORECASE)
    casier3 = re.search(r'\bconseil deguerre\b', casier, re.IGNORECASE)
    casier4 =re.search(r'\bconseilde guerre\b', casier, re.IGNORECASE)

    if casier1 or casier2 or casier3 or casier4:
        return 'conseil'

    else:
        return None

def extract_grade(text, CONSTANT):
    max_grade = 0
    for grade, (terms, required) in CONSTANT.items():
        if grade in (1, 2):
            # For grades 1 and 2, at least one term from the first list and all terms from the second list are required
            pattern = r'(?:\b(?:' + '|'.join(terms) + r')\b.{0,5}(?:' + '|'.join(required) + r'))'
            matches = re.finditer(pattern, text)
            for match in matches:
                max_grade = max(max_grade, grade)
        else:
             pattern = r'\b(?:' + '|'.join(terms) + r')\b'
             matches = re.finditer(pattern, text)
             for match in matches:
                max_grade = max(max_grade, grade)

    return max_grade if max_grade > 0 else None

def extract_promotion(text, CONSTANT):
    found_ranks = set()
    for grade, (terms, required) in CONSTANT.items():
        if grade in (1, 2):
            # For grades 1 and 2, at least one term from the first list and all terms from the second list are required
            pattern = r'(?:\b(?:' + '|'.join(terms) + r')\b.{0,5}(?:' + '|'.join(required) + r'))'
            matches = re.finditer(pattern, text)
            for match in matches:
                found_ranks.add(grade)
        else:
            pattern = r'\b(?:' + '|'.join(terms) + r')\b'
            matches = re.finditer(pattern, text)
            for match in matches:
                found_ranks.add(grade)

    if len(found_ranks) < 2:
        return None
    else:
        return f"{min(found_ranks)}-{max(found_ranks)}"

def extract_promotion_list(text, CONSTANT):
    found_ranks = set()
    for grade, (terms, required) in CONSTANT.items():
        if grade in (1, 2):
            # For grades 1 and 2, at least one term from the first list and all terms from the second list are required
            pattern = r'(?:\b(?:' + '|'.join(terms) + r')\b.{0,5}(?:' + '|'.join(required) + r'))'
            matches = re.finditer(pattern, text)
            for match in matches:
                found_ranks.add(grade)
        else:
            pattern = r'\b(?:' + '|'.join(terms) + r')\b'
            matches = re.finditer(pattern, text)
            for match in matches:
                found_ranks.add(grade)

    if len(found_ranks) < 2:
        return None
    else:
        return sorted(found_ranks)

def extract_arme(text, CONSTANT):
    count = {key: 0 for key in CONSTANT}
    for keyword in CONSTANT:
        for word in text.split():
            for keyword_value in CONSTANT[keyword]:
                if keyword_value in word:
                   count[keyword] += 1
    max_count = max(count.values())
    if max_count == 0 or not text.strip():
        return None
    max_keys = [key for key, value in count.items() if value == max_count]
    if len(max_keys) == 1:
        return max_keys[0]
    else:
        last_key = None
        for word in text.split():
            for key in max_keys:
                if any(keyword_value in word for keyword_value in CONSTANT[key]):
                    last_key = key
        return last_key

def extract_age(birth_date_str, reference_date_str='1914-08-02'):
    # Convert birth date and reference date strings to datetime objects
    birth_date = datetime.strptime(birth_date_str, '%d/%m/%Y')
    reference_date = datetime.strptime(reference_date_str, '%Y-%m-%d')

    # Calculate age
    age = reference_date.year - birth_date.year - ((reference_date.month, reference_date.day) < (birth_date.month, birth_date.day))

    return age

def check_insoumis(row):
    if pd.isnull(row['decision']):
        return None

    decision = row['decision'].strip()
    decision_insoumis = re.search(r'\binsoumis\b', decision, re.IGNORECASE)
    decision_insoumission = re.search(r'\binsoumission\b', decision, re.IGNORECASE)

    if decision_insoumis or decision_insoumission:
        return 'insoumis'

    if pd.isnull(row['details']):
        return None

    details = row['details'].strip()
    details_insoumis = re.search(r'\binsoumis\b', details, re.IGNORECASE)
    details_insoumission = re.search(r'\binsoumission\b', details, re.IGNORECASE)

    if details_insoumis or details_insoumission:
        return 'insoumis'

    if pd.isnull(row['cassier']):
        return None

    casier = row['cassier'].strip()
    casier_insoumis = re.search(r'\binsoumis\b', casier, re.IGNORECASE)
    casier_insoumission = re.search(r'\binsoumission\b', casier, re.IGNORECASE)

    if casier_insoumis or casier_insoumission :
        return 'insoumis'

    else:
        return None

def check_etudiant(row):
    if pd.isnull(row['etat_civil']):
        return None

    etat_civil = row['etat_civil'].strip()
    c1 = re.search(r'\betudiant\b', etat_civil, re.IGNORECASE)
    c2 = re.search(r'\bétudiant\b', etat_civil, re.IGNORECASE)
    c3 = re.search(r'\bélève\b', etat_civil, re.IGNORECASE)
    c4 = re.search(r'\beleve\b', etat_civil, re.IGNORECASE)
    c5 = re.search(r'\béleve\b', etat_civil, re.IGNORECASE)
    c6 = re.search(r'\belève\b', etat_civil, re.IGNORECASE)

    if c1 or c2 or c3 or c4 or c5 or c6:
        return 'etudiant'

def check_prisonnier(row):
    if not pd.isnull(row['details']):
        detail = row['details'].strip()
        c1 = re.search(r'\bprisonnier\b', detail, re.IGNORECASE)
        c2 = re.search(r'\bcapturé\b', detail, re.IGNORECASE)
        c3 = re.search(r'\bpinterné\b', detail, re.IGNORECASE)
        c4 = re.search(r'\bpinterne\b', detail, re.IGNORECASE)
        c5 = re.search(r'\bcapture\b', detail, re.IGNORECASE)

        if c1 or c2 or c3 or c4 or c5:
            return 'prisonnier'

    if not pd.isnull(row['campagnes']):
        campagnes = row['campagnes'].strip()
        c1 = re.search(r'\bcaptivité\b', campagnes, re.IGNORECASE)
        c2 = re.search(r'\bcapturé\b', campagnes, re.IGNORECASE)
        c3 = re.search(r'\bpinterné\b', campagnes, re.IGNORECASE)
        c4 = re.search(r'\bpinterne\b', campagnes, re.IGNORECASE)
        c5 = re.search(r'\bcaptivite\b', campagnes, re.IGNORECASE)

        if c1 or c2 or c3 or c4 or c5:
            return 'prisonnier'

    return None


def check_mobiliser(row):
    if not pd.isnull(row['details']):
        detail = row['details'].strip()
        c1 = re.search(r"\bl'allemagne\b", detail, re.IGNORECASE)
        c2 = re.search(r'\bcallegamne\b', detail, re.IGNORECASE)
        c3 = re.search(r'\bporient\b', detail, re.IGNORECASE)
        c4 = re.search(r'\bsilésie\b', detail, re.IGNORECASE)
        c5 = re.search(r'\brhénans\b', detail, re.IGNORECASE)

        if c1 or c2 or c3 or c4 or c5:
            return 'mobilisé'

    if not pd.isnull(row['campagnes']):
        campagnes = row['campagnes'].strip()
        c6 = re.search(r"\bl'allemagne\b", campagnes, re.IGNORECASE)
        c7 = re.search(r'\bcallegamne\b', campagnes, re.IGNORECASE)
        c8 = re.search(r'\bporient\b', campagnes, re.IGNORECASE)
        c9 = re.search(r'\bsilésie\b', campagnes, re.IGNORECASE)
        c10 = re.search(r'\brhénans\b', campagnes, re.IGNORECASE)

        if c6 or c7 or c8 or c9 or c10:
            return 'mobilisé'

    return None

def check_blessure(row):
   if not pd.isnull(row['details']):
        detail = row['details'].strip()
        c1 = re.search(r'\bblessé\b', detail, re.IGNORECASE)
        c2 = re.search(r'\bblessure\b', detail, re.IGNORECASE)
        c3 = re.search(r'\bevacue\b', detail, re.IGNORECASE)
        c4 = re.search(r'\bevacué\b', detail, re.IGNORECASE)
        c5 = re.search(r'\bévacué\b', detail, re.IGNORECASE)
        c6 = re.search(r'\bbrulure\b', detail, re.IGNORECASE)
        c7 = re.search(r'\bblesse\b', detail, re.IGNORECASE)
        c16 = re.search(r'\bplaie\b', detail, re.IGNORECASE)
        if c1 or c2 or c3 or c4 or c5 or c6 or c7 or c16:
            return 'blessure'

   if not pd.isnull(row['blessures']):
       blessures = row['blessures'].strip()
       c8 = re.search(r'\bblessé\b', blessures, re.IGNORECASE)
       c9 = re.search(r'\bblessure\b', blessures, re.IGNORECASE)
       c10 = re.search(r'\bevacue\b', blessures, re.IGNORECASE)
       c11= re.search(r'\bevacué\b', blessures, re.IGNORECASE)
       c12 = re.search(r'\bévacué\b', blessures, re.IGNORECASE)
       c13 = re.search(r'\bbrulure\b', blessures, re.IGNORECASE)
       c14 = re.search(r'\bblesse\b', blessures, re.IGNORECASE)
       c15 = re.search(r'\bplaie\b', blessures, re.IGNORECASE)
       if c8 or c9 or c10 or c11 or c12 or c13 or c14 or c15:
            return 'blessure'
   return None

def extract_mort(text):
    words_to_find = ["décédé", "france", 'guerre', 'mort', 'disparu']
    found_words = [word for word in words_to_find if re.search(r'[^\w\s]'.format(word), text.lower())]
    if any(word in found_words for word in ["mort", "décédé", "disparu"]) or len(found_words) > 1:
         tuer = ["tué", 'tue', 'ennemi' ,'tombé', 'feu', 'champ', 'bataille', 'tombe']
         blessures = ["ambulance", "blessures"]
         gaz = ['gaz', 'intoxication']
         disparu = ['disparu']
         maladie = ['maladie']
         accident = ['accident']
         for word in text.lower().split():
              word_stripped = re.sub(r'[^\w\s]', '', word)
              if any(word_stripped.startswith(word) for word in tuer):
                    return "À l'ennemi"
              elif word_stripped in blessures:
                    return "Suite des blessures"
              elif word_stripped in gaz:
                    return "Gaz"
              elif word_stripped in disparu:
                    return 'Disparu'
              elif word_stripped in maladie:
                    return 'Maladie'
              elif word_stripped in accident:
                    return 'Accident'
    return None


def check_mitrailleur(row):
    if not pd.isnull(row['details']):
        detail = row['details'].strip()
        c1 = re.search(r"\bmitrailleur\b", detail, re.IGNORECASE)
        c2 = re.search(r'\bmitrailleures\b', detail, re.IGNORECASE)
        c3 = re.search(r'\bmitrailleuse\b', detail, re.IGNORECASE)

        if c1 or c2 or c3 :
            return 'mitrailleur'

    if not pd.isnull(row['affectation']):
        affectation = row['affectation'].strip()
        c4 = re.search(r'\bmitrailleur\b', affectation, re.IGNORECASE)
        c5 = re.search(r'\bmitrailleures\b', affectation, re.IGNORECASE)
        c6 = re.search(r'\bmitrailleuse\b', affectation, re.IGNORECASE)

        if c4 or c5 or c6 :
            return 'mitrailleur'

    return None

def extract_blessure(text):
    words_to_find = ["blessé", "blesse", 'evacué', 'blessure', 'brulure', 'évacué', 'évacue', 'plaie']
    found_words = [word for word in words_to_find if re.search(r'[^\w\s]'.format(word), text.lower())]
    if len(found_words) > 0:
         obus = ["obus", 'bombe', 'éclat', 'eclat', 'shrapnell', 'schrapnell']
         grenade = ['grenade']
         balle = ["balles", 'balle']
         gaz = ['gaz', 'intoxication', 'intorication']
         baionette = ['baionnette']
         accident = ['accident']
         for word in text.lower().split():
              word_stripped = re.sub(r'[^\w\s]', '', word)
              if any(word_stripped.startswith(word) for word in obus):
                    return "eclat"
              elif word_stripped in grenade:
                    return "grenade"
              elif word_stripped in balle:
                    return "balle"
              elif word_stripped in gaz:
                    return "gaz"
              elif word_stripped in baionette:
                    return 'baionnette'
              elif word_stripped in accident:
                    return 'accident'

    return None

def find_blessure(df):
    # Boolean mask to identify rows where 'blessures' column is NaN
    mask = df['blessures'].isna()

    # Apply the function to 'details' column only for rows where 'blessures' column is NaN
    df.loc[mask, 'blesse_2'] = df.loc[mask, 'details'].apply(lambda x: extract_blessure(x.lower()) if isinstance(x, str) else x)

    # Apply the function to 'blessures' column for all rows
    df['blesse_2'] = df['blessures'].apply(lambda x: extract_blessure(x.lower()) if isinstance(x, str) else x)

    return df

def extract_pension(text):
    # Lowercase the input text
    text = text.lower()

    # Regular expression to find occurrences of "pension" or "reforme" followed by a number with a percentage sign
    pattern = re.compile(r'(pension|reforme)\D*(\d{1,2}|100)\s*%')

    # Find all matches in the text
    matches = pattern.findall(text)

    max_percentage = 0
    for match in matches:
        # Extract the percentage value from the match
        percentage = int(match[1])

        # Update max_percentage if the current percentage is higher
        max_percentage = max(max_percentage, percentage)

    return max_percentage

def clean_pension(n):
    if n % 5 != 0 :
        return None
    if n < 10 :
        return None
    return n

def find_reforme(text):
    # Lowercase the input text
    text = text.lower()

    # Regular expression to find 'n°1' or 'n°2' after 'réformé', 'réforme', 'reformé', or 'reforme'
    pattern = re.compile(r'(?:réformé|réforme|reformé|reforme)\D*(n°[12])')

    # Find all matches in the text
    matches = pattern.findall(text)

    if matches:
        # Return the last match found
        return matches[-1]
    else:
        return None

def check_citation(row):
    if not pd.isnull(row['details']):
        detail = row['details'].strip()
        c1 = re.search(r"\bcité\b", detail, re.IGNORECASE)
        c2 = re.search(r'\bcite\b', detail, re.IGNORECASE)

        if c1 or c2 :
            return 'cité'

    if not pd.isnull(row['campagnes']):
        campagnes = row['campagnes'].strip()
        c3 = re.search(r'\bcité\b', campagnes, re.IGNORECASE)
        c4 = re.search(r'\bcité\b', campagnes, re.IGNORECASE)

        if c3 or c4  :
            return 'cité'

    if not pd.isnull(row['blessures']):
        blessures = row['blessures'].strip()
        c5 = re.search(r'\bcité\b', blessures, re.IGNORECASE)
        c6 = re.search(r'\bcite\b', blessures, re.IGNORECASE)

        if c5 or c6 :
            return 'cité'

    return None

def check_legion_dhonneur(row):
    if not pd.isnull(row['details']):
        detail = row['details'].strip()
        c1 = re.search(r"\bd[']honneur\b", detail, re.IGNORECASE)
        c2 = re.search(r"\bchamp\b", detail, re.IGNORECASE)

        if c1 and not c2:
            return "légion d'honneur"

    if not pd.isnull(row['campagnes']):
        campagnes = row['campagnes'].strip()
        c1 = re.search(r"\bd[']honneur\b", campagnes, re.IGNORECASE)
        c2 = re.search(r"\bchamp\b", campagnes, re.IGNORECASE)

        if c1 and not c2:
            return "légion d'honneur"

    if not pd.isnull(row['blessures']):
        blessures = row['blessures'].strip()
        c1 = re.search(r"\bd[']honneur\b", blessures, re.IGNORECASE)
        c2 = re.search(r"\bchamp\b", blessures, re.IGNORECASE)

        if c1 and not c2:
            return "légion d'honneur"

    return None

def check_medals(row):
    columns = ['details', 'campagnes' , 'blessures']
    awards = []
    for column in columns:
        if not pd.isnull(row[column]):
            text = row[column].strip()
            # Use a single regular expression to match "médaille militaire" with or without accents
            match = re.search(r"\bm[ée]daille\s+militaire\b", text, re.IGNORECASE)
            if match:
                awards.append("médaille militaire")

    for column in columns:
        if not pd.isnull(row[column]):
            text = row[column].strip()
            # Use a single regular expression to match "médaille militaire" with or without accents
            match = re.search(r"\bm[ée]daille\s+coloniale\b", text, re.IGNORECASE)
            if match:
                awards.append("médaille coloniale")

    for column in columns:
        if not pd.isnull(row[column]):
            text = row[column].strip()
            # Use a single regular expression to match "médaille militaire" with or without accents
            match = re.search(r"\bm[ée]daille\s+de\s+la\s+victoire\b", text, re.IGNORECASE)
            if match:
                awards.append("médaille de la victoire")

    for column in columns:
        if not pd.isnull(row[column]):
            text = row[column].strip()
            # Use a single regular expression to match "médaille militaire" with or without accents
            match = re.search(r"\bcroix\s+du\s+combat", text, re.IGNORECASE)
            if match:
                awards.append("croix du combattant volontaire")

    for column in columns:
        if not pd.isnull(row[column]):
            text = row[column].strip()
            # Use a single regular expression to match "médaille militaire" with or without accents
            match = re.search(r"\bcroix\s+de\s+guerre\b", text, re.IGNORECASE)
            if match:
                awards.append("croix de guerre")
    if len(awards) == 0:
        return None
    if len(awards) > 0:
        awards = list(set(awards))
        awards = ', '.join(awards)
        return awards
    return None

