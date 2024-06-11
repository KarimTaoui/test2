from flask import Flask, request, jsonify
from flask_cors import CORS
from fuzzywuzzy import fuzz, process
import re
import time

app = Flask(__name__)
CORS(app)

# Dictionnaire pour mapper les noms de comptes aux numéros
account_data = {
    "Capital émis (capital social ou fonds de dotation, ou fonds d’exploitation)": "101",
    "Primes liées au capital social": "103",
    "Ecart d’évaluation": "104",
    "Ecart de réévaluation": "105",
    "Réserves (légale, statutaire, ordinaire, réglementée)": "106",
    "Ecart d'équivalence": "107",
    "Compte de l'exploitant": "108",
    "Capital souscrit non appelé": "109",
    "Capital réserves et assimilés":"10",
    "Report à nouveau": "11",
    "Résultat de l'exercice": "12",
    "Subventions d’équipement": "131",
    "Autres subventions d’investissements": "132",
    "Impôts différés actif": "133",
    "Impôts différés passif": "134",
    "Autres produits et charges différés": "138",
    "Provisions pour pensions et obligations similaires": "153",
    "Provisions pour impôts": "155",
    "Provisions pour renouvellement des immobilisations (concession)": "156",
    "Autres provisions pour charges - passifs non courants": "158",
    "Titres participatifs": "161",
    "Emprunts obligataires convertibles": "162",
    "Autres emprunts obligataires": "163",
    "Emprunts auprès des établissements de crédit": "164",
    "Dépôts et cautionnements reçus": "165",
    "Dettes sur contrat de location-financement": "167",
    "Autres emprunts et dettes assimilés": "168",
    "Primes de remboursement des obligations": "169",
    "Dettes rattachées à des participations groupe": "171",
    "Dettes rattachées à des participations hors groupe": "172",
    "Dettes rattachées à des sociétés en participation": "173",
    "Autres dettes rattachées à des participations": "178",
    "Comptes de liaison entre établissements": "181",
    "Comptes de liaison entre sociétés en participation": "188",
    "Frais de développement immobilisable": "203",
    "Logiciels informatiques et assimilés": "204",
    "Concessions et droits similaires, brevets, licences, marques": "205",
    "Ecart d’acquisition": "207",
    "Autres immobilisations incorporelles": "208",
    "Terrains": "211",
    "Agencements et aménagements de terrain": "212",
    "Constructions": "213",
    "Installations techniques, matériel et outillage industriels": "215",
    "Autres immobilisations corporelles": "218",
    "Terrains en concession": "221",
    "Agencements et aménagements de terrain en concession": "222",
    "Constructions en concession": "223",
    "Installations techniques en concession": "225",
    "Autres immobilisations corporelles en concession": "228",
    "Droits du concédant": "229",
    "Immobilisations corporelles en cours": "232",
    "Immobilisations incorporelles en cours": "237",
    "Avances et acomptes versés sur commandes d'immobilisations": "238",
    "Titres de filiales": "261",
    "Autres titres de participation": "262",
    "Titres de participation évalués par équivalence (entreprises associées)": "265",
    "Créances rattachées à des participations groupe": "266",
    "Créances rattachées à des participations hors groupe": "267",
    "Créances rattachées à des sociétés en participation": "268",
    "Versements restant à effectuer sur titres de participation non libérés": "269",
    "Titres immobilisés autres que les titres immobilisés de l'activité de portefeuille": "271",
    "Titres représentatifs de droit de créance (obligations, bons)": "272",
    "Titres immobilisés de l'activité de portefeuille": "273",
    "Prêts et créances sur contrat de location-financement": "274",
    "Dépôts et cautionnements versés": "275",
    "Autres créances immobilisées": "276",
    "Versements restant à effectuer sur titres immobilisés non libérés": "279",
    "Amortissement des frais de recherche et développement immobilisables": "2803",
    "Amortissement des logiciels informatiques et assimilés": "2804",
    "Amortissement concessions & droits similaires, brevets, licences, marques": "2805",
    "Amortissement écart d’acquisition (good will)": "2807",
    "Amortissement autres immobilisations incorporelles": "2808",
    "Amortissement agencements et aménagements de terrain": "2812",
    "Amortissement constructions": "2813",
    "Amortissement installations techniques": "2815",
    "Amortissement autres immobilisations corporelles": "2818",
    "Pertes de valeur sur frais de recherche et développement immobilisables": "2903",
    "Pertes de valeur sur logiciels informatiques et assimilés": "2904",
    "Pertes de valeur sur concessions et droits similaires, brevets, licences, marques": "2905",
    "Pertes de valeur sur écart d’acquisition": "2907",
    "Pertes de valeur sur autres immobilisations incorporelles": "2908",
    "Pertes de valeur sur immobilisations corporelles": "291",
    "Pertes de valeur sur agencements et aménagements de terrain": "2912",
    "Pertes de valeur sur constructions": "2913",
    "Pertes de valeur sur Installations techniques": "2915",
    "Pertes de valeur sur autres immobilisations corporelles": "2918",
    "Pertes de valeur sur immobilisations mises en concession": "292",
    "Pertes de valeur sur immobilisations en cours": "293",
    "Pertes de valeur sur participations et créances rattachées à participations": "296",
    "Pertes de valeur sur autres titres immobilisés": "297",
    "Pertes de valeur sur autres actifs financiers immobilisés": "298",
    "Stocks de marchandises": "30",
    "Matières premières et fournitures": "31",
    "Autres approvisionnements": "32",
    "Matières consommables": "321",
    "Fournitures consommables": "322",
    "Emballages": "326",
    "En cours de production de biens": "33",
    "Produits en cours": "331",
    "Travaux en cours": "335",
    "En cours de production de services": "34",
    "Etudes en cours": "341",
    "Prestations de services en cours": "345",
    "Stocks de produits": "35",
    "Produits intermédiaires": "351",
    "Produits finis": "355",
    "Produits résiduels ou matières de récupération (déchets, rebuts)": "358",
    "Stocks provenant d’immobilisations": "36",
    "Stocks à l'extérieur (en cours de route, en dépôt ou en consignation)": "37",
    "Achats stockés": "38",
    "Marchandises stockées": "380",
    "Matières premières et fournitures stockées": "381",
    "Autres approvisionnements stockés": "382",
    "Pertes de valeur sur stocks et en cours": "39",
    "Pertes de valeur sur Stocks de marchandises": "390",
    "Pertes de valeur sur Matières premières et fournitures": "391",
    "Pertes de valeur sur Autres approvisionnements": "392",
    "Pertes de valeur sur En cours de production de biens": "393",
    "Pertes de valeur sur En cours de production de services": "394",
    "Pertes de valeur sur stocks de produits": "395",
    "Pertes de valeur sur Stocks à l'extérieur": "397",
    "Fournisseurs et comptes rattachés": "40",
    "Fournisseurs de stocks et services": "401",
    "Fournisseurs effets à payer": "403",
    "Fournisseurs d'immobilisations": "404",
    "Fournisseurs d'immobilisations effets à payer": "405",
    "Fournisseurs factures non parvenues": "408",
    "Fournisseurs débiteurs : avances et acomptes versés, RRR à obtenir, autres créances":"409",
    "Clients et comptes rattachés": "41",
    "Clients": "411",
    "Clients, effets à recevoir": "413",
    "Clients douteux": "416",
    "Créances sur travaux ou prestations en cours": "417",
    "Clients - produits non encore facturés": "418",
    "Clients créditeurs - avances reçues, RRR à accorder et autres avoirs à établir": "419",
    "Personnel et comptes rattachés": "42",
    "Personnel, rémunérations dues": "421",
    "Fonds des oeuvres sociales": "422",
    "Participation des salariés au résultat": "423",
    "Personnel, avances et acomptes accordés": "425",
    "Personnel, dépôts reçus": "426",
    "Personnel, oppositions sur salaires": "427",
    "Personnel, charges à payer et produits à recevoir": "428",
    "Organismes sociaux et comptes rattachés": "43",
    "Sécurité sociale": "431",
    "Autres organismes sociaux": "432",
    "Organismes sociaux, charges à payer et produits à recevoir": "438",
    "Etat, collectivités publiques, organismes internationaux et comptes rattachés": "44",
    "Etat et autres collectivités publiques, subventions à recevoir": "441",
    "Etat, impôts et taxes recouvrables sur des tiers": "442",
    "Opérations particulières avec l'Etat et les collectivités publiques": "443",
    "Etat, impôts sur les résultats": "444",
    "Etat, taxes sur le chiffre d'affaires": "445",
    "Organismes internationaux": "446",
    "Autres impôts, taxes et versements assimilés": "447",
    "Etat, charges à payer et produits à recevoir (hors impôts)": "448",
    "Groupe et Associés": "45",
    "Opérations Groupe": "451",
    "Associés , comptes courants": "455",
    "Associés, opérations sur le capital": "456",
    "Associés, dividendes à payer": "457",
    "Associés, opérations faites en commun ou en groupement": "458",
    "Débiteurs divers et créditeurs divers": "46",
    "Créances sur cessions d'immobilisations": "462",
    "Dettes sur acquisitions valeurs mobilières de placement & Instruments financiers dérivés": "464",
    "Créances sur cessions valeurs mobilières de placement & Instruments financiers dérivés": "465",
    "Autres comptes débiteurs ou créditeurs": "467",
    "Diverses charges à payer et produits à recevoir": "468",
    "Comptes transitoires ou d'attente": "47",
    "Charges ou produits constatés d'avance et provisions": "48",
    "Provisions - passifs courants": "481",
    "Charges constatées d'avance": "486",
    "Produits constatés d'avance": "487",
    "Pertes de valeur sur comptes de tiers": "49",
    "Pertes de valeur sur comptes de clients": "491",
    "Pertes de valeur sur comptes du groupe et sur associés": "495",
    "Pertes de valeur sur comptes de débiteurs divers": "496",
    "Pertes de valeur sur autres comptes de tiers": "498",
    "Valeurs mobilières de placement": "50",
    "Part dans des entreprises liées": "501",
    "Actions propres": "502",
    "Autres actions ou titres conférant un droit de propriété": "503",
    "Obligations, bons du trésor et bons de caisse à court terme": "506",
    "Autres valeurs mobilières de placement et créances assimilées": "508",
    "Versements restant à effectuer sur valeurs mobilières de placement non libérées": "509",
    "Banque, établissements financiers et assimilés": "51",
    "Valeurs à l'encaissement": "511",
    "Banques comptes courants": "512",
    "Trésor public et établissements publics": "515",
    "Autres organismes financiers": "517",
    "Intérêts courus": "518",
    "Concours bancaires courants": "519",
    "Instruments financiers dérivés": "52",
    "Caisse": "53",
    "Régies d'avances et accréditifs": "54",
    "Régies d’avances": "541",
    "Accréditifs": "542",
    "Virements internes": "58",
    "Virements de fonds": "581",
    "Autres virements internes": "588",
    "Pertes de valeur sur actifs financiers courants": "59",
    "Pertes de valeur sur valeurs en banque et Etablissements financiers": "591",
    "Pertes de valeurs sur régies d'avances et accréditifs": "594",
    "Achats consommés": "60",
    "Achats de marchandises vendues": "600",
    "Matières premières": "601",
    "Autres approvisionnements": "602",
    "Variations des stocks": "603",
    "Achats d'études et de prestations de services": "604",
    "Achats de matériels, équipements et travaux": "605",
    "Achats non stockés de matières et fournitures": "607",
    "Frais accessoires d'achat": "608",
    "Rabais, remises, ristournes obtenus sur achats": "609",
    "Services extérieurs": "61",
    "Sous-traitance générale": "611",
    "Locations": "613",
    "Charges locatives et charges de copropriété": "614",
    "Entretien, réparations et maintenance": "615",
    "Primes d'assurances": "616",
    "Etudes et recherches": "617",
    "Documentation et divers": "618",
    "Rabais, remises, ristournes obtenus sur services extérieurs": "619",
    "Autres services extérieurs": "62",
    "Personnel extérieur à l'entreprise": "621",
    "Rémunérations d'intermédiaires et honoraires": "622",
    "Publicité, publication, relations publiques": "623",
    "Transports de biens et transport collectif du personnel": "624",
    "Déplacements, missions et réceptions": "625",
    "Frais postaux et de télécommunications": "626",
    "Services bancaires et assimilés": "627",
    "Cotisations et divers": "628",
    "Rabais, remises, ristournes obtenus sur autres services extérieurs": "629",
    "Charges de personnel": "63",
    "Rémunérations du personnel": "631",
    "Rémunérations de l'exploitant individuel": "634",
    "Cotisations aux organismes sociaux": "635",
    "Charges sociales de l'exploitant individuel": "636",
    "Autres charges sociales": "637",
    "Autres charges de personnel": "638",
    "Impôts, taxes et versements assimilés": "64",
    "Impôts, taxes et versements assimilés sur rémunérations": "641",
    "Impôts et taxes non récupérables sur chiffre d’affaires": "642",
    "Autres impôts et taxes (hors impôts sur les résultats)": "645",
    "Autres charges opérationnelles": "65",
    "Redevances pour concessions, brevets, licences, logiciels, droits et valeurs similaires": "651",
    "Moins values sur sortie d'actifs immobilisés non financiers": "652",
    "Jetons de présence": "653",
    "Pertes sur créances irrécouvrables": "654",
    "Quote-part de résultat sur opérations faites en commun": "655",
    "Amendes et pénalités, subventions accordés, dons et libéralités": "656",
    "Charges exceptionnelles de gestion courante": "657",
    "Autres charges de gestion courante": "658",
    "Charges financières": "66",
    "Charges d'intérêts": "661",
    "Pertes sur créances liées à des participations": "664",
    "Ecart d’évaluation sur actifs financiers - Moins-values": "665",
    "Pertes de change": "666",
    "Pertes nettes sur cessions d’actifs financiers": "667",
    "Autres charges financières": "668",
    "Eléments extraordinaires- charges": "67",
    "Dotations aux amortissements, provisions et pertes de valeur": "68",
    "Dotations aux amortissements, prov. et pertes de valeur - actifs non courants": "681",
    "Dotations aux amortissements, prov. et pertes de valeur des biens mis concession": "682",
    "Dotations aux amortissements, provisions et pertes de valeur - actifs courants": "685",
    "Dotations aux amortissements, provisions et pertes de valeur- éléments financiers": "686",
    "Impôts sur les résultats et assimilés": "69",
    "Imposition différée actif": "692",
    "Imposition différée passif": "693",
    "Impôts sur les bénéfices basés sur le résultat des activités ordinaires": "695",
    "Autres impôts sur les résultats": "698",
    "Ventes de marchandises et de produits fabriqués, ventes de prestations service et produits  annexes": "70",
    "Ventes de marchandises": "700",
    "Ventes de produits finis": "701",
    "Ventes de produits intermédiaires": "702",
    "Ventes de produits résiduels": "703",
    "Vente de travaux": "704",
    "Vente d'études": "705",
    "Autres prestations de services": "706",
    "Produits des activités annexes": "708",
    "Rabais, remises et ristournes accordés": "709",
    "Production stockée ou déstockée": "72",
    "Variation de stocks d'encours": "723",
    "Variation de stocks de produits": "724",
    "Production immobilisée": "73",
    "Production immobilisée d'actifs incorporels": "731",
    "Production immobilisée d'actifs corporels": "732",
    "Subventions d’exploitation": "74",
    "Subvention d'équilibre": "741",
    "Autres subventions d'exploitation": "748",
    "Autres produits opérationnels": "75",
    "Redevances pour concessions, brevets, licences, logiciels et valeurs similaires": "751",
    "Plus values sur sorties d’actifs immobilisés non financiers": "752",
    "Jetons de présence et rémunérations d'administrateurs ou de gérants": "753",
    "Quotes-parts de subventions d’investissement virées au résultat de l’exercice": "754",
    "Quote-part de résultat sur opérations faites en commun": "755",
    "Rentrées sur créances amorties": "756",
    "Produits exceptionnels sur opérations de gestion": "757",
    "Autres produits de gestion courante": "758",
    "Produits financiers": "76",
    "Produits des participations": "761",
    "Revenus des actifs financiers": "762",
    "Revenus de créances": "763",
    "Ecart d’évaluation sur actifs financiers - Plus-values": "765",
    "Gains de change": "766",
    "Profits nets sur cessions d’actifs financiers": "767",
    "Autres produits financiers": "768",
    "Eléments extraordinaires (Produits)": "77",
    "Reprises sur pertes de valeur et provisions": "78",
    "Reprises d'exploitation sur pertes de valeur et provisions - actifs non courants": "781",
    "Reprises d'exploitation sur pertes de valeur et provisions - actifs courants": "785",
    "Reprises financières sur pertes de valeur et provisions": "786"
   
    }


