#This python file contains all the different constants necessary for text extraction

DECISION = {
    "Bon pour le service armé": ["arme", "armé", 'Bon', "Propre", 'propre'],
    "Exempté" : ["dispense", "exempte", "dispensé", "exempté", "dipensé", "dipense"],
    "Ajourné" : ["ajourne", "ajourné", "sejourne", "sejourné", "différé", 'differé'],
    "Bon absent" : ["absent"],
    "Bon pour le service auxiliaire" : ["auxil", "auxiliaire", "faible", 'faiblesse'],
    "Engagé volontaire" : ["engage", "volontaire", "engagé"]
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
    "Infanterie": ["infa", "chasseurs a pied", "chasseur a pied", " ri ", "infanterie",
                   "infie", "infi", "infe", "ifie", "interie"],
    "Troupes coloniales" : ["tirail", "goum", "afrique", "spahis", "coloniaux",
                            "zouaves", "etranger", "tirailleurs", "colo", "d'af"],
    "Aviation" : ["avia", "aero"],
	'Armée de la mer' : ['marine', 'navale', 'flotte', 'equipages'],
    "Train" : ["train", "auto"],
    "Genie" : ["genie"],
    "Cavalerie" : ["dragons", "cuirassiers", "chasseurs", "hussard", "huss", "chasseurs a cheval",
                   "chas a cheval", "chasseur a cheval", "drag"],
    "Artillerie" : ["art", "ouvriers dart", "ouv art", "ouv d art",
                    "boa", "alc", "r a ", "dartillerie" , "legere portee"],
    "Corps medical" : ["infirmier", 'santé', 'infiriniers', "d'infirère", "d'infirimiers"],
    "Service auxiliaire" : ["aux", "etat major", "coa", "sem", "em" ],
    "Affectations spéciales" : ["special", "usine"]
}

grade_norme_dico = {
        1: "2e classe",
        2: "1er classe",
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
