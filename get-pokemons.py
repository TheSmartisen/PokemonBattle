import requests
import sqlite3
import random
import time

# Constants
POKEAPI_BASE_URL = 'https://pokeapi.co/api/v2/pokemon/'
DATABASE_NAME = 'pokemon.db'
NUMBER_OF_POKEMON = 16
TOTAL_POKEMON = 1302  # Fixed total number of Pokémon

def get_pokemon_data(pokemon_id):
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
        print(f"HTTP error occurred for Pokémon ID {pokemon_id}: {http_err}")
    except Exception as err:
        print(f"An error occurred for Pokémon ID {pokemon_id}: {err}")
    return None

def select_random_pokemon(total, number, existing_ids=None):
    """
    Select a unique set of random Pokémon IDs, excluding any IDs in existing_ids.

    Args:
        total (int): Total number of available Pokémon.
        number (int): Number of Pokémon to select.
        existing_ids (set, optional): Set of Pokémon IDs to exclude from selection.

    Returns:
        list: A list of unique Pokémon IDs.
    """
    if existing_ids is None:
        existing_ids = set()
    available_ids = set(range(1, total + 1)) - existing_ids
    if number > len(available_ids):
        raise ValueError("Not enough available Pokémon to select the desired number.")
    # Convert the set to a list to ensure compatibility with random.sample
    available_ids = list(available_ids)
    return random.sample(available_ids, number)

def create_database(conn):
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

def insert_pokemon(conn, pokemon):
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

def main():
    """
    Main function to orchestrate the Pokémon tournament setup.
    """
    try:
        print(f"Selecting {NUMBER_OF_POKEMON} valid random Pokémon from {TOTAL_POKEMON} total Pokémon...")
        
        selected_ids = set()
        tried_ids = set()
        pokemon_data = []
        
        while len(pokemon_data) < NUMBER_OF_POKEMON:
            remaining = NUMBER_OF_POKEMON - len(pokemon_data)
            # Select more IDs than needed to account for possible invalid IDs
            batch_size = remaining * 2
            new_ids = select_random_pokemon(TOTAL_POKEMON, batch_size, existing_ids=selected_ids.union(tried_ids))
            
            for pid in new_ids:
                if len(pokemon_data) >= NUMBER_OF_POKEMON:
                    break
                if pid in selected_ids or pid in tried_ids:
                    continue
                print(f"Fetching data for Pokémon ID {pid}...")
                data = get_pokemon_data(pid)
                if data:
                    pokemon_data.append(data)
                    selected_ids.add(pid)
                    print(f"Successfully fetched data for {data['name']} (ID: {pid}).")
                else:
                    tried_ids.add(pid)
                time.sleep(0.5)  # To respect API rate limits
            
            # If not enough Pokémon are found, adjust the strategy
            if not new_ids:
                print("No more available Pokémon to select. Exiting.")
                break
        
        if len(pokemon_data) < NUMBER_OF_POKEMON:
            print(f"Only fetched {len(pokemon_data)} valid Pokémon. Expected {NUMBER_OF_POKEMON}.")
            return
        
        print(f"\nSuccessfully fetched data for {len(pokemon_data)} Pokémon.")
        print("Creating SQLite database and table...")
        conn = sqlite3.connect(DATABASE_NAME)
        create_database(conn)

        print("Inserting Pokémon data into the database...")
        for pokemon in pokemon_data:
            insert_pokemon(conn, pokemon)

        conn.commit()
        conn.close()
        print(f"Successfully stored {len(pokemon_data)} Pokémon into '{DATABASE_NAME}'.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