# Inverser le dictionnaire pour mapper les numéros de compte aux noms
number_to_account = {v: k for k, v in account_data.items()}

# Liste des noms de comptes
account_names = list(account_data.keys())

# Mots superflus à ignorer
ignore_words = {"s'il", "vous", "plait", "donne", "moi", "le", "la", "les", "un", "une", "des", "de", "du", "numéro", "de", "compte", "à", "l'", "d'", "c'est", "quoi"}

# Variable de session pour garder une trace de l'état de la conversation
session_state = {
    'step': None,
    'length': None,
    'width': None,
    'height': None
}

def search_by_account_number(user_input):
    account_number_match = re.search(r'\b\d{3}\b', user_input)
    if account_number_match:
        account_number = account_number_match.group()
        account_name = number_to_account.get(account_number)
        if account_name:
            return f"Le compte numéro '{account_number}' correspond à : {account_name}"
        else:
            return "Compte non trouvé"
    else:
        return "Je suis désolé, je n'ai pas compris votre question. Pouvez-vous reformuler, s'il vous plaît "

def search_by_account_name(user_input):
    account_name, account_number = get_account_info(user_input)
    if account_number:
        return f"Le numéro du compte '{account_name}' est : {account_number}"
    else:
        return "Pouvez-vous clarifier votre demande ?"

