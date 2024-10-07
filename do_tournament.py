import sqlite3
import random
import curses
import time


# Function to create HP bar
def hp_bar(current_hp, max_hp, length=20):
    hp_ratio = current_hp / max_hp
    filled_length = int(length * hp_ratio)
    bar = '█' * filled_length + '-' * (length - filled_length)
    return f'[{bar}] {current_hp}/{max_hp} HP'


# Function to retrieve 16 characters from the database
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

# Function to parse stats from a string
def parse_stats(stats_string):
    stats = {}
    stats_pairs = stats_string.split(", ")
    for stat in stats_pairs:
        key, value = stat.split(":")
        stats[key.strip()] = int(value.strip())
    return stats


# Function to parse abilities from a string
def parse_abilities(abilities_string):
    abilities = abilities_string.split(", ")
    return [ability.strip() for ability in abilities]


# Function for a battle between two Pokémon
def battle(screen, pokemon1, pokemon2):
    stats1 = parse_stats(pokemon1["stats"])
    stats2 = parse_stats(pokemon2["stats"])
    abilities1 = parse_abilities(pokemon1["abilities"])
    abilities2 = parse_abilities(pokemon2["abilities"])

    # Initialize HP for the battle
    stats1["hp"] = parse_stats(pokemon1["stats"])["hp"]
    stats2["hp"] = parse_stats(pokemon2["stats"])["hp"]

    # Determine which Pokémon goes first
    if stats1["speed"] > stats2["speed"]:
        first, second = pokemon1, pokemon2
        first_stats, second_stats = stats1, stats2
        first_abilities, second_abilities = abilities1, abilities2
    else:
        first, second = pokemon2, pokemon1
        first_stats, second_stats = stats2, stats1
        first_abilities, second_abilities = abilities2, abilities1

    round_number = 1

    while first_stats["hp"] > 0 and second_stats["hp"] > 0:
        # Clear the screen before each round
        screen.clear()

        # Display current HP bars
        screen.addstr(1, 2, f"{first['name']} HP: {hp_bar(first_stats['hp'], parse_stats(first['stats'])['hp'])}")
        screen.addstr(2, 2, f"{second['name']} HP: {hp_bar(second_stats['hp'], parse_stats(second['stats'])['hp'])}")
        
        # Choose a random ability and calculate damage
        first_ability = random.choice(first_abilities)
        second_ability = random.choice(second_abilities)
        
        screen.addstr(4, 2, f"Round {round_number}:")
        screen.addstr(5, 2, f"{first['name']} uses {first_ability} on {second['name']}!")

        damage = first_stats["attack"] + first_stats["special-attack"] - second_stats["defense"] - second_stats["special-defense"]
        damage = max(damage, 10)  # Minimum of 10 damage per attack
        second_stats["hp"] -= damage
        if second_stats["hp"] <= 0:
            screen.addstr(6, 2, f"{second['name']} is KO!")
            screen.refresh()
            time.sleep(2)
            return first

        screen.addstr(6, 2, f"{second['name']} has {second_stats['hp']} HP left.")

        # Let the second Pokémon attack
        screen.addstr(7, 2, f"{second['name']} uses {second_ability} on {first['name']}!")

        damage = second_stats["attack"] + second_stats["special-attack"] - first_stats["defense"] - first_stats["special-defense"]
        damage = max(damage, 10)  # Minimum of 10 damage per attack
        first_stats["hp"] -= damage
        if first_stats["hp"] <= 0:
            screen.addstr(8, 2, f"{first['name']} is KO!")
            screen.refresh()
            time.sleep(2)
            return second

        screen.addstr(8, 2, f"{first['name']} has {first_stats['hp']} HP left.")

        round_number += 1
        screen.refresh()
        time.sleep(2)  # Pause before the next round

    return first if first_stats["hp"] > 0 else second


# Function to determine the tournament winner
def determine_tournament_winner(screen, bracket):
    tour_number = 1
    while len(bracket) > 1:
        next_tour = []
        for match in bracket:
            winner = battle(screen, match[0], match[1])
            next_tour.append(winner)
        bracket = [(next_tour[i], next_tour[i + 1]) for i in range(0, len(next_tour), 2)]
        tour_number += 1

    final_match = bracket[0]
    final_winner = battle(screen, final_match[0], final_match[1])

    screen.clear()
    screen.addstr(1, 2, f"Final Winner: {final_winner['name']}")
    screen.refresh()
    time.sleep(3)


# Main function to start the tournament
def main(screen):
    db_name = "pokemon.db"
    table_name = "pokemon"

    # Select 16 random Pokémon from the database
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT id FROM {table_name}")
        all_ids = [row[0] for row in cursor.fetchall()]
        pokemon_ids = random.sample(all_ids, 16)

    characters = get_characters(db_name, table_name, pokemon_ids)

    if len(characters) == 16:
        bracket = [(characters[i], characters[i + 1]) for i in range(0, len(characters), 2)]
        determine_tournament_winner(screen, bracket)
    else:
        screen.addstr(1, 2, "Not enough characters available for the tournament.")
        screen.refresh()
        time.sleep(2)


if __name__ == "__main__":
    curses.wrapper(main)
