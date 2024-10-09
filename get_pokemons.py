import requests
import sqlite3
import random
import time
import curses
from typing import List, Optional

# Constantes
POKEAPI_BASE_URL = 'https://pokeapi.co/api/v2/pokemon/'
DATABASE_NAME = 'pokemon.db'
NUMBER_OF_POKEMON = 16
TOTAL_POKEMON = 1302  # Nombre total de Pokémon

def get_pokemon_data(pokemon_id: int) -> Optional[dict]:
    """
    Récupérer les données d'un Pokémon spécifique par son ID depuis l'API PokéAPI.

    Args:
        pokemon_id (int): L'ID du Pokémon à récupérer.

    Returns:
        dict ou None: Les données du Pokémon sous forme de dictionnaire si réussi, sinon None.
    """
    url = f"{POKEAPI_BASE_URL}{pokemon_id}/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Lever une exception pour les erreurs HTTP
        return response.json()  # Retourner la réponse JSON sous forme de dictionnaire
    except requests.HTTPError as http_err:
        # Afficher un message d'erreur si l'ID du Pokémon n'est pas trouvé
        print(f"Le Pokémon numéro {pokemon_id} n'existe pas !")
    except Exception as err:
        # Afficher un message d'erreur général pour tout autre problème
        print(f"Une erreur est survenue pour le Pokémon ID {pokemon_id}: {err}")
    return None

def create_database(conn: sqlite3.Connection):
    """
    Créer la table 'pokemon' dans la base de données SQLite si elle n'existe pas.

    Args:
        conn (sqlite3.Connection): La connexion à la base de données SQLite.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS pokemon (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        height INTEGER,
        weight INTEGER,
        base_experience INTEGER,
        abilities TEXT,
        types TEXT,
        stats TEXT
    );
    """
    conn.execute(create_table_query)  # Exécuter la requête pour créer la table
    conn.commit()  # Valider les changements dans la base de données

