from mip import Model, BINARY, xsum


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
data = load_my_format('/home/w136736/insa/opti-graphes/Instances/Instance2.txt')
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

m = Model()
# Variables : e, d, p
x = {}
for e in E:
    for d in J:
        for p in P:
            x[(e, d, p)] = m.add_var(var_type=BINARY)

# Variables d'affectation : employé e, jour j, poste p

# Variables pour week-ends (si besoin)


# Variables pour écarts de personnel


#Pour la contrainte 1 OK
for e in E:
    for d in J:
        m += xsum(x[(e, d, p)] for p in P) <= 1

#Pour la contrainte 2
for e in E:
    for d in J[:-1]:  # jusqu'à l’avant-dernier jour
        for p in P:
            if Ip.get(p, [])!='':
                for p2 in Ip.get(p, []):
                    if p2!='':
                        m += x[(e, d, p)] + x[(e, d+1, p2)] <= 1
#Pour la contrainte 3 OK
for e in E:
    for p in P:
        m += xsum(x[(e, d, p)] for d in J) <= mmax_ep.get((e,p), len(J))
#Pour la contrainte 4 OK
# Dictionnaire des durées
shift = {}
for p in P:
    shift[p] = data['shifts'][p]
for e in E:
    total_time = xsum(x[(e, d, p)] * shift[p]['length'] for d in J for p in P)
    m += total_time >= tmin_e[e]
    m += total_time <= tmax_e[e]
#Pour la contrainte 5
for e in E:
    for d in J[:-cmax_e[e]+1]:  # pour toutes les fenêtres
        m += xsum(x[(e, day, p)] for day in range(d, d + cmax_e[e]) for p in P) <= cmax_e[e]
#Pour la contrainte 6
# La série de jours travaillés suivants doit faire au moins cmin_e[e]
for e in E:
    for d in J[:-cmin_e[e]+1]:
        m += xsum(x[(e, day, p)] for day in range(d, d + cmin_e[e]) for p in P) >= cmin_e[e]
#Pour la contrainte 7
for e in E:
    for d in J[:-rmin_e[e]+1]:
        m += xsum(1 - sum(x[(e, day, p)] for p in P) for day in range(d, d + rmin_e[e])) >= rmin_e[e]
#Pour la contrainte 8

