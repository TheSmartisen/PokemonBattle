import sqlite3
import random
import curses
import time


# Function to create HP bar
def hp_bar(current_hp, max_hp, length=40, damage=0):
    hp_ratio = current_hp / max_hp
    filled_length = int(length * hp_ratio)
    damage_length = min(int(length * (damage / max_hp)), filled_length)
    remaining_length = filled_length - damage_length

    bar = (
        '█' * remaining_length +
        '░' * damage_length +
        ' ' * (length - filled_length)
    )
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


# Function to display the tournament bracket
def display_bracket(screen, bracket, winners, y_offset=0):
    for i, match in enumerate(bracket):
        pokemon1, pokemon2 = match
        winner = winners[i] if i < len(winners) else None
        screen.addstr(y_offset + i * 2, 2, f"{pokemon1['name'].capitalize():<15} ┐")
        screen.addstr(y_offset + i * 2 + 1, 2, f"{pokemon2['name'].capitalize():<15} ┘")
        if winner:
            screen.addstr(y_offset + i * 2 + 1, 22, f"Winner: {winner['name'].capitalize()}")


# Function for a battle between two Pokémon
def battle(screen, pokemon1, pokemon2, bracket, winners):
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

        # Display the tournament bracket
        display_bracket(screen, bracket, winners)

        # Display current HP bars and align them
        max_hp1 = parse_stats(first['stats'])["hp"]
        max_hp2 = parse_stats(second['stats'])["hp"]
        screen.addstr(20, 12, f"{first['name'].capitalize():<10} HP: {hp_bar(first_stats['hp'], max_hp1, length=40)}", curses.color_pair(1))
        screen.addstr(21, 12, f"{second['name'].capitalize():<10} HP: {hp_bar(second_stats['hp'], max_hp2, length=40)}", curses.color_pair(1))
        
        # Choose a random ability and calculate damage
        first_ability = random.choice(first_abilities)
        second_ability = random.choice(second_abilities)
        
        screen.addstr(23, 2, f"Round {round_number}:")
        screen.addstr(24, 2, f"{first['name'].capitalize()} uses ", curses.color_pair(1))
        screen.addstr(f"{first_ability} on {second['name'].capitalize()}!", curses.color_pair(2))

        damage = first_stats["attack"] + first_stats["special-attack"] - second_stats["defense"] - second_stats["special-defense"]
        damage = max(damage, 10)  # Minimum of 10 damage per attack
        second_stats["hp"] -= damage
        if second_stats["hp"] <= 0:
            screen.addstr(25, 2, f"{second['name'].capitalize()} is KO!", curses.color_pair(2))
            screen.addstr(21, 12, f"{second['name'].capitalize():<10} HP: {hp_bar(second_stats['hp'], max_hp2, length=40, damage=damage)}", curses.color_pair(1))
            screen.refresh()
            time.sleep(2)
            return first

        screen.addstr(25, 2, f"{second['name'].capitalize()} takes ", curses.color_pair(2))
        screen.addstr(f"{damage} damage!", curses.color_pair(2))

        # Update the HP bars showing the damage done
        screen.addstr(21, 12, f"{second['name'].capitalize():<10} HP: {hp_bar(second_stats['hp'], max_hp2, length=40, damage=damage)}", curses.color_pair(1))
        screen.refresh()
        time.sleep(2)

        # Let the second Pokémon attack
        screen.addstr(26, 2, f"{second['name'].capitalize()} uses ", curses.color_pair(1))
        screen.addstr(f"{second_ability} on {first['name'].capitalize()}!", curses.color_pair(2))

        damage = second_stats["attack"] + second_stats["special-attack"] - first_stats["defense"] - first_stats["special-defense"]
        damage = max(damage, 10)  # Minimum of 10 damage per attack
        first_stats["hp"] -= damage
        if first_stats["hp"] <= 0:
            screen.addstr(27, 2, f"{first['name'].capitalize()} is KO!", curses.color_pair(2))
            screen.addstr(20, 12, f"{first['name'].capitalize():<10} HP: {hp_bar(first_stats['hp'], max_hp1, length=40, damage=damage)}", curses.color_pair(1))
            screen.refresh()
            time.sleep(2)
            return second

        screen.addstr(27, 2, f"{first['name'].capitalize()} takes ", curses.color_pair(2))
        screen.addstr(f"{damage} damage!", curses.color_pair(2))

        # Update the HP bars showing the damage done
        screen.addstr(20, 12, f"{first['name'].capitalize():<10} HP: {hp_bar(first_stats['hp'], max_hp1, length=40, damage=damage)}", curses.color_pair(1))

        round_number += 1
        screen.refresh()
        time.sleep(2)  # Pause before the next round

    return first if first_stats["hp"] > 0 else second


# Function to determine the tournament winner
def determine_tournament_winner(screen, bracket):
    winners = []
    tour_number = 1
    while len(bracket) > 1:
        next_tour = []
        for match in bracket:
            winner = battle(screen, match[0], match[1], bracket, winners)
            winners.append(winner)
            next_tour.append(winner)
        bracket = [(next_tour[i], next_tour[i + 1]) for i in range(0, len(next_tour), 2)]
        tour_number += 1

    final_match = bracket[0]
    final_winner = battle(screen, final_match[0], final_match[1], bracket, winners)

    screen.clear()
    screen.addstr(1, 2, f"Final Winner: {final_winner['name'].capitalize()}", curses.color_pair(1))
    screen.refresh()
    time.sleep(3)


# Main function to start the tournament
def main(screen):
    curses.start_color()

    # Initialize colors
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Green text for Pokémon names
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)  # Red text for damage and attack names
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)  # White text for the base health bar

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