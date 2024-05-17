import pandas as pd
import numpy as np
import ast
from rapidfuzz.process import extractOne
from rapidfuzz.fuzz import ratio

def decision_column_cleaning(row, CONSTANT):
	if pd.isna(row):
		return row
	word_list = ast.literal_eval(row)
	for i, word in enumerate(word_list):
		if(0 < len(word) <= 4):
			score = extractOne(word, CONSTANT, scorer=ratio, processor=lambda s: s.lower())
			if (score[1] > 66.0):
				print(f"Replaced {word} with {score[0]}")
				word_list[i] =  score[0]
		elif(len(word) > 4):
			score = extractOne(word, CONSTANT, scorer=ratio, processor=lambda s: s.lower())
			if (score[1] >= 88.0):
				print(f"Replaced {word} with {score[0]}")
				word_list[i] =  score[0]

	return (word_list)

def instruction_column_cleaning(row, CONSTANT):
	if pd.isna(row):
		return row
	word_list = ast.literal_eval(row)
	for i, word in enumerate(word_list):
		if(0 < len(word) <= 4):
			score = extractOne(word, CONSTANT, scorer=ratio, processor=lambda s: s.lower())
			if (score[1] > 66.0):
				print(f"Replaced {word} with {score[0]}")
				word_list[i] =  score[0]
		elif(len(word) > 0):
			score = extractOne(word, CONSTANT, scorer=ratio, processor=lambda s: s.lower())
			if (score[1] >= 80.0):
				print(f"Replaced {word} with {score[0]}")
				word_list[i] =  score[0]

	return (word_list)

def column_cleaning(row, CONSTANT):
	if pd.isna(row):
		return row
	word_list = ast.literal_eval(row)
	for i, word in enumerate(word_list):
		if(len(word) > 0):
			score = extractOne(word, CONSTANT, scorer=ratio, processor=lambda s: s.lower())
			if (score[1] >= 88.0):
				print(f"Replaced {word} with {score[0]}")
				word_list[i] =  score[0]

	return (word_list)