def get_account_info(user_input):
    cleaned_input = clean_input(user_input)
    best_match, score = get_account_by_name(cleaned_input)
    if best_match:
        return best_match, account_data[best_match]
    else:
        return "je n'ai pas compris", None

def get_account_by_name(account_name):
    best_match, score = process.extractOne(account_name, account_names, scorer=fuzz.token_set_ratio)
    threshold = 90  # Abaisser le seuil pour plus de flexibilité
    if score >= threshold:
        return best_match, score
    else:
        return None, None

def clean_input(user_input):
    words = re.split(r'\W+', user_input)
    cleaned_words = [word for word in words if word.lower() not in ignore_words]
    return " ".join(cleaned_words)

def calculate_debit(length, width, height):
    try:
        length = float(length)
        width = float(width)
        height = float(height)
        return length * width * height
    except ValueError:
        return None

def detect_calcul_debit_intent(user_input):
    expected_expression = "calcul de débit"
    similarity_ratio = fuzz.partial_ratio(user_input, expected_expression)
    return similarity_ratio >= 80  # Exemple de seuil de similarité

def detect_greeting_intent(user_input):
    greetings = ["bonjour", "salut", "bonsoir", "coucou", "hello", "hi", "cv", "ça va", "comment ça va","bien","labess","hmd","ghya","lhamdoulileh","super"]
    for greeting in greetings:
        if fuzz.partial_ratio(user_input, greeting) >= 80:
            return True
    return False

