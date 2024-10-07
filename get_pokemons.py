import requests
import sqlite3
import random
import time
from typing import List, Optional

# Constants
POKEAPI_BASE_URL = 'https://pokeapi.co/api/v2/pokemon/'
DATABASE_NAME = 'pokemon.db'
NUMBER_OF_POKEMON = 16
TOTAL_POKEMON = 1302  # Fixed total number of Pokémon

def get_pokemon_data(pokemon_id: int) -> Optional[dict]:
    """
    Fetch data for a specific Pokémon by its ID from the PokéAPI.

    Args:
        pokemon_id (int): The ID of the Pokémon to fetch.

    Returns:
        dict or None: The Pokémon data as a dictionary if successful, else None.
    """
    url = f"{POKEAPI_BASE_URL}{pokemon_id}/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.HTTPError as http_err:
        print(f"\033[91mHTTP error occurred for Pokémon ID {pokemon_id}: {http_err}\033[0m\n")
    except Exception as err:
        print(f"\033[91mAn error occurred for Pokémon ID {pokemon_id}: {err}\033[0m\n")
    return None

def create_database(conn: sqlite3.Connection):
    """
    Create the 'pokemon' table in the SQLite database if it doesn't exist.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
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
    conn.execute(create_table_query)
    conn.commit()

def insert_pokemon(conn: sqlite3.Connection, pokemon: dict):
    """
    Insert a Pokémon's data into the database.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        pokemon (dict): The Pokémon data.
    """
    insert_query = """
    INSERT OR REPLACE INTO pokemon (id, name, height, weight, base_experience, abilities, types, stats)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """
    abilities = ', '.join([ability['ability']['name'] for ability in pokemon.get('abilities', [])])
    types = ', '.join([ptype['type']['name'] for ptype in pokemon.get('types', [])])
    stats = ', '.join([f"{stat['stat']['name']}:{stat['base_stat']}" for stat in pokemon.get('stats', [])])
    
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
    conn.execute(insert_query, data)
    conn.commit()

def check_pokemon_in_db(conn: sqlite3.Connection, pokemon_id: int) -> bool:
    """
    Check if a Pokémon's data is already stored in the database.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        pokemon_id (int): The ID of the Pokémon.

    Returns:
        bool: True if the Pokémon is in the database, False otherwise.
    """
    cursor = conn.execute("SELECT 1 FROM pokemon WHERE id = ?", (pokemon_id,))
    return cursor.fetchone() is not None

def get_pokemon_name_from_db(conn: sqlite3.Connection, pokemon_id: int) -> Optional[str]:
    """
    Retrieve the name of a Pokémon by its ID from the database.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        pokemon_id (int): The ID of the Pokémon.

    Returns:
        str or None: The name of the Pokémon if found, else None.
    """
    cursor = conn.execute("SELECT name FROM pokemon WHERE id = ?", (pokemon_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def select_random_pokemons() -> List[int]:
    """
    Select 16 random Pokémon IDs, ensure their data is stored in the database,
    fetch and store data for those not already in the database, and return the IDs.

    Returns:
        list: A list of 16 Pokémon IDs.
    """
    selected_ids = []
    tried_ids = set()

    try:
        with sqlite3.connect(DATABASE_NAME) as conn:
            create_database(conn)  # Ensure the table is created if not exists
            
            while len(selected_ids) < NUMBER_OF_POKEMON:
                remaining = NUMBER_OF_POKEMON - len(selected_ids)
                new_ids = random.sample(range(1, TOTAL_POKEMON + 1), remaining)

                for pid in new_ids:
                    if pid in tried_ids:
                        continue  # Skip if we've already tried this Pokémon ID
                    
                    if check_pokemon_in_db(conn, pid):
                        pokemon_name = get_pokemon_name_from_db(conn, pid)  # Retrieve the Pokémon's name
                        print(f"Pokémon ID \033[92m{pid} ({pokemon_name})\033[0m already in the database.\n")  # Show ID and name in green
                        selected_ids.append(pid)
                    else:
                        # Fetch data from API if not in database
                        print(f"Fetching Pokémon ID {pid} from API...")
                        pokemon_data = get_pokemon_data(pid)
                        
                        if pokemon_data:
                            insert_pokemon(conn, pokemon_data)
                            selected_ids.append(pid)
                            print(f"Stored data for Pokémon ID \033[94m{pid}\033[0m: \033[94m{pokemon_data['name']}\033[0m.\n")
                        else:
                            tried_ids.add(pid)  # Mark as tried if fetch failed
                    
                    time.sleep(0.5)  # Respect API rate limits
        
        return selected_ids

    except Exception as e:
        print(f"\033[91mAn error occurred: {e}\033[0m")
        return []

# Optional: Allow running this script directly for testing
if __name__ == "__main__":
    ids = select_random_pokemons()
    print(f"Selected Pokémon IDs: {ids}")