def insert_pokemon(conn: sqlite3.Connection, pokemon: dict):
    """
    Insérer les données d'un Pokémon dans la base de données.

    Args:
        conn (sqlite3.Connection): La connexion à la base de données SQLite.
        pokemon (dict): Les données du Pokémon.
    """
    insert_query = """
    INSERT OR REPLACE INTO pokemon (id, name, height, weight, base_experience, abilities, types, stats)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    # Extraire les capacités, types et statistiques des données du Pokémon
    abilities = ', '.join([ability['ability']['name'] for ability in pokemon.get('abilities', [])])
    types = ', '.join([ptype['type']['name'] for ptype in pokemon.get('types', [])])
    stats = ', '.join([f"{stat['stat']['name']}:{stat['base_stat']}" for stat in pokemon.get('stats', [])])
    
    # Préparer le tuple de données pour l'insertion
    data = (
        pokemon['id'],
        pokemon['name'],
        pokemon.get('height'),
        pokemon.get('weight'),
        pokemon.get('base_experience'),
        abilities,
        types,
        stats
    )
    # Exécuter la requête d'insertion avec les données fournies
    conn.execute(insert_query, data)
    conn.commit()  # Valider les changements dans la base de données

def check_pokemon_in_db(conn: sqlite3.Connection, pokemon_id: int) -> bool:
    """
    Vérifier si les données d'un Pokémon sont déjà stockées dans la base de données.

    Args:
        conn (sqlite3.Connection): La connexion à la base de données SQLite.
        pokemon_id (int): L'ID du Pokémon.

    Returns:
        bool: True si le Pokémon est dans la base de données, False sinon.
    """
    # Exécuter une requête pour vérifier si l'ID du Pokémon existe dans la base de données
    cursor = conn.execute("SELECT 1 FROM pokemon WHERE id = ?", (pokemon_id,))
    return cursor.fetchone() is not None  # Retourner True si un résultat est trouvé

def get_pokemon_name_from_db(conn: sqlite3.Connection, pokemon_id: int) -> Optional[str]:
    """
    Récupérer le nom d'un Pokémon par son ID depuis la base de données.

    Args:
        conn (sqlite3.Connection): La connexion à la base de données SQLite.
        pokemon_id (int): L'ID du Pokémon.

    Returns:
        str ou None: Le nom du Pokémon si trouvé, sinon None.
    """
    # Exécuter une requête pour récupérer le nom du Pokémon par son ID
    cursor = conn.execute("SELECT name FROM pokemon WHERE id = ?", (pokemon_id,))
    result = cursor.fetchone()
    return result[0] if result else None  # Retourner le nom si trouvé, sinon None

def select_random_pokemons(stdscr) -> List[int]:
    """
    Sélectionner 16 IDs de Pokémon au hasard, s'assurer que leurs données sont stockées dans la base de données,
    récupérer et stocker les données pour ceux qui ne sont pas déjà dans la base de données, et retourner les IDs.

    Args:
        stdscr: L'écran curses pour l'affichage.

    Returns:
        list: Une liste de 16 IDs de Pokémon.
    """
    selected_ids = []  # Liste pour stocker les IDs de Pokémon sélectionnés
    tried_ids = set()  # Ensemble pour suivre les IDs déjà essayés

    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            create_database(conn)  # S'assurer que la table est créée si elle n'existe pas
            
            latest_status = ""  # Pour stocker le dernier statut de récupération
            
            while len(selected_ids) < NUMBER_OF_POKEMON:
                remaining = NUMBER_OF_POKEMON - len(selected_ids)
                new_ids = random.sample(range(1, TOTAL_POKEMON + 1), remaining)  # Sélectionner des IDs de Pokémon au hasard

                for pid in new_ids:
                    if pid in tried_ids:
                        continue  # Passer si cet ID de Pokémon a déjà été essayé
                    
                    # Afficher la récupération en cours
                    latest_status = f"Récupération des données du Pokémon numéro {pid}...\n"
                    stdscr.clear()
                    stdscr.addstr(latest_status)
                    stdscr.addstr("\nListe des Pokémon :\n\n")
                    for i, pokemon_id in enumerate(selected_ids, start=1):
                        pokemon_name = get_pokemon_name_from_db(conn, pokemon_id)
                        stdscr.addstr(f"{i}. {pokemon_name}\n")  # Utiliser la couleur blanche par défaut pour la liste des Pokémon
                    stdscr.refresh()
                    
                    if check_pokemon_in_db(conn, pid):
                        # Si le Pokémon est déjà dans la base de données, récupérer son nom
                        pokemon_name = get_pokemon_name_from_db(conn, pid)
                        selected_ids.append(pid)  # Ajouter l'ID du Pokémon à la liste sélectionnée
                    else:
                        # Récupérer les données depuis l'API si pas dans la base de données
                        pokemon_data = get_pokemon_data(pid)
                        
                        if isinstance(pokemon_data, dict):  # Vérifier que les données récupérées sont un dictionnaire
                            # Insérer les données du Pokémon dans la base de données si récupérées avec succès
                            insert_pokemon(conn, pokemon_data)
                            selected_ids.append(pid)  # Ajouter l'ID du Pokémon à la liste sélectionnée
                            latest_status = f"Données du Pokémon numéro {pid}: {pokemon_data['name']} enregistrées.\n"
                            stdscr.addstr(latest_status)
                        else:
                            tried_ids.add(pid)  # Marquer comme essayé si la récupération a échoué
                            latest_status = f"Erreur : Le Pokémon numéro {pid} n'a pas pu être récupéré.\n"
                            stdscr.addstr(latest_status)
                    
                    # Afficher la liste et le statut mis à jour
                    stdscr.clear()
                    stdscr.addstr(latest_status)
                    stdscr.addstr("\nListe des Pokémon :\n\n")
                    for i, pokemon_id in enumerate(selected_ids, start=1):
                        pokemon_name = get_pokemon_name_from_db(conn, pokemon_id)
                        stdscr.addstr(f"{i}. {pokemon_name}\n")  # Utiliser la couleur blanche par défaut pour la liste des Pokémon
                    stdscr.refresh()
                    
                    time.sleep(0.5)  # Respecter les limites de l'API
        
        return selected_ids  # Retourner la liste des IDs de Pokémon sélectionnés

    except Exception as e:
        # Afficher un message d'erreur si une exception se produit
        stdscr.addstr(f"Une erreur est survenue: {e}\n")
        stdscr.refresh()
        return []
    finally:
        # Effacer l'écran après la récupération
        stdscr.clear()
        stdscr.refresh()

# Optionnel : Permettre de lancer ce script directement pour des tests avec curses
if __name__ == "__main__":
    def main(stdscr):
        # Initialiser les paires de couleurs
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)  # Rouge
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Vert
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Bleu
        
        # Appeler la fonction principale
        select_random_pokemons(stdscr)
    
    curses.wrapper(main)  # Utiliser curses pour gérer l'affichage