def respond_to_greeting(user_input):
    if "bonjour" in user_input or "bonsoir" in user_input:
        return "Bonjour! Comment puis-je vous aider aujourd'hui?"
    elif "salut" in user_input or "coucou" in user_input:
        return "Salut! Comment puis-je vous aider aujourd'hui?"
    elif "hello" in user_input:
        return "Hello! How can I assist you today?"
    elif "cv" in user_input or "ça va" in user_input or "comment ça va" in user_input:
        return "Je vais bien, merci! Et vous?"
    else:
        return "Bien! Comment puis-je vous aider aujourd'hui?"

def detect_thanks_intent(user_input):
    thanks_keywords = ["merci", "thanks", "thank you", "thx", "merci beaucoup"]
    for thanks in thanks_keywords:
        if fuzz.partial_ratio(user_input, thanks) >= 80:
            return True
    return False

def respond_to_thanks(user_input):
    return "Avec plaisir ! Si vous avez d'autres questions, n'hésitez pas."

@app.route('/chatbot', methods=['POST'])
def chatbot():
    global session_state

    data = request.json
    user_input = data.get('message', '').lower().strip()  # Normalize input

    if detect_greeting_intent(user_input):
        response_text = respond_to_greeting(user_input)
    elif detect_thanks_intent(user_input):
        response_text = respond_to_thanks(user_input)
    elif detect_calcul_debit_intent(user_input):
        session_state = {
            'step': 'length',
            'length': None,
            'width': None,
            'height': None
        }
        response_text = 'Quelle est la longueur?'
    elif session_state['step'] == 'length':
        session_state['length'] = user_input
        session_state['step'] = 'width'
        response_text = 'Quelle est la largeur?'
    elif session_state['step'] == 'width':
        session_state['width'] = user_input
        session_state['step'] = 'height'
        response_text = 'Quelle est la hauteur?'
    elif session_state['step'] == 'height':
        session_state['height'] = user_input
        session_state['step'] = None
        length = session_state['length']
        width = session_state['width']
        height = session_state['height']
        debit = calculate_debit(length, width, height)
        if debit is not None:
            response_text = f'Le débit est de {debit} mètres cubes.'
        else:
            response_text = 'Les valeurs fournies ne sont pas valides. Veuillez entrer des nombres valides.'
    elif re.search(r'\b\d{3}\b', user_input):
        response_text = search_by_account_number(user_input)
    else:
        response_text = search_by_account_name(user_input)
    
    if user_input.isdigit():
        account_number = user_input
        account_name = number_to_account.get(account_number)
        if account_name:
            response_text = f"Si vous voulez dire le compte numéro {user_input} , {search_by_account_number(user_input)}"
        else:
            response_text = f"Le numéro {user_input} ne correspond à aucun compte."

    time.sleep(2)

    return jsonify({'response': [{'text': response_text}]})



if __name__ == "__main__":
    app.run(debug=True)
