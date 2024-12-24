import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Initialize session state for storing data
if "prix_history" not in st.session_state:
    st.session_state.prix_history = []

if "players" not in st.session_state:
    st.session_state.players = {}  # {name: {"total_races": 0}}

if "selected_players_for_prix" not in st.session_state:
    st.session_state.selected_players_for_prix = []

# move to pull from track database
TRACK_LIST = [
    "Bowser's Castle",
    "Rainbow Road",
    "Mario Circuit",
    "Luigi Circuit",
    "Moo Moo Meadows",
    "Mushroom Gorge",
    "Coconut Mall",
    "DK Summit",
    "Wario's Gold Mine",
    "Maple Treeway",
    "Grumble Volcano",
    "Dry Dry Ruins",
    "Moonview Highway",
    "Koopa Cape",
]

st.set_page_config(page_title="Race Tracker", page_icon="🏎️", layout="wide")
st.title("🏎️ Race Tournament Tracker")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Player Profiles", "Create Prix", "History"])

with tab1:
    st.header("Leaderboard")

    if st.session_state.players:
        # Create leaderboard dataframe
        leaderboard_data = []
        for player, stats in st.session_state.players.items():
            leaderboard_data.append(
                {
                    "Player": player,
                    "Total Races": stats["total_races"],
                }
            )

        df_leaderboard = pd.DataFrame(leaderboard_data)
        df_leaderboard = df_leaderboard.sort_values("Total Races", ascending=False)
        st.dataframe(df_leaderboard, use_container_width=True)
    else:
        st.info("No player data available yet. Create a Prix to get started!")

with tab2:
    st.header("Player Profiles")

    if st.session_state.players:
        selected_player = st.selectbox(
            "Select Player", list(st.session_state.players.keys())
        )

        if selected_player:
            stats = st.session_state.players[selected_player]
            st.metric("Total Races", stats["total_races"])
    else:
        st.info("No player data available yet. Create a Prix to get started!")

