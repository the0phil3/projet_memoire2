#This python file contains all the different constants necessary for text extraction

DECISION = {
    "bon pour le service armé": ["arme", "armé", 'Bon', "Propre", 'propre'],
    "exempté" : ["dispense", "exempte", "dispensé", "exempté", "dipensé", "dipense"],
    "ajourné" : ["ajourne", "ajourné", "sejourne", "sejourné", "différé", 'differé'],
    "bon absent" : ["absent"],
    "bon pour le service auxiliaire" : ["auxil", "auxiliaire", "faible", 'faiblesse'],
    "engagé volontaire" : ["engage", "volontaire", "engagé"]
}

GRADE = {
    1: (["soldat", "sapeur", "hussard", "chasseur", "cycliste", "cavalier", "cuirassier",
         "cuir", "cannonier", 'zouave', 'légionnaire', 'conducteur'], ["2", "classe"]),
    2: (["soldat", "sapeur", "hussard", "chasseur", "cycliste", "cavalier", "cuirassier",
         "cuir", "cannonier", 'zouave', 'légionnaire', 'conducteur'], ["1", "classe"]),
    3: (["caporal", "brigadier"], []),
    4: (["fourier", "fourrier"], []),
    5: (["sergent", "marechal des logis", "logis"], []),
    6: (["adjudant"], []),
    7: (["adjudant chef"], []),
    8: (["aspirant"], []),
    9: (["lieutenant", "lieut"], []),
    10: (["capitaine"], []),
    11: (["chef d'escadron", 'chef de bataillon'], []),
}

AFFECTATION = {
    "infanterie": ["infa", "chasseurs a pied", "chasseur a pied", " ri ", "infanterie",
                   "infie", "infi", "infe", "ifie", "interie"],
    "troupes coloniales" : ["tirail", "goum", "afrique", "spahis", "coloniaux",
                            "zouaves", "etranger", "tirailleurs", "colo", "d'af"],
    "aviation" : ["avia", "aero"],
	'armée de la mer' : ['marine', 'navale', 'flotte', 'equipages'],
    "train" : ["train", "auto"],
    "génie" : ["genie"],
    "cavalerie" : ["dragons", "cuirassiers", "chasseurs", "hussard", "huss", "chasseurs a cheval",
                   "chas a cheval", "chasseur a cheval", "drag"],
    "artillerie" : ["art", "ouvriers dart", "ouv art", "ouv d art",
                    "boa", "alc", "r a ", "dartillerie" , "legere portee"],
    "corps medical" : ["infirmier", 'santé', 'infiriniers', "d'infirère", "d'infirimiers"],
    "service auxiliaire" : ["aux", "etat major", "coa", "sem", "em" ],
    "affectations spéciales" : ["special", "usine"]
}

grade_norme_dico = {
        1: "2e classe",
        2: "1e classe",
        3: "caporal",
        4: "fourrier",
        5: "sergent",
        6: "adjudant",
        7: "adjudant-chef",
        8: "aspirant",
        9: "lieutenant",
        10: "capitaine",
        11: "commandant"
    }
