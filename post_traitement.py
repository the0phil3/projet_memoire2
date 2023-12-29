import pandas as pd
import re
import numpy as np
import string
from unidecode import unidecode

# Define a dictionary to map accented characters to their non-accented counterparts
accented_chars = {
    'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a', 'å': 'a',
    'ç': 'c',
    'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
    'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
    'ñ': 'n',
    'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
    'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
    'ý': 'y',
}

# Define a dictionary of different branches of the army
affectation_dico = {
    "Infanterie": ["infa", "chasseurs a pied", "chasseur a pied", " ri ", "infanterie", 
                   "infie", "infi", "infe", "ifie", "interie" ],
    "Troupes coloniales" : ["tirail", "goum", "afrique", "spahis", "coloniaux", 
                            "zouaves", "etranger", "tirailleurs", "colo"],
    "Aviation" : ["avia", "aero"],
    "Train" : ["train"],
    "Genie" : ["genie"],
    "Cavalerie" : ["dragons", "cuirassiers", "chasseurs", "hussard", "huss", "chasseurs a cheval",
                   "chas a cheval", "chasseur a cheval", "drag"],
    "Artillerie" : ["art", "ouvriers dart", "ouv art", "ouv d art", 
                    "boa", "alc", "r a ", "dartillerie" , "legere portee"],
    "Corps medical" : ["infirmier"],
    "Service auxiliaire" : ["aux", "etat major", "coa", "sem", "em" ],
    "Affectations spéciales" : ["special", "usine"]
}

#Define a dictionary for the decision region
decision_dico = {
    "Bon pour le service armé": ["arme", "armé"],
    "Exempté" : ["dispense", "exempte", "dispensé", "exempté", "dipensé", "dipense"],
    "Ajourné" : ["ajourne", "ajourné", "sejourne", "sejourné"],
    "Bon absent" : ["absent"],
    "Bon pour le serivce auxiliaire" : ["auxil", "auxiliaire", "faible"],
    "Engagé volontaire" : ["engage", "volontaire", "engagé"]
}

#Define a dictionary for the ranks of soldiers
grade_dico = {
    1: (["soldat", "sapeur", "hussard", "chasseur", "cycliste", "cavalier", "cuirassier", "cuir", "cannonier"], ["2", "classe"]),
    2: (["soldat", "sapeur", "hussard", "chasseur", "cycliste", "cavalier", "cuirassier", "cuir", "cannonier"], ["1", "classe"]),
    3: (["caporal", "brigadier"], []),
    4: (["chaporal chef", "brigdaier chef", "chaporalchef", "brigdaierchef"], []),
    5: (["sergent", "marechal des logis", "logis"], []),
    6: (["fourier", "sergent chef"], []),
    7: (["adjudant"], []),
    8: (["adjudant chef"], []),
    9: (["aspirant"], []),
    10: (["s lieutenant", "sous lieut", "s lieut", "ss lieu"], []),
    11: (["lieutenant", "lieut"], []),
    12: (["capitaine"], []),
    13: (["commandant"], []),
    14: (["colonel"], [])
}

def remove_accented_characters(text):
    for char, replacement in accented_chars.items():
        text = text.replace(char, replacement)
    return text

def remove_punctuation(text):
    return ''.join(char for char in text if char not in string.punctuation)

def determine_most_frequent_arme(df, keyword_dict):
    def count_keywords(text, keywords):
        count = {key: 0 for key in keywords}
        for keyword in keywords:
            for word in text.split():
                for keyword_value in keyword_dict[keyword]:
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
                    if any(keyword_value in word for keyword_value in keyword_dict[key]):
                        last_key = key
            return last_key

    # Unlist the 'affectation' column and join the elements as a single string
    df['affectation'] = df['affectation'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x)

    # Convert the text to lowercase, remove accented characters, and remove punctuation
    df['affectation'] = df['affectation'].apply(lambda x: remove_punctuation(remove_accented_characters(x.lower())))

    # Define a function to count keywords for each row and return the most frequent one
    df['arme'] = df['affectation'].apply(lambda x: count_keywords(x, keyword_dict))

    return df

def determine_extracted_decision(df, decision_dict):
    def count_keywords(text, keywords):
        count = {key: 0 for key in keywords}
        for keyword in keywords:
            for word in text.split():
                for keyword_value in decision_dict[keyword]:
                    if keyword_value in word:
                        count[keyword] += 1
        max_count = max(count.values())
        if max_count == 0 and 'bon' in text.split():
            return 'Bon pour le service armé'
        if max_count == 0 or not text.strip():
            return None
        max_keys = [key for key, value in count.items() if value == max_count]
        if len(max_keys) == 1:
            return max_keys[0]
        else:
            last_key = None
            for word in text.split():
                for key in max_keys:
                    if any(keyword_value in word for keyword_value in decision_dict[key]):
                        last_key = key
            return last_key

    # Unlist the 'decision' column and join the elements as a single string
    df['decision'] = df['decision'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x)

    # Convert the text to lowercase, remove accented characters, and remove punctuation
    df['decision'] = df['decision'].apply(lambda x: remove_punctuation(remove_accented_characters(x.lower())))

    # Define a function to count keywords for each row and return the most frequent one
    df['extracted_decision'] = df['decision'].apply(lambda x: count_keywords(x, decision_dict))

    return df

def search_certificat_de_bonne_conduite(df):
    df['details_cleaned'] = df['details'].apply(lambda x: remove_punctuation(remove_accented_characters(x.lower())) if x else None)
    
    def find_certificat_conduite(text):
        words_to_find = ["certificat", "bonne", "conduite"]
        found_words = [word for word in words_to_find if re.search(r'[^\w\s]'.format(word), text)]
        if "conduite" in found_words and len(found_words) > 1:
            accorded_words = ["a reçu", "a recu", "accordé", "accorde", "Accorde", "Accordé"]
            refused_words = ["refuse", "refusé", "n'a pas", "n a pas", "Refusé", "Refuse"]
            
            for word in text.split():
                word_stripped = re.sub(r'[^\w\s]', '', word)
                if any(word_stripped.startswith(acc_word) for acc_word in accorded_words):
                    return "Accordé"
                elif word_stripped in refused_words:
                    return "Refusé"
        return None
    
    df['certificat'] = df['details_cleaned'].apply(lambda x: find_certificat_conduite(x) if x else None)
    df.drop(columns=['details_cleaned'], inplace=True)

    return df

def search_military_grade(df, grade_dico):
    df['details_cleaned'] = df['details'].apply(lambda x: remove_punctuation(remove_accented_characters(x.lower())) if x else None)

    def find_military_grade(text):
        max_grade = 0
        for grade, (terms, required) in grade_dico.items():
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

    df['grade'] = df['details_cleaned'].apply(lambda x: find_military_grade(x) if x else None)
    df.drop(columns=['details_cleaned'], inplace=True)

    # Define a dictionary to rename the values in the 'grade' column
    grade_norme_dico = {
        1: "2e classe",
        2: "1er classe",
        3: "caporal",
        4: "caporal-chef",
        5: "sergent",
        6: "sergent-fourier",
        7: "adjudant",
        8: "adjudant-chef",
        9: "aspirant",
        10: "sous-lieutenant",
        11: "lieutenant",
        12: "capitaine",
        13: "commandant",
        14: "colonel"
    }

    df['grade'] = df['grade'].map(grade_norme_dico)

    return df