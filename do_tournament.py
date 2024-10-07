import requests
import sqlite3
import json
import random
from get_pokemons import select_random_pokemons


# Fonction pour récupérer 16 personnages depuis la base de données
def get_characters(db_name, table_name, pokemon_ids):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    placeholders = ','.join('?' for _ in pokemon_ids)
    cursor.execute(f'''
        SELECT name, height, weight, base_experience FROM {table_name} WHERE id IN ({placeholders})
    ''', pokemon_ids)
    characters = []
    for row in cursor.fetchall():
        character = {
            "name": row[0],
            "height": row[1],
            "weight": row[2],
            "base_experience": row[3]
        }
        characters.append(character)
    conn.close()
    return characters


# Fonction pour créer la matrice d'un tournoi de 16 personnages
def create_tournament_bracket(characters):
    random.shuffle(characters)
    bracket = [(characters[i]["name"], characters[i + 1]["name"]) for i in range(0, len(characters), 2)]
    return bracket


# Fonction pour sélectionner un vainqueur pour chaque match jusqu'à définir un vainqueur final
def determine_tournament_winner(bracket):
    round_number = 1
    while len(bracket) > 1:
        print(f"\nRound {round_number} :")
        next_round = []
        for match in bracket:
            winner = random.choice(match)
            next_round.append(winner)
            print(f"{match[0]} vs {match[1]} -> Vainqueur : {winner}")
        bracket = [(next_round[i], next_round[i + 1]) for i in range(0, len(next_round), 2)]
        round_number += 1
    print(f"\nLe vainqueur final est : {bracket[0][0]}")


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
            print(f"{match[0]} vs {match[1]}")

        # Déterminer le vainqueur du tournoi
        determine_tournament_winner(bracket)
    else:
        print("Impossible de créer la matrice du tournoi : moins de 16 personnages disponibles.")