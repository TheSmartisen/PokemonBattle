import sqlite3
import random
import curses
import time
from get_pokemons import select_random_pokemons

# Function to create HP bar using curses
def hp_bar(stdscr, y, x, current_hp, max_hp, length=40, damage=0):
    # Ensure current_hp is within valid bounds
    current_hp = max(0, min(current_hp, max_hp))

    # Calculate the segments of the HP bar
    hp_ratio = current_hp / max_hp
    filled_length = round(length * hp_ratio)

    # Calculate the length of the red part for the most recent damage
    damage_length = min(round(length * (damage / max_hp)), filled_length)
    remaining_length = filled_length - damage_length

    # Display the HP bar at the specified position
    stdscr.addstr(y, x, "[", curses.color_pair(3))  # Add the opening bracket in white
    stdscr.addstr("█" * remaining_length, curses.color_pair(1))  # Green for remaining HP
    stdscr.addstr("░" * damage_length, curses.color_pair(2))     # Red for most recent damage
    stdscr.addstr("-" * (length - filled_length), curses.color_pair(3))  # White for missing HP
    stdscr.addstr("]", curses.color_pair(3))  # Closing bracket in white
    stdscr.addstr(f" {current_hp}/{max_hp} HP", curses.color_pair(3))  # Display the HP count

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

# Function to clear the damage text area
def clear_damage_text(screen, start_y, num_lines):
    for i in range(num_lines):
        screen.move(start_y + i, 0)
        screen.clrtoeol()

# Function for a battle between two Pokémon
def battle(screen, pokemon1, pokemon2, bracket, winners):
    stats1 = parse_stats(pokemon1["stats"])
    stats2 = parse_stats(pokemon2["stats"])
    abilities1 = parse_abilities(pokemon1["abilities"])
    abilities2 = parse_abilities(pokemon2["abilities"])

    # Initialize HP for the battle
    current_hp1 = stats1["hp"]
    current_hp2 = stats2["hp"]

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

    # Draw both Pokémon with full health at the start of the match
    screen.clear()
    display_bracket(screen, bracket, winners)
    screen.addstr(20, 2, f"{first['name'].capitalize():<20}", curses.color_pair(1))  # Pokémon name in green with reserved space
    hp_bar(screen, 20, 24, current_hp1, stats1["hp"], length=40)  # Start health bar at column 24
    screen.addstr(21, 2, f"{second['name'].capitalize():<20}", curses.color_pair(1))  # Pokémon name in green with reserved space
    hp_bar(screen, 21, 24, current_hp2, stats2["hp"], length=40)  # Start health bar at column 24
    screen.refresh()
    time.sleep(1.5)

    while current_hp1 > 0 and current_hp2 > 0:
        # Clear damage text area for a clean slate before the next round
        clear_damage_text(screen, 23, 7)

        # First Pokémon attacks
        first_ability = random.choice(first_abilities)
        screen.addstr(23, 2, f"Round {round_number}:", curses.color_pair(3))  # Round number in white
        screen.addstr(24, 2, f"{first['name'].capitalize()} ", curses.color_pair(1))  # Pokémon name in green
        screen.addstr("uses ", curses.color_pair(3))  # Action text in white
        screen.addstr(f"{first_ability} ", curses.color_pair(2))  # Attack name in red
        screen.addstr(f"on {second['name'].capitalize()}!", curses.color_pair(3))  # Rest of the text in white

        # Calculate damage
        damage = first_stats["attack"] + first_stats["special-attack"] - second_stats["defense"] - second_stats["special-defense"]
        damage = max(damage, 10)  # Minimum of 10 damage per attack
        current_hp2 -= damage
        current_hp2 = max(0, current_hp2)  # Ensure HP doesn't go below 0

        # Update the HP bar of the second Pokémon to reflect the damage taken (red section only)
        screen.addstr(21, 2, f"{second['name'].capitalize():<20}", curses.color_pair(1))  # Pokémon name in green with reserved space
        hp_bar(screen, 21, 24, current_hp2 + damage, stats2["hp"], length=40, damage=damage)
        screen.addstr(25, 2, f"{second['name'].capitalize()} ", curses.color_pair(1))  # Pokémon name in green
        screen.addstr("takes ", curses.color_pair(3))  # Action text in white
        screen.addstr(f"{damage} damage!", curses.color_pair(2))  # Damage value in red
        screen.refresh()
        time.sleep(1.5)

        # Check if the second Pokémon is KO'd
        if current_hp2 <= 0:
            screen.addstr(26, 2, f"{second['name'].capitalize()} is KO!", curses.color_pair(2))  # KO message in red
            screen.refresh()
            time.sleep(2)
            return first

        # Clear damage text area for the next round
        clear_damage_text(screen, 27, 7)

        # Second Pokémon attacks
        second_ability = random.choice(second_abilities)
        screen.addstr(27, 2, f"{second['name'].capitalize()} ", curses.color_pair(1))  # Pokémon name in green
        screen.addstr("uses ", curses.color_pair(3))  # Action text in white
        screen.addstr(f"{second_ability} ", curses.color_pair(2))  # Attack name in red
        screen.addstr(f"on {first['name'].capitalize()}!", curses.color_pair(3))  # Rest of the text in white

        # Calculate damage
        damage = second_stats["attack"] + second_stats["special-attack"] - first_stats["defense"] - first_stats["special-defense"]
        damage = max(damage, 10)  # Minimum of 10 damage per attack
        current_hp1 -= damage
        current_hp1 = max(0, current_hp1)  # Ensure HP doesn't go below 0

        # Update the HP bar of the first Pokémon to reflect the damage taken (red section only)
        screen.addstr(20, 2, f"{first['name'].capitalize():<20}", curses.color_pair(1))  # Pokémon name in green with reserved space
        hp_bar(screen, 20, 24, current_hp1 + damage, stats1["hp"], length=40, damage=damage)
        screen.addstr(28, 2, f"{first['name'].capitalize()} ", curses.color_pair(1))  # Pokémon name in green
        screen.addstr("takes ", curses.color_pair(3))  # Action text in white
        screen.addstr(f"{damage} damage!", curses.color_pair(2))  # Damage value in red
        screen.refresh()
        time.sleep(1.5)

        # Check if the first Pokémon is KO'd
        if current_hp1 <= 0:
            screen.addstr(29, 2, f"{first['name'].capitalize()} is KO!", curses.color_pair(2))  # KO message in red
            screen.refresh()
            time.sleep(2)
            return second

        # Proceed to the next round
        round_number += 1
        screen.refresh()
        time.sleep(1.5)  # Pause before the next round

    return first if current_hp1 > 0 else second


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
    pokemon_ids = select_random_pokemons(screen)

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