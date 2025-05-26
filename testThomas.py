from ortools.sat.python import cp_model


model = cp_model.CpModel()

def load_my_format(filename):
    data = {
        'horizon': None,
        'shifts': {},             # ID -> { 'length': int }
        'staff': {},              # ID -> { 'max_shifts': int, 'max_total': int, 'min_total': int, 'max_cseq': int, 'min_cseq': int, 'min_rest': int, 'max_wend': int }
        'days_off': {},           # EmployeeID -> list de jours
        'shift_on_requests': [],  # list de dicts
        'shift_off_requests': [],
        'cover': []
    }

    section = None
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Ignorer les commentaires ou lignes vides
            if line.startswith('#') or not line:
                continue

            # Détecter la section
            if line.startswith('SECTION_'):
                section = line
                continue

            # Traitement selon la section
            if section == 'SECTION_HORIZON':
                data['horizon'] = int(line)
            elif section == 'SECTION_SHIFTS':
                parts = line.split(',')
                shift_id = parts[0]
                length = int(parts[1])
                last = parts[2]
                no_follow = last.split('|') # liste de shifts qui ne peuvent pas suivre
                data['shifts'][shift_id] = {'length': length, 'no_follow': no_follow}
            elif section == 'SECTION_STAFF':
                # Ligne exemple : A,D=14,4320,3360,5,2,2,1
                parts = line.split(',')  # ['A', 'D=14', '4320', '3360', '5', '2', '2', '1']
                emp_id = parts[0]

                valeurs= parts[2:]
                attr_part = parts[1]  # 'D=14'
                # Séparer la partie après le '='
                max_shifts = attr_part.split('|')
                '''
                if len(key_value) != 2:
                    print("Format inattendu dans ligne:", line)
                    continue


                if len(valeurs) != 6:
                    print("Nombre de valeurs inattendu dans ligne:", line)
                    print("il y a", len(valeurs), "éléments :", valeurs)
                    continue
                '''
                #max_shifts = key_value[1]
                max_total_minutes = int(valeurs[0])
                min_total_minutes = int(valeurs[1])
                max_cseq = int(valeurs[2])
                min_cseq = int(valeurs[3])
                min_rest = int(valeurs[4])
                max_wend = int(valeurs[5])

                data['staff'][emp_id] = {
                    'max_shifts': max_shifts,
                    'max_total': max_total_minutes,
                    'min_total': min_total_minutes,
                    'max_cseq': max_cseq,
                    'min_cseq': min_cseq,
                    'min_rest': min_rest,
                    'max_wend': max_wend
                }
            elif section == 'SECTION_DAYS_OFF':
                parts = line.split(',')
                emp_id = parts[0]
                days_off_list = [int(d) for d in parts[1:]]
                data['days_off'][emp_id] = days_off_list
            elif section == 'SECTION_SHIFT_ON_REQUESTS':
                parts = line.split(',')
                emp_id = parts[0]
                day = int(parts[1])
                shift_id = parts[2]
                weight = int(parts[3])
                data['shift_on_requests'].append({'empID': emp_id, 'day': day, 'shiftID': shift_id, 'weight': weight})
            elif section == 'SECTION_SHIFT_OFF_REQUESTS':
                parts = line.split(',')
                emp_id = parts[0]
                day = int(parts[1])
                shift_id = parts[2]
                weight = int(parts[3])
                data['shift_off_requests'].append({'empID': emp_id, 'day': day, 'shiftID': shift_id, 'weight': weight})
            elif section == 'SECTION_COVER':
                parts = line.split(',')
                day = int(parts[0])
                shiftID = parts[1]
                requirement = int(parts[2])
                weight_under = int(parts[3])
                weight_over = int(parts[4])
                data['cover'].append({'day': day, 'shiftID': shiftID, 'requirement': requirement, 'weight_under': weight_under, 'weight_over': weight_over})
    return data

# initialisation après chargement de data
data = load_my_format('/home/w136736/insa/opti-graphes/Instances/Instance21.txt')
print(data)
# Nombre total de jours dans l'horizon
h = data['horizon']
# Ensemble des jours (commençant à 1)
J = list(range(1, h + 1))

# Ensemble des week-ends (si h=14, W=1,2,...)
W = list(range(1, (h // 7) + 1))

# Ensemble des employés (liste des clés dans 'staff')
E = list(data['staff'].keys())

# Ensemble des types de postes (d'après 'shifts' IDs)
P = list(data['shifts'].keys())

# Dictionnaires pour les paramètres par poste
dp = {}     # durée en minutes
Ip = {}     # ensemble des postes qui ne peuvent pas suivre p
ujp = {}   # le besoin en personnel par jour pour chaque p

for p in P:
    dp[p] = data['shifts'][p]['length']
    # Si 'no_follow' est en place, le récupérer, sinon vide
    Ip[p] = data['shifts'][p].get('no_follow', [])
    # Si vous voulez remplir ujp pour tous j dans J, faire :
    for j in J:
        # Ex: supposer que pour tous j c'est le même besoin, ou si dans data par exemple
        # vous avez un dict, adaptez ici.
        # exemple: ujp[(p,j)] = valeur définie selon votre fichier ou règle
        pass

# Dictionnaires pour les employés, initialisés à partir des données
Re = {}     # jours de repos
tmin_e = {} # tps min total
tmax_e = {} # tps max total
cmin_e = {} # la longueur minimale de posts consécutifs
cmax_e = {} # la longueur maximale
rmin_e = {} # repos consécutifs minimaux
wmax_e = {} # max week-ends travaillé
mmax_ep = {} # max jours par poste p pour chaque employé e

for e in E:
    staff_info = data['staff'][e]
    # Exemple d'extraire chaque paramètre
    tmax_e[e] = staff_info['max_total']
    tmin_e[e] = staff_info['min_total']
    cmax_e[e] = staff_info['max_cseq']
    cmin_e[e] = staff_info['min_cseq']
    rmin_e[e] = staff_info['min_rest']
    wmax_e[e] = staff_info['max_wend']
    # Pour les jours de repos, si dans data['days_off'] e est présent
    Re[e] = data['days_off'].get(e, [])
    # Pour mmax_ep, il faut que dans tes données tu aies cette info
    # Si tu l'as dans `data['mmax_ep']`, l'utiliser directement.
    # Sinon, si tu ne l'as pas, tu peux le fixer par exemple à une valeur par défaut
    # (ex: 14)
    # Exemple :
    # mmax_ep[(e,p)] = valeur
    # Si pas dans data, tu peux faire :
    # mmax_ep[(e,p)] = valeur_par_defaut


### DEFINITION DES VARIABLES DE DECISION

# Variables d'affectation : employé e, jour j, poste p
x_ejp = {}
for e in E:
    for j in J:
        for p in P:
            x_ejp[(e, j, p)] = model.NewBoolVar(f"x_{e}_{j}_{p}")

# Variables pour week-ends (si besoin)
wmax = max(W)
w_end = {}
for e in E:
    for w in W:
        w_end[(e, w)] = model.NewBoolVar(f"w_{e}_{w}")

# Variables pour écarts de personnel
y_missing = {}
y_excess = {}
for p in P:
    for j in J:
        y_missing[(p, j)] = model.NewIntVar(0, 10000, f"miss_{p}_{j}")
        y_excess[(p, j)] = model.NewIntVar(0, 10000, f"excess_{p}_{j}")



