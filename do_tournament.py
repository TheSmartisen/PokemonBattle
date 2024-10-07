import sqlite3
import random
from get_pokemons import select_random_pokemons


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


# Fonction pour créer la matrice d'un tournoi de 16 personnages
def create_tournament_bracket(characters):
    random.shuffle(characters)
    bracket = [(characters[i], characters[i + 1]) for i in range(0, len(characters), 2)]
    return bracket


# Fonction pour calculer le vainqueur d'une bataille entre deux Pokémon
def battle(pokemon1, pokemon2):
    # Le vainqueur est déterminé en fonction de l'expérience de base et d'un facteur aléatoire
    score1 = pokemon1["base_experience"] + random.randint(0, 50)
    score2 = pokemon2["base_experience"] + random.randint(0, 50)
    print(
        f"Bataille entre {pokemon1['name']} (Expérience : {pokemon1['base_experience']}, Score : {score1}) vs {pokemon2['name']} (Expérience : {pokemon2['base_experience']}, Score : {score2})")
    if score1 > score2:
        # Vainqueur en vert
        # Perdant en rouge
        return pokemon1
    else:
        # Perdant en rouge
        return pokemon2


# Fonction pour sélectionner un vainqueur pour chaque match jusqu'à définir un vainqueur final
def determine_tournament_winner(bracket):
    round_number = 1
    while len(bracket) > 1:
        print(f"\nRound {round_number} :")
        next_round = []
        for match in bracket:
            winner = battle(match[0], match[1])
            next_round.append(winner)
            print(
                f"[92m{winner['name']}[0m vs [91m{match[1]['name'] if match[0]['name'] == winner['name'] else match[0]['name']}[0m -> Vainqueur : [92m{winner['name']}[0m")
        bracket = [(next_round[i], next_round[i + 1]) for i in range(0, len(next_round), 2)]
        round_number += 1
    print(f"\nLe vainqueur final est : \033[92m{bracket[0][0]['name']}\033[0m")


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