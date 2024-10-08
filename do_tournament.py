import sqlite3
import random
import curses
import time
from get_pokemons import select_random_pokemons

# Updated HP bar to handle damage display properly
def hp_bar(stdscr, y, x, current_hp, max_hp, length=40, damage=0):
    # Ensure current_hp is within valid bounds
    current_hp = max(0, min(current_hp, max_hp))

    # Calculate the segments of the HP bar
    hp_ratio = current_hp / max_hp
    filled_length = round(length * hp_ratio)

    # Calculate the length of the red part for the most recent damage
    previous_hp = current_hp + damage  # previous_hp is the HP before the hit
    previous_hp_ratio = previous_hp / max_hp
    previous_filled_length = round(length * previous_hp_ratio)

    damage_length = previous_filled_length - filled_length  # Red bar shows the damage done

    # Display the HP bar at the specified position
    stdscr.addstr(y, x, "[", curses.color_pair(3))  # Add the opening bracket in white
    stdscr.addstr("█" * filled_length, curses.color_pair(1))  # Green for remaining HP
    stdscr.addstr("░" * damage_length, curses.color_pair(2))  # Red for most recent damage
    stdscr.addstr("-" * (length - previous_filled_length), curses.color_pair(3))  # White for missing HP
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

# Function to display the tournament bracket with tiers expanding to the right
def display_bracket(screen, brackets, y_offset=0):
    max_y, max_x = screen.getmaxyx()
    x_offsets = [2, 20, 40, 60, 80]  # X positions for each tier
    base_spacing = 2  # Vertical spacing between Pokémon

    for tier_index, bracket in enumerate(brackets):
        # Set x_offset for the current tier
        x_offset = x_offsets[tier_index]

        for match_index, match in enumerate(bracket):
            # Calculate the y position for each match or winner
            y_pos = y_offset + match_index * base_spacing

            if tier_index == 0:
                # Display Pokémon in the first tier (Tier 1)
                if len(match) > 0 and y_pos < max_y:
                    screen.addstr(y_pos, x_offset, f"{match[0]['name'].capitalize():<15}", curses.color_pair(3))
                if len(match) > 1 and y_pos + 1 < max_y:
                    screen.addstr(y_pos + 1, x_offset, f"{match[1]['name'].capitalize():<15}", curses.color_pair(3))
            else:
                # Display winners in higher tiers
                if len(match) == 3 and y_pos < max_y:
                    winner = match[-1]
                    screen.addstr(y_pos, x_offset, f"{winner['name'].capitalize():<15}", curses.color_pair(3))

    # Refresh the screen to display the updates
    screen.refresh()

# Function to clear the damage text area
def clear_damage_text(screen, start_y, num_lines):
    for i in range(num_lines):
        screen.move(start_y + i, 0)
        screen.clrtoeol()

# Function for a battle between two Pokémon
def battle(screen, pokemon1, pokemon2, brackets):
    stats1 = parse_stats(pokemon1["stats"])
    stats2 = parse_stats(pokemon2["stats"])
    abilities1 = parse_abilities(pokemon1["abilities"])
    abilities2 = parse_abilities(pokemon2["abilities"])

    # Initialize HP for the battle
    current_hp1 = stats1["hp"]
    current_hp2 = stats2["hp"]

    # Determine which Pokémon goes first based on speed
    if stats1["speed"] > stats2["speed"]:
        first, second = pokemon1, pokemon2
        first_stats, second_stats = stats1, stats2
        first_abilities, second_abilities = abilities1, abilities2
    else:
        first, second = pokemon2, pokemon1
        first_stats, second_stats = stats2, stats1
        first_abilities, second_abilities = abilities2, abilities1

    round_number = 1

    # Clear the screen and display the updated bracket before starting the match
    screen.clear()
    display_bracket(screen, brackets)
    hp_bar_y_offset = 20  # Start drawing HP bars below the bracket display

    # Display initial health bars
    screen.addstr(hp_bar_y_offset, 2, f"{first['name'].capitalize():<20}", curses.color_pair(1))  # Pokémon name in green
    hp_bar(screen, hp_bar_y_offset, 24, current_hp1, stats1["hp"], length=40)  # Start health bar at column 24
    screen.addstr(hp_bar_y_offset + 1, 2, f"{second['name'].capitalize():<20}", curses.color_pair(1))  # Pokémon name in green
    hp_bar(screen, hp_bar_y_offset + 1, 24, current_hp2, stats2["hp"], length=40)  # Start health bar at column 24
    screen.refresh()
    time.sleep(1.5)

    while current_hp1 > 0 and current_hp2 > 0:
        # Clear damage text area for a clean slate before the next round
        clear_damage_text(screen, hp_bar_y_offset + 3, 7)

        # First Pokémon attacks
        first_ability = random.choice(first_abilities)
        screen.addstr(hp_bar_y_offset + 3, 2, f"Round {round_number}:", curses.color_pair(3))  # Round number in white
        screen.addstr(hp_bar_y_offset + 4, 2, f"{first['name'].capitalize()} ", curses.color_pair(1))  # Pokémon name in green
        screen.addstr("uses ", curses.color_pair(3))  # Action text in white
        screen.addstr(f"{first_ability} ", curses.color_pair(2))  # Attack name in red
        screen.addstr(f"on {second['name'].capitalize()}!", curses.color_pair(3))  # Rest of the text in white

        # Calculate damage
        damage = first_stats["attack"] + first_stats["special-attack"] - second_stats["defense"] - second_stats["special-defense"]
        damage = max(damage, 10)  # Minimum of 10 damage per attack
        previous_hp2 = current_hp2  # Store HP before hit
        current_hp2 -= damage
        current_hp2 = max(0, current_hp2)  # Ensure HP doesn't go below 0

        # Update the HP bar of the second Pokémon to reflect the damage taken (red section only)
        screen.addstr(hp_bar_y_offset + 1, 2, f"{second['name'].capitalize():<20}", curses.color_pair(1))  # Pokémon name in green
        hp_bar(screen, hp_bar_y_offset + 1, 24, current_hp2, stats2["hp"], length=40, damage=previous_hp2 - current_hp2)  # Update HP bar and number
        screen.addstr(hp_bar_y_offset + 5, 2, f"{second['name'].capitalize()} ", curses.color_pair(1))  # Pokémon name in green
        screen.addstr("takes ", curses.color_pair(3))  # Action text in white
        screen.addstr(f"{damage} damage!", curses.color_pair(2))  # Damage value in red
        screen.refresh()
        time.sleep(1.5)

        # Check if the second Pokémon is KO'd
        if current_hp2 <= 0:
            screen.addstr(hp_bar_y_offset + 6, 2, f"{second['name'].capitalize()} is KO!", curses.color_pair(2))  # KO message in red
            screen.refresh()
            time.sleep(2)
            return first  # First Pokémon wins the battle

        # Clear damage text area for the next round
        clear_damage_text(screen, hp_bar_y_offset + 7, 7)

        # Second Pokémon attacks
        second_ability = random.choice(second_abilities)
        screen.addstr(hp_bar_y_offset + 7, 2, f"{second['name'].capitalize()} ", curses.color_pair(1))  # Pokémon name in green
        screen.addstr("uses ", curses.color_pair(3))  # Action text in white
        screen.addstr(f"{second_ability} ", curses.color_pair(2))  # Attack name in red
        screen.addstr(f"on {first['name'].capitalize()}!", curses.color_pair(3))  # Rest of the text in white

        # Calculate damage
        damage = second_stats["attack"] + second_stats["special-attack"] - first_stats["defense"] - first_stats["special-defense"]
        damage = max(damage, 10)  # Minimum of 10 damage per attack
        previous_hp1 = current_hp1  # Store HP before hit
        current_hp1 -= damage
        current_hp1 = max(0, current_hp1)  # Ensure HP doesn't go below 0

        # Update the HP bar of the first Pokémon to reflect the damage taken (red section only)
        screen.addstr(hp_bar_y_offset, 2, f"{first['name'].capitalize():<20}", curses.color_pair(1))  # Pokémon name in green
        hp_bar(screen, hp_bar_y_offset, 24, current_hp1, stats1["hp"], length=40, damage=previous_hp1 - current_hp1)  # Update HP bar and number
        screen.addstr(hp_bar_y_offset + 8, 2, f"{first['name'].capitalize()} ", curses.color_pair(1))  # Pokémon name in green
        screen.addstr("takes ", curses.color_pair(3))  # Action text in white
        screen.addstr(f"{damage} damage!", curses.color_pair(2))  # Damage value in red
        screen.refresh()
        time.sleep(1.5)

        # Check if the first Pokémon is KO'd
        if current_hp1 <= 0:
            screen.addstr(hp_bar_y_offset + 9, 2, f"{first['name'].capitalize()} is KO!", curses.color_pair(2))  # KO message in red
            screen.refresh()
            time.sleep(2)
            return second  # Second Pokémon wins the battle

        # Proceed to the next round
        round_number += 1
        screen.refresh()
        time.sleep(1.5)  # Pause before the next round

    return first if current_hp1 > 0 else second


def determine_tournament_winner(screen, initial_bracket):
    brackets = [initial_bracket]  # List to keep track of all tiers of the tournament

    # While there are more than one match left in the bracket
    while len(brackets[-1]) > 1:
        current_bracket = brackets[-1]
        next_tier = []

        i = 0
        while i < len(current_bracket):
            match = current_bracket[i]
            if len(match) == 1:
                # If there's an unmatched Pokémon, automatically move to the next tier
                next_tier.append((match[0],))
                i += 1
            else:
                # Conduct battle and get the winner
                winner = battle(screen, match[0], match[1], brackets)

                # Add the winner to the next tier
                next_tier.append((winner,))

                # Update the current tier to indicate the winner in the brackets
                current_bracket[i] = (match[0], match[1], winner)

                # Clear the screen and display the updated bracket after each match
                screen.clear()
                display_bracket(screen, brackets)
                screen.refresh()
                time.sleep(1.5)  # Pause to allow user to see the updated bracket

                i += 1

        # Append the next tier of winners to the list of brackets
        brackets.append(next_tier)

    # Final match: Last match in the final tier
    final_match = brackets[-1][0]
    final_winner = battle(screen, final_match[0], final_match[1], brackets)

    # Update the final tier with the final winner
    brackets[-1][0] = (final_match[0], final_match[1], final_winner)

    # Display the final winner and the final bracket
    screen.clear()
    display_bracket(screen, brackets)
    screen.addstr(1, 2, f"Final Winner: {final_winner['name'].capitalize()}", curses.color_pair(3))
    screen.refresh()
    time.sleep(3)

# Main function to start the tournament
def main(screen):
    curses.start_color()

    # Initialize colors
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Green text for Pokémon names
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