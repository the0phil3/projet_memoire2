# Statistical treament of "registre matricules" from the French departement of the Seine (1887 - 1921)

Here is the repositiory for the processing and analysis of my database of 8000 soldiers from the Seine department during the Great War.

My processing rests on the work of my bash shell found [here](https://github.com/the0phil3/matricule_htr).

This repository is structured as such:
- data/primary/ contains the primary csvs used for the creation of figures and the anlaysis of my database
- data/secondary/ contains the secondary csvs used in the first part of my dissertation
- prelimwork/ contains the code used throughout the research process
- build/ contains the cython implementation of the levenshtein distance function from RapidFuzz

The code in the main directory is all the code used for this dissertation:
1. base_matching: contains the code matching the MPF database with our sample
2. cleaning_const: contains all the constants used form RapidFuzz corpus cleaning
3. column_cleaning: contains the functions for RapidFuzz corpus cleaning
4. db_creation: contains the code used for cleaning and combining the raw data into one useable spreadsheet
5. extract_const: contains the constants used in some of the extraction functions
6. funcs: contains the functions used during the extraction of information from the raw data
7. mpf_creation: contains the code used to get all the individuals from the Seine recrutement office in the MPF database
8. mpf_funcs: contains the functions used during base_matching and mpf_creation
9. primary_extraction: contains all the code creating a final database full of information
10. primary_figures: contains all the code from the primary_extraction used for making the figures and graphs from my database
11. scraping_division: contains the first code used to split the jpegs of individual fiches matricules into different subgroups so that they could transcribed on different computers
12. secondary_figures: contains the code used to create the graphs and figures from the secondary literature
13. setup: contains the implentation of the levenshtein distance function from RapidFuzz in cython
14. similarity_cython: levenshtein distance function from RapidFuzz in cython


In the data/primary/ folder:
- big_bertha is the complete raw data for 8000 individuals from the Seine
- final_df is the processed data for these individuals
- mpf_seine is the data for matched individuals coming from the Seine sample and the MPF database