with tab3:
    st.header("Create Prix")

    # Player selection section (outside the form)
    st.subheader("Select Players")

    # Single-select existing players with "Add New Player" option
    existing_players = [
        p
        for p in ["jacob", "jake", "josh", "jason", "jeff", "jordan", "jeremy"]
        if p not in st.session_state.selected_players_for_prix
    ]
    player_options = existing_players + ["+ Add New Player"]

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_option = st.selectbox(
            "Select or Add Player", options=player_options, key="player_selector"
        )

        if selected_option == "+ Add New Player":
            # Create columns for the new player form
            col_fname, col_lname = st.columns(2)
            with col_fname:
                first_name = st.text_input("First Name")
            with col_lname:
                last_name = st.text_input("Last Name")
            nickname = st.text_input("Nickname")
            player_to_add = nickname
        else:
            player_to_add = selected_option

        if player_to_add:
            # Vehicle customization for all players
            st.subheader("Kart Combo")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                character = st.selectbox(
                    "Character",
                    options=[
                        "Mario",
                        "Luigi",
                        "Peach",
                        "Daisy",
                        "Rosalina",
                        "Tanooki Mario",
                        "Cat Peach",
                        "Yoshi",
                        "Toad",
                        "Koopa Troopa",
                        "Shy Guy",
                        "Lakitu",
                        "Toadette",
                        "King Boo",
                        "Baby Mario",
                        "Baby Luigi",
                        "Baby Peach",
                        "Baby Daisy",
                        "Baby Rosalina",
                        "Metal Mario",
                        "Pink Gold Peach",
                        "Wario",
                        "Waluigi",
                        "Donkey Kong",
                        "Bowser",
                        "Dry Bones",
                        "Bowser Jr",
                        "Dry Bowser",
                        "Lemmy",
                        "Larry",
                        "Wendy",
                        "Ludwig",
                        "Iggy",
                        "Roy",
                        "Morton",
                        "Inkling Girl",
                        "Inkling Boy",
                        "Link",
                        "Villager (M)",
                        "Villager (F)",
                        "Isabelle",
                        "Mii",
                    ],
                )

            with col2:
                kart = st.selectbox(
                    "Kart",
                    options=[
                        "Standard Kart",
                        "Pipe Frame",
                        "Mach 8",
                        "Steel Driver",
                        "Cat Cruiser",
                        "Circuit Special",
                        "Tri-Speeder",
                        "Badwagon",
                        "Prancer",
                        "Biddybuggy",
                        "Landship",
                        "Sneeker",
                        "Sports Coupe",
                        "Gold Standard",
                        "Standard Bike",
                        "Comet",
                        "Sport Bike",
                        "The Duke",
                        "Flame Rider",
                        "Varmint",
                        "Mr. Scooty",
                        "Jet Bike",
                        "Yoshi Bike",
                    ],
                )

            with col3:
                wheels = st.selectbox(
                    "Wheels",
                    options=[
                        "Standard",
                        "Monster",
                        "Roller",
                        "Slim",
                        "Slick",
                        "Metal",
                        "Button",
                        "Off-Road",
                        "Sponge",
                        "Wood",
                        "Cushion",
                        "Blue Standard",
                        "Hot Monster",
                        "Azure Roller",
                        "Crimson Slim",
                        "Cyber Slick",
                    ],
                )

            with col4:
                glider = st.selectbox(
                    "Glider",
                    options=[
                        "Super Glider",
                        "Cloud Glider",
                        "Wario Wing",
                        "Waddle Wing",
                        "Peach Parasol",
                        "Parachute",
                        "Parafoil",
                        "Flower Glider",
                        "Bowser Kite",
                        "Plane Glider",
                        "MKTV Parafoil",
                        "Gold Glider",
                    ],
                )

            if st.button("Add to Prix"):
                # Initialize new player if needed
                if player_to_add not in st.session_state.players:
                    st.session_state.players[player_to_add] = {
                        "total_races": 0,
                        "player_info": (
                            {
                                "first_name": first_name,
                                "last_name": last_name,
                                "nickname": nickname,
                                "vehicle": {
                                    "character": character,
                                    "kart": kart,
                                    "wheels": wheels,
                                    "glider": glider,
                                },
                            }
                            if selected_option == "+ Add New Player"
                            else {
                                "first_name": player_to_add,
                                "last_name": "",
                                "nickname": player_to_add,
                                "vehicle": {
                                    "character": character,
                                    "kart": kart,
                                    "wheels": wheels,
                                    "glider": glider,
                                },
                            }
                        ),
                    }
                else:
                    # Update vehicle setup for existing player
                    st.session_state.players[player_to_add]["player_info"][
                        "vehicle"
                    ] = {
                        "character": character,
                        "kart": kart,
                        "wheels": wheels,
                        "glider": glider,
                    }

                # Add to selected players
                st.session_state.selected_players_for_prix.append(player_to_add)
                st.rerun()

    # Display selected players with remove buttons
    if st.session_state.selected_players_for_prix:
        st.write("Selected Players:")
        for idx, player in enumerate(st.session_state.selected_players_for_prix):
            col1, col2 = st.columns([3, 1])
            with col1:
                vehicle = st.session_state.players[player]["player_info"]["vehicle"]
                st.write(
                    f"{idx + 1}. {player} "
                    f"({vehicle['character']}, {vehicle['kart']}, "
                    f"{vehicle['wheels']}, {vehicle['glider']})"
                )
            with col2:
                if st.button(f"Remove {player}", key=f"remove_{player}"):
                    st.session_state.selected_players_for_prix.remove(player)
                    st.rerun()
    else:
        st.info("Add players to the Prix using the selector above")

    # Prix Setup Form (just for starting the prix)
    with st.form("prix_setup"):
        # Add Prix settings
        st.subheader("Prix Settings")

        col1, col2 = st.columns(2)

        with col1:
            # CC Class selection
            cc_class = st.selectbox(
                "CC Class",
                options=["50cc", "100cc", "150cc", "Mirror", "200cc"],
                index=4,  # Default to 150cc
            )

            # Teams toggle
            teams_enabled = st.toggle("Teams Enabled", value=False)

            # Items selection
            items_setting = st.selectbox(
                "Items",
                options=[
                    "Normal Items",
                    "No Items",
                    "Shells Only",
                    "Bananas Only",
                    "Mushrooms Only",
                    "Custom",
                ],
                index=0,
            )

        with col2:
            # COM settings
            com_level = st.selectbox(
                "COM Level",
                options=["Normal", "Hard"],
                index=1,
            )

            com_vehicles = st.selectbox(
                "COM Vehicles",
                options=["All Vehicles", "Karts Only", "Bikes Only", "Random"],
                index=0,
            )

            # Course selection
            course_setting = st.selectbox(
                "Courses",
                options=[
                    "Random",
                    "Choose",
                    "In Order",
                ],
                index=0,
            )

        # Number of races selection
        num_races = st.selectbox(
            "Number of Races",
            options=[1, 4, 6, 8, 12, 16, 24, 48, 64],
            index=0,
        )

        submit_setup = st.form_submit_button("Start Prix")

        if submit_setup and st.session_state.selected_players_for_prix:
            st.session_state.current_prix = {
                "name": f"Prix {len(st.session_state.prix_history) + 1}",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "players": st.session_state.selected_players_for_prix,
                "races": [],
                "num_races": num_races,
                # Add new settings to prix data
                "settings": {
                    "cc_class": cc_class,
                    "teams": teams_enabled,
                    "items": items_setting,
                    "com_level": com_level,
                    "com_vehicles": com_vehicles,
                    "courses": course_setting,
                },
            }
            # Clear the selected players list
            st.session_state.selected_players_for_prix = []
            st.success("Prix created! Enter race results below.")
            st.rerun()
        elif submit_setup:
            st.error("Please select at least one player")

    # Race Results Input
    if "current_prix" in st.session_state:
        st.subheader(f"Enter Results for {st.session_state.current_prix['name']}")

        race_num = len(st.session_state.current_prix["races"]) + 1
        if race_num <= st.session_state.current_prix["num_races"]:
            with st.form(f"race_{race_num}"):
                st.write(f"Race {race_num}")

                # Add track selection
                track = st.selectbox("Select Track", options=TRACK_LIST)

                # Create columns for player names and their placements
                col1, col2 = st.columns([2, 1])

                placements = {}
                selected_positions = set()

                # First pass to collect all placements
                with col1:
                    st.write("Player")
                    for player in st.session_state.current_prix["players"]:
                        st.write(player)

                with col2:
                    st.write("Position")
                    for player in st.session_state.current_prix["players"]:
                        position = st.selectbox(
                            f"Position for {player}",
                            options=range(1, 13),
                            key=f"pos_{player}",
                            label_visibility="collapsed",
                        )
                        placements[player] = position
                        selected_positions.add(position)

                submit_race = st.form_submit_button("Submit Race Results")

                if submit_race:
                    # Validate that all positions are unique
                    if len(selected_positions) != len(
                        st.session_state.current_prix["players"]
                    ):
                        st.error("Each player must have a unique position!")
                    else:
                        # Store race results
                        st.session_state.current_prix["races"].append(
                            {
                                "number": race_num,
                                "track": track,
                                "placements": placements,
                            }
                        )
                        st.rerun()

        # Show submit prix button when all races are completed
        if (
            len(st.session_state.current_prix["races"])
            == st.session_state.current_prix["num_races"]
        ):
            if st.button("Submit Prix Results"):
                # Update player stats for all races in the prix
                for race in st.session_state.current_prix["races"]:
                    for player in race["placements"]:
                        st.session_state.players[player]["total_races"] += 1

                # Add to prix history and clean up
                st.session_state.prix_history.append(st.session_state.current_prix)
                del st.session_state.current_prix
                st.success("Prix completed!")
                st.rerun()

        # Add results table below the race input
        if st.session_state.current_prix["races"]:
            st.subheader("Current Prix Results")

            # Define scoring system
            def get_points(position):
                if position == 1:
                    return 15
                elif position == 2:
                    return 12
                elif position == 3:
                    return 10
                else:
                    return 13 - position

            # Create DataFrame with players as rows and races as columns
            results_data = {}
            total_points = {}

            # Initialize dictionaries
            for player in st.session_state.current_prix["players"]:
                results_data[player] = []
                total_points[player] = 0

            # Fill in placements and points for each race
            for race in st.session_state.current_prix["races"]:
                for player in st.session_state.current_prix["players"]:
                    position = race["placements"][player]  # Get position directly
                    points = get_points(position)
                    total_points[player] += points

                    # Format position with proper ordinal suffix
                    if position == 1:
                        suffix = "st"
                    elif position == 2:
                        suffix = "nd"
                    elif position == 3:
                        suffix = "rd"
                    else:
                        suffix = "th"

                    results_data[player].append(f"{position}{suffix} ({points}pts)")

            # Add total points to results data
            for player in results_data:
                results_data[player].append(total_points[player])

            # Create DataFrame
            df_results = pd.DataFrame(
                results_data,
                index=[
                    f"Race {i+1} - {race['track']}"
                    for i, race in enumerate(st.session_state.current_prix["races"])
                ]
                + ["Total Points"],
            ).transpose()

            # Sort DataFrame by total points
            df_results = df_results.sort_values("Total Points", ascending=False)

            # Display the table
            st.dataframe(
                df_results,
                use_container_width=True,
                column_config={
                    col: {"width": 150}
                    for col in df_results.columns[:-1]  # All race columns
                }
                | {
                    "Total Points": {
                        "width": 120,
                        "background": "rgb(220, 220, 220)",
                    }
                },
            )

with tab4:
    st.header("Prix History")

    if st.session_state.prix_history:
        for prix in reversed(st.session_state.prix_history):
            with st.expander(f"{prix['name']} - {prix['date']}"):
                # Display prix settings
                st.subheader("Prix Settings")
                settings = prix["settings"]
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"CC Class: {settings['cc_class']}")
                    st.write(f"Teams: {'Enabled' if settings['teams'] else 'Disabled'}")
                    st.write(f"Items: {settings['items']}")
                with col2:
                    st.write(f"COM Level: {settings['com_level']}")
                    st.write(f"COM Vehicles: {settings['com_vehicles']}")
                    st.write(f"Courses: {settings['courses']}")

                st.divider()

                # Display race results
                for race in prix["races"]:
                    st.write(f"Race {race['number']} - {race['track']}:")
                    for pos, player in enumerate(race["placements"], 1):
                        st.write(f"{pos}. {player}")
                    st.divider()
    else:
        st.info("No prix history available yet. Create a Prix to get started!")
