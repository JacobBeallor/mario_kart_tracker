import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
from database import get_db_context
from sqlalchemy import func, desc, distinct
from models import Prix, Race, RaceResult, Player

# Initialize session state for storing data
if "prix_history" not in st.session_state:
    st.session_state.prix_history = []

if "players" not in st.session_state:
    st.session_state.players = {}  # {name: {"total_races": 0}}

if "selected_players_for_prix" not in st.session_state:
    st.session_state.selected_players_for_prix = []

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
    st.header("Player Leaderboard")

    # Fetch player rankings from database
    with get_db_context() as db:
        # Get player rankings sorted by ELO rating
        prix_results = (
            db.query(
                Race.prix_id,
                Player.player_nickname,
                Player.elo_rating,
                func.sum(RaceResult.points_earned).label('total_points'),
                func.count(distinct(Race.race_id)).label('total_races'),
                func.count(distinct(Race.race_id)).filter(RaceResult.finish_position == 1).label('races_won')
            )
            .join(RaceResult, Player.player_id == RaceResult.player_id)
            .join(Race, RaceResult.race_id == Race.race_id)
            .group_by(Race.prix_id, Player.player_nickname, Player.elo_rating)
            .subquery()
        )

        prix_rankings = (
            db.query(
                prix_results.c.prix_id,
                prix_results.c.player_nickname,
                prix_results.c.elo_rating,
                prix_results.c.total_races,
                prix_results.c.races_won,
                func.rank().over(
                    partition_by=prix_results.c.prix_id,
                    order_by=prix_results.c.total_points.desc()
                ).label('prix_finish_position')
            )
            .subquery()
        )

        rankings = (
            db.query(
                prix_rankings.c.player_nickname,
                prix_rankings.c.elo_rating,
                prix_rankings.c.total_races,
                prix_rankings.c.races_won,
                (prix_rankings.c.races_won / prix_rankings.c.total_races).label('race_win_rate'),
                func.count(distinct(prix_rankings.c.prix_id)).label('total_prixs'),
                func.count(distinct(prix_rankings.c.prix_id)).filter(prix_rankings.c.prix_finish_position == 1).label('prixs_won'),
                (func.count(distinct(prix_rankings.c.prix_id)).filter(prix_rankings.c.prix_finish_position == 1) / func.count(distinct(prix_rankings.c.prix_id))).label('prix_win_rate')
            )
            .group_by(prix_rankings.c.player_nickname, prix_rankings.c.elo_rating, prix_rankings.c.total_races, prix_rankings.c.races_won)
            .order_by(prix_rankings.c.elo_rating.desc())
            .all()
        )

        if rankings:
            # Convert to DataFrame for easier manipulation
            standings_df = pd.DataFrame([
                {
                    'Player': r.player_nickname,
                    'ELO Rating': float(r.elo_rating),
                    'Total Races': int(r.total_races)
                }
                for r in rankings
            ])

            # Get top 10 players
            top_10 = standings_df.head(10)

            # Create horizontal bar chart
            fig = px.bar(
                top_10,
                x='ELO Rating',
                y='Player',
                orientation='h',
                title='Top 10 Players by ELO Rating',
            )

            # Customize the bars
            colors = ['gold', 'silver', '#CD7F32'] + ['#E8E8E8'] * 7  # Gold, Silver, Bronze + Gray for rest
            medal_emojis = ['🥇', '🥈', '🥉']

            # Update bar colors and add ELO rating labels
            fig.update_traces(
                marker_color=colors,
                textposition='outside',
                texttemplate='%{x:.0f}',  # Show ELO rating
                textfont=dict(size=14)
            )

            # Customize y-axis labels (player names) with medals for top 3
            fig.update_layout(
                yaxis=dict(
                    ticktext=[
                        f"{medal_emojis[i]} {player}" if i < 3 else player
                        for i, player in enumerate(top_10['Player'])
                    ],
                    tickvals=list(range(len(top_10))),
                    autorange="reversed",  # Put highest rated player at top
                    tickfont=dict(size=16)  # Make y-axis labels larger
                ),
                xaxis_title="ELO Rating",
                yaxis_title="",
                title_x=0.5,
                title_font_size=20,
                height=400,
                margin=dict(l=10, r=10, t=40, b=10),
                plot_bgcolor='rgba(0,0,0,0)',
            )

            # Add gridlines
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
            fig.update_yaxes(showgrid=False)

            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

            # Create detailed standings table
            table_data = pd.DataFrame([
                {
                    'Player': r.player_nickname,
                    'ELO Rating': int(r.elo_rating),
                    'Total Races': int(r.total_races),
                    'Races Won': int(r.races_won),
                    'Win Rate': f"{float(r.race_win_rate):.1%}",
                    'Total Prix': int(r.total_prixs),
                    'Prix Won': int(r.prixs_won),
                    'Prix Win Rate': f"{float(r.prix_win_rate):.1%}"
                }
                for r in rankings
            ])
            
            # Add ranking column
            table_data.index = range(1, len(table_data) + 1)
            table_data.index.name = 'Rank'
            
            # Display the table
            st.dataframe(
                table_data,
                use_container_width=True,
                column_config={
                    'ELO Rating': st.column_config.NumberColumn(
                        'ELO Rating',
                        help='Player\'s current ELO rating'
                    ),
                    'Total Races': st.column_config.NumberColumn(
                        'Total Races',
                        help='Total number of races completed'
                    ),
                    'Races Won': st.column_config.NumberColumn(
                        'Races Won',
                        help='Number of races finished in 1st place'
                    ),
                    'Win Rate': st.column_config.TextColumn(
                        'Win Rate',
                        help='Percentage of races won'
                    ),
                    'Total Prix': st.column_config.NumberColumn(
                        'Total Prix',
                        help='Number of prix tournaments completed'
                    ),
                    'Prix Won': st.column_config.NumberColumn(
                        'Prix Won',
                        help='Number of prix tournaments won'
                    ),
                    'Prix Win Rate': st.column_config.TextColumn(
                        'Prix Win Rate',
                        help='Percentage of prix tournaments won'
                    )
                },
                hide_index=False
            )
        else:
            st.info("No race data available yet. Create a Prix to get started!")

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
            new_player = st.text_input("Enter New Player Name")
            player_to_add = new_player if new_player.strip() else None
        else:
            player_to_add = selected_option

        if st.button("Add to Prix"):
            if player_to_add:
                # Initialize new player if needed
                if player_to_add not in st.session_state.players:
                    st.session_state.players[player_to_add] = {
                        "total_races": 0,
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
                st.write(f"{idx + 1}. {player}")
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
