# Import the RapidFuzz module and the desired function(s)
from rapidfuzz import fuzz

# Define a function to compute the similarity score
def similarity_score_cython(bytes s1, bytes s2):
    # Call the RapidFuzz function to compute the similarity ratio
    return fuzz.ratio(s1.decode(), s2.decode())