W = range(1, (len(J) // 7) + 1)

for e in E:
    for w in W:
        samedi = (w-1)*7 + 5
        dimanche = (w-1)*7 + 6

        # Variable binaire qui indique si l'employé a travaillé un week-end w
        travaille_wend = m.add_var(var_type=BINARY, name=f"w_{e}_{w}")

        # Si l’employé a travaillé dans ce week-end (samedi ou dimanche)
        # alors il faut que `travaille_wend` = 1 : donc sum >= 1 => travaille_wend=1
        m += (xsum(x[(e, samedi, p)] for p in P) + xsum(x[(e, dimanche, p)] for p in P)) >= travaille_wend

        # Limitation : le nombre de week-ends ne doit pas dépasser wmax_e[e]
        m += travaille_wend <= wmax_e[e]
#Pour la contrainte 9
'''for e in E:
    for d in data['days_off'].get(e, []):
        for p in P:
            m += x[(e, d, p)] == 0'''
#Pour la contrainte 10

def contraint1(solver, x, E, J, P):
    """
    Vérifie que pour chaque employé e et jour j, il y a au plus une affectation (un seul poste).
    Retourne True si la contrainte est respectée dans la solution, False sinon.
    """
    for e in E:
        for d in J:
            affectations = [solver.Value(x[(e, d, p)]) for p in P]
            somme_affects = sum(affectations)
            if somme_affects > 1:
                print(f"Violation : Employé {e} le jour {d+1} a {somme_affects} affectations.")
                return False
    return True


def constraint2(solver, x, E, J, P, Ip):
    """
    Vérifie que dans la solution, pour chaque employé e,
    le poste p à jour d, et le poste p' interdit à suivre,
    si on travaille p à d, alors on ne travaille pas p' à d+1.
    Retourne True si la contrainte est respectée, sinon False.
    """
    for e in E:
        for d in J[:-1]:  # jusqu'à penultième jour pour d+1
            d_next = d + 1
            for p in P:
                if solver.Value(x[(e, d, p)]) == 1:
                    # si ce poste p est travaillé ce jour-là
                    for p_prime in Ip.get(p, []):
                        # alors, p' ne doit pas être travaillé le lendemain
                        if solver.Value(x[(e, d_next, p_prime)]) == 1:
                            print(f"Violation : Employé {e} travaille {p} le jour {d+1} et {p_prime} le jour {d+2}")
                            return False
    return True

def constraint3(solver, x, E, J, P, mmax_e_p):
    """
    Vérifie qu’un employé e n’est pas affecté plus que mmax_e_p fois au poste p dans la solution.
    Retourne True si respecté, sinon False.
    """
    for e in E:
        for p in P:
            count = 0
            for d in J:
                if solver.Value(x[(e, d, p)]) == 1:
                    count += 1
            if count > mmax_e_p.get((e, p), float('inf')):
                print(f"Violation : Employé {e} est affecté {count} fois au poste {p} (limite {mmax_e_p.get((e,p), 'inf')})")
                return False
    return True

def constraint4(solver, x, E, J, P, shift_types, tmin_e, tmax_e):
    """
    Vérifie que pour chaque employé, la durée totale de travail est dans [tmin_e[e], tmax_e[e]].
    Retourne True si respecté, sinon False.
    """
    for e in E:
        total_duree = 0
        for d in J:
            for p in P:
                if solver.Value(x[(e, d, p)]) == 1:
                    total_duree += shift_types[p].duration
        # Vérifier la limite inférieure si définie
        if e in tmin_e and total_duree < tmin_e[e]:
            print(f"Violation : Employé {e} travaille seulement {total_duree} min (< {tmin_e[e]})")
            return False
        # Vérifier la limite supérieure si définie
        if e in tmax_e and total_duree > tmax_e[e]:
            print(f"Violation : Employé {e} travaille {total_duree} min (> {tmax_e[e]})")
            return False
    return True

def constraint5(solver, x, E, J, cmax_e):
    """
    Vérifie que pour chaque employé e, il n'a pas de séquence de jours travaillés (1) > cmax_e[e].
    Retourne True si respecté, sinon False.
    """
    for e in E:
        max_consecutif = 0
        count = 0
        for d in J:
            # Vérifie si e travaille ce jour
            travaille = any(solver.Value(x[(e, d, p)]) == 1 for p in P)
            if travaille:
                count += 1
                if count > max_consecutif:
                    max_consecutif = count
            else:
                count = 0
        # Vérification contre cmax_e
        if e in cmax_e and max_consecutif > cmax_e[e]:
            print(f"Violation : Employé {e} a une séquence de {max_consecutif} jours travaillés consécutifs (> {cmax_e[e]})")
            return False
    return True

def constraint6(solver, x, E, J, cmin_e):
    """
    Vérifie que pour chaque employé e, toute séquence de jours travaillés
    a une longueur >= cmin_e[e].
    Retourne True si respecté, sinon False.
    """
    for e in E:
        count = 0
        for d in J:
            # Vérifie si e travaille ce jour
            travaille = any(solver.Value(x[(e, d, p)]) == 1 for p in P)
            if travaille:
                count += 1
            else:
                # Si on a fini une séquence, on vérifie sa longueur
                if count > 0 and count < cmin_e.get(e, 0):
                    print(f"Violation : Employé {e} a une séquence de {count} jours travaillés (< {cmin_e[e]})")
                    return False
                count = 0
        # Vérification en fin de boucle pour la dernière séquence
        if count > 0 and count < cmin_e.get(e, 0):
            print(f"Violation : Employé {e} a une séquence finale de {count} jours travaillés (< {cmin_e[e]})")
            return False
    return True

def constraint7(solver, x, E, J, rmin_e):
    """
    Vérifie que pour chaque employé e, toute séquence de jours de repos
    a une longueur >= rmin_e[e].
    Retourne True si respecté, sinon False.
    """
    for e in E:
        count = 0
        for d in J:
            # Vérifie si e est en repos ce jour-là
            en_repos = all(solver.Value(x[(e, d, p)]) == 0 for p in P)
            if en_repos:
                count += 1
            else:
                # Si on a fini une séquence, on vérifie sa longueur
                if 0 < count < rmin_e.get(e, 0):
                    print(f"Violation : Employé {e} a une séquence de {count} jours de repos (< {rmin_e[e]})")
                    return False
                count = 0
        # Vérification en fin de boucle pour la dernière séquence
        if 0 < count < rmin_e.get(e, 0):
            print(f"Violation : Employé {e} a une séquence finale de {count} jours de repos (< {rmin_e[e]})")
            return False
    return True

def constraint8(solver, x, E, W, week_end_info, wmax_e):
    """
    Vérifie que pour chaque employé e, le nombre de week-ends travaillés ne dépasse pas wmax_e[e].
    - week_end_info : dict avec clé (e,w) = bool, indique si e a travaillé ce week-end.
    Retourne True si OK, sinon False.
    """
    for e in E:
        count_wend = 0
        for w in W:
            # Définir les jours du week-end w
            samedi = w*7 + 5   # jour 5 dans la semaine (si 0 = lundi)
            dimanche = w*7 + 6 # jour 6
            travail_weekend = False
            if samedi < len(J):
                travail_weekend = travail_weekend or (any(solver.Value(x[(e, samedi, p)]) == 1 for p in P))
            if dimanche < len(J):
                travail_weekend = travail_weekend or (any(solver.Value(x[(e, dimanche, p)]) == 1 for p in P))
            if travail_weekend:
                count_wend += 1
        if count_wend > wmax_e.get(e, float('inf')):
            print(f"Violation : Employé {e} travaille {count_wend} week-ends (> {wmax_e[e]})")
            return False
    return True

def constraint9(solver, x, days_off, E, P):
    """
    Vérifie que pour chaque employé e dans days_off,
    si un jour d est interdit, alors e n’est affecté à aucun poste ce jour-là.
    Retourne True si respecté, sinon False.
    """
    for e in days_off:
        jours_interdits = days_off[e]
        for d in jours_interdits:
            for p in P:
                if solver.Value(x[(e, d, p)]) == 1:
                    print(f"Violation : Employé {e} travaille le jour {d} alors que c’est interdit.")
                    return False
    return True



m.objective = xsum(x[(e, d, p)] * shift[p]['length'] for e in E for d in J for p in P)
status = m.optimize()
if status == 'optimal':
    # boucle pour récupérer et afficher
    for e in E:
        for d in J:
            for p in P:
                if x[(e, d, p)].x >= 0.5:
                    print(f"{e} travaille le jour {d} sur {p}")
def construire_planning(solver, x, E, J, P):
    """
    Construit un planning à partir de la solution, sous forme d'un dict
    ou d'une liste par employé et jour, en respectant toutes les contraintes dures.
    """
    planning = {}
    for e in E:
        planning[e] = []
        for d in J:
            poste_trouve = '-'
            for p in P:
                if solver.Value(x[(e, d, p)]) == 1:
                    poste_trouve = p
                    break
            planning[e].append(poste_trouve)
    return planning

