import sqlite3
import random
from get_pokemons import select_random_pokemons
import json


# Fonction pour récupérer 16 personnages depuis la base de données
def get_characters(db_name, table_name, pokemon_ids):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in pokemon_ids)
    cursor.execute(f'''
        SELECT id, name, height, weight, base_experience, abilities, types, stats FROM {table_name} WHERE id IN ({placeholders})
    ''', pokemon_ids)
    characters = []
    for row in cursor.fetchall():
        character = {
            "id": row[0],
            "name": row[1],
            "height": row[2],
            "weight": row[3],
            "base_experience": row[4],
            "abilities": row[5],
            "types": row[6],
            "stats": row[7]
        }
        characters.append(character)
    conn.close()
    return characters


# Fonction pour analyser les statistiques à partir de la chaîne de texte
def parse_stats(stats_string):
    stats = {}
    stats_pairs = stats_string.split(", ")
    for stat in stats_pairs:
        key, value = stat.split(":")
        stats[key.strip()] = int(value.strip())
    return stats


# Fonction pour analyser les capacités à partir de la chaîne de texte
def parse_abilities(abilities_string):
    abilities = abilities_string.split(", ")
    return [ability.strip() for ability in abilities]


# Fonction pour créer la matrice d'un tournoi de 16 personnages
def create_tournament_bracket(characters):
    random.shuffle(characters)
    bracket = [(characters[i], characters[i + 1]) for i in range(0, len(characters), 2)]
    return bracket


# Fonction pour calculer le vainqueur d'une bataille entre deux Pokémon
def battle(pokemon1, pokemon2):
    # Analyser les statistiques et les capacités de chaque Pokémon
    stats1 = parse_stats(pokemon1["stats"])
    stats2 = parse_stats(pokemon2["stats"])
    abilities1 = parse_abilities(pokemon1["abilities"])
    abilities2 = parse_abilities(pokemon2["abilities"])

    # Détermination de la vitesse pour savoir qui frappe en premier
    if stats1["speed"] > stats2["speed"]:
        first, second = pokemon1, pokemon2
        first_stats, second_stats = stats1, stats2
        first_abilities, second_abilities = abilities1, abilities2
    else:
        first, second = pokemon2, pokemon1
        first_stats, second_stats = stats2, stats1
        first_abilities, second_abilities = abilities2, abilities1

    # Calcul des dégâts infligés
    round_number = 1

    while first_stats["hp"] > 0 and second_stats["hp"] > 0:
        # Choisir une capacité aléatoire pour l'attaque
        first_ability = random.choice(first_abilities)
        second_ability = random.choice(second_abilities)

        print(f"\nRound {round_number}: {first['name']} utilise {first_ability} contre {second['name']}")
        # Première attaque
        damage = stats1["attack"] + stats1["special-attack"] - stats2["defense"] - stats2["special-defense"]
        damage = max(damage, 10)  # Minimum de 10 dégâts par capacité
        second_stats["hp"] -= damage
        if second_stats["hp"] <= 0:
            print(f"{second['name']} est KO!")
            return first
        print(f"{second['name']} a {second_stats['hp']} points de vie restants.")

        # Deuxième attaque
        print(f"{second['name']} utilise {second_ability} contre {first['name']}")
        damage = stats2["attack"] + stats2["special-attack"] - stats1["defense"] - stats1["special-defense"]
        damage = max(damage, 10)  # Minimum de 10 dégâts par capacité
        first_stats["hp"] -= damage
        if first_stats["hp"] <= 0:
            print(f"{first['name']} est KO!")
            return second
        print(f"{first['name']} a {first_stats['hp']} points de vie restants.")

        round_number += 1


# Fonction pour sélectionner un vainqueur pour chaque match jusqu'à définir un vainqueur final
def determine_tournament_winner(bracket):
    tour_number = 1
    while len(bracket) > 1:
        print(f"\nTour {tour_number} :")
        next_tour = []
        for match in bracket:
            winner = battle(match[0], match[1])
            next_tour.append(winner)
            print(
                f"\033[92m{winner['name']}\033[0m vs \033[91m{match[1]['name'] if match[0]['name'] == winner['name'] else match[0]['name']}\033[0m -> Vainqueur : \033[92m{winner['name']}\033[0m")
        bracket = [(next_tour[i], next_tour[i + 1]) for i in range(0, len(next_tour), 2)]
        tour_number += 1

    # Afficher le détail de la bataille finale
    print("Bataille finale :")
    final_match = bracket[0]
    final_winner = battle(final_match[0], final_match[1])
    print(f"Le vainqueur final est : [92m{final_winner['name']}[0m")


if __name__ == "__main__":
    db_name = "pokemon.db"
    table_name = "pokemon"

    # Sélectionner 16 Pokémon aléatoires via la fonction select_random_pokemons
    pokemon_ids = select_random_pokemons()

    # Récupérer 16 personnages depuis la base de données
    characters = get_characters(db_name, table_name, pokemon_ids)
    if len(characters) == 16:
        # Créer la matrice du tournoi
        bracket = create_tournament_bracket(characters)
        print("Matrice du tournoi :")
        for match in bracket:
            print(f"{match[0]['name']} vs {match[1]['name']}")

        # Déterminer le vainqueur du tournoi
        determine_tournament_winner(bracket)
    else:
        print("Impossible de créer la matrice du tournoi : moins de 16 personnages disponibles.")