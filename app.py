import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
from database import get_db_context
from sqlalchemy import func, desc, distinct
from elo import apply_elo_adjustments, calculate_elo_adjustments
from models import Prix, Race, RaceResult, Player, Track, KartCombo

# Initialize session state for storing data
if "prix_history" not in st.session_state:
    st.session_state.prix_history = []

if "players" not in st.session_state:
    st.session_state.players = {}  # {name: {"total_races": 0}}

if "selected_players_for_prix" not in st.session_state:
    st.session_state.selected_players_for_prix = []

if "combo_selections" not in st.session_state:
    st.session_state.combo_selections = {}

if "reset_player_selector" not in st.session_state:
    st.session_state.reset_player_selector = False

# Get track list from database
with get_db_context() as db:
    TRACK_LIST = [track.track_name for track in db.query(Track.track_name).order_by(Track.track_name).all()]


# Add these mappings near the top of the file with other constants
ITEMS_MAPPING = {
    "Normal Items": "normal",
    "No Items": "none",
    "Shells Only": "shells_only",
    "Bananas Only": "bananas_only",
    "Mushrooms Only": "mushrooms_only",
    "Custom": "custom_items",
    "Bob-ombs Only": "bob-ombs_only",
    "Coins Only": "coins_only",
    "Frantic Items": "frantic_items",
}

COM_VEHICLES_MAPPING = {
    "All Vehicles": "all",
    "Karts Only": "karts_only",
    "Bikes Only": "bikes_only"
}

COURSE_SETTING_MAPPING = {
    "Random": "random",
    "Choose": "choose",
    "In Order": "in_order"
}

st.set_page_config(page_title="Race Tracker", page_icon="🏎️", layout="wide")
st.title("🏎️ Mario Kart Tracker")

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
                func.sum(prix_rankings.c.total_races).label('total_races'),
                func.sum(prix_rankings.c.races_won).label('races_won'),
                (func.sum(prix_rankings.c.races_won) / func.sum(prix_rankings.c.total_races)).label('race_win_rate'),
                func.count(distinct(prix_rankings.c.prix_id)).label('total_prixs'),
                func.count(distinct(prix_rankings.c.prix_id)).filter(prix_rankings.c.prix_finish_position == 1).label('prixs_won'),
                (func.count(distinct(prix_rankings.c.prix_id)).filter(prix_rankings.c.prix_finish_position == 1) / func.count(distinct(prix_rankings.c.prix_id))).label('prix_win_rate')
            )
            .group_by(prix_rankings.c.player_nickname, prix_rankings.c.elo_rating)
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
                title='Top Players by ELO Rating',
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
                margin=dict(l=10, r=10, t=40, b=10),
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                title={
                    'text': 'Top Players by ELO Rating',
                    'x': 0.5,
                    'y': 0.95,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
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
                    'Total Prixs': st.column_config.NumberColumn(
                        'Total Prixs',
                        help='Number of prix tournaments completed'
                    ),
                    'Prixs Won': st.column_config.NumberColumn(
                        'Prixs Won',
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
    
    st.header("Track Stats")
    # Track selection dropdown
    with get_db_context() as db:
        available_tracks = [
            track[0] for track in 
            db.query(Track.track_name)
            .distinct()
            .order_by(Track.track_name)
            .all()
        ]
        
        if available_tracks:
            selected_track = st.selectbox(
                "Select a track to view player performance",
                options=available_tracks
            )

            # Get total races for selected track
            track_race_count = (
                db.query(func.count(Race.race_id))
                .join(Track, Race.track_id == Track.track_id)
                .filter(Track.track_name == selected_track)
                .scalar()
            )
            
            # Get player with most wins on this track
            track_winner = (
                db.query(
                    Player.player_nickname,
                    func.count(RaceResult.result_id).label('wins')
                )
                .join(RaceResult, Player.player_id == RaceResult.player_id)
                .join(Race, RaceResult.race_id == Race.race_id)
                .join(Track, Race.track_id == Track.track_id)
                .filter(Track.track_name == selected_track)
                .filter(RaceResult.finish_position == 1)
                .group_by(Player.player_nickname)
                .order_by(desc('wins'))
                .first()
            )

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Total Times Raced",
                    value=track_race_count
                )
            
            with col2:
                if track_winner:
                    st.metric(
                        label="Most Wins 🥇",
                        value=f"{track_winner.player_nickname} ({track_winner.wins})"
                    )
                else:
                    st.metric(
                        label="Most Wins 🥇", 
                        value="No wins recorded"
                    )

            # Get top 10 players by average finish position for selected track
            track_rankings = (
                db.query(
                    Player.player_nickname,
                    func.avg(RaceResult.points_earned).label('avg_points'),
                    func.count(RaceResult.result_id).label('total_races')
                )
                .join(RaceResult, Player.player_id == RaceResult.player_id)
                .join(Race, RaceResult.race_id == Race.race_id)
                .join(Track, Race.track_id == Track.track_id)
                .filter(Track.track_name == selected_track)
                .group_by(Player.player_nickname)
                .having(func.count(RaceResult.result_id) >= 1)
                .order_by(desc('avg_points'))
                .limit(10)
                .all()
            )

            if track_rankings:
                # Convert to DataFrame
                df = pd.DataFrame(
                    track_rankings,
                    columns=['Player', 'Average Points', 'Total Races']
                )
                df['Average Points'] = df['Average Points'].round(2)

                # Create horizontal bar chart for track rankings
                fig = px.bar(
                    df,
                    x='Average Points',
                    y='Player',
                    orientation='h',
                    text='Average Points',
                )
                
                # Customize the bars
                colors = ['gold', 'silver', '#CD7F32'] + ['#E8E8E8'] * 7
                
                # Update traces
                fig.update_traces(
                    marker_color=colors,
                    textposition='outside',
                    texttemplate='%{x:.2f}',
                    cliponaxis=False
                )
                
                # Customize layout
                fig.update_layout(
                    xaxis_range=[0, 15],
                    xaxis_title="Average Points per Race",
                    yaxis_title="",
                    yaxis=dict(
                        autorange="reversed",
                        tickfont=dict(size=14)
                    ),
                    margin=dict(l=10, r=100, t=40, b=10),
                    height=max(400, len(df) * 40),
                    uniformtext=dict(
                        mode='hide',
                        minsize=10
                    ),
                    title={
                        'text': f'Top Players on {selected_track}',
                        'x': 0.5,
                        'y': 0.95,
                        'xanchor': 'center',
                        'yanchor': 'top'
                    }
                )
                
                # Add gridlines
                fig.update_xaxes(
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='LightGray',
                    range=[0, 16]  # Give extra space for labels
                )
                fig.update_yaxes(showgrid=False)
                
                # Display chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No race data available for {selected_track}")
        else:
            st.info("No track data available yet. Create a Prix to get started!")

    st.subheader("Track Distribution")

    # Query database for track distribution
    with get_db_context() as db:
        track_counts = (
            db.query(
                Track.track_name,
                func.count(Race.race_id).label('number_of_races')
            )
            .join(Race, Race.track_id == Track.track_id, isouter=True)
            .group_by(Track.track_name)
            .order_by(desc('number_of_races'))
            .all()
        )
        
        if track_counts:
            # Convert to DataFrame
            df = pd.DataFrame(track_counts, columns=['Track', 'Races'])
            
            # Calculate expected value if tracks were chosen equally
            total_races = df['Races'].sum()
            expected_races = total_races / len(TRACK_LIST)
            
            # Add missing tracks with 0 races
            existing_tracks = df['Track'].tolist()
            missing_tracks = [track for track in TRACK_LIST if track not in existing_tracks]
            if missing_tracks:
                df = pd.concat([
                    df,
                    pd.DataFrame({'Track': missing_tracks, 'Races': 0})
                ])
            
            # Create horizontal bar chart
            fig = px.bar(
                df,
                x='Races',
                y='Track',
                orientation='h',
                text='Races'
            )
            
            # Add expected value line
            fig.add_vline(
                x=expected_races,
                line_dash="dash",
                line_color="rgba(255, 0, 0, 0.5)",
                annotation_text="Expected",
                annotation_position="top"
            )
            
            # Update layout with improved label visibility
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                showlegend=False,
                margin=dict(l=10, r=10, t=40, b=10),
                height=max(400, len(df) * 25),  # Dynamic height based on number of tracks
                uniformtext=dict(mode='hide', minsize=8),  # Ensure consistent text size
            )
            
            # Update traces to show labels
            fig.update_traces(
                textposition='outside',
                texttemplate='%{x}',  # Show the number of races
                cliponaxis=False  # Prevent labels from being cut off
            )
            
            # Update axes
            fig.update_xaxes(
                title='Races',
                showgrid=True,
                gridwidth=1,
                gridcolor='LightGray'
            )
            fig.update_yaxes(
                title='',
                showgrid=False,
                tickfont=dict(size=12)  # Adjust track name font size
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No race data available yet to show track distribution.")

with tab2:
    st.header("Player Profiles")

    # Add player selection dropdown
    with get_db_context() as db:
        # Get all unique player nicknames
        players = db.query(Player.player_nickname).distinct().order_by(Player.player_nickname).all()
        player_list = [p[0] for p in players]
        
        col1, _ = st.columns([1, 3])  # Create columns to constrain width
        with col1:
            selected_player = st.selectbox(
                "Select Player",
                player_list,
                key="player_profile_select",
                label_visibility="visible",
                help="Choose a player to view their profile"
            )        
        
        if selected_player:
            # Prix Statistics
            all_prix_history = (
                db.query(
                    Prix.prix_id,
                    Player.player_nickname,
                    func.sum(RaceResult.points_earned).label('total_points'),
                    func.rank().over(
                        partition_by=Prix.prix_id,
                        order_by=func.sum(RaceResult.points_earned).desc()
                        ).label('finish_position')
                )
                .join(Race, Race.prix_id == Prix.prix_id)
                .join(RaceResult, RaceResult.race_id == Race.race_id)
                .join(Player, Player.player_id == RaceResult.player_id)
                .group_by(Prix.prix_id, Player.player_nickname)
                .subquery()
            )

            # Get total prix and prix wins
            prix_stats = (
                db.query(
                    func.count(distinct(all_prix_history.c.prix_id)).label('total_prix'),
                    func.count(distinct(all_prix_history.c.prix_id)).filter(
                        all_prix_history.c.finish_position == 1
                    ).label('prix_wins'),
                    func.avg(all_prix_history.c.finish_position).label('average_finish_position')
                )
                .filter(all_prix_history.c.player_nickname == selected_player)
                .first()
            )

            # Race Statistics 
            race_stats = (
                db.query(
                    func.count(Race.race_id).label('total_races'),
                    func.count(Race.race_id).filter(
                        RaceResult.finish_position == 1
                    ).label('race_wins'),
                    func.avg(RaceResult.points_earned).label('average_points')
                )
                .join(RaceResult, RaceResult.race_id == Race.race_id)
                .join(Player, Player.player_id == RaceResult.player_id)
                .filter(Player.player_nickname == selected_player)
                .first()
            )

            # Display Prix Stats
            if prix_stats.total_prix > 0:
                prix_col1, prix_col2, prix_col3, prix_col4 = st.columns(4)
                with prix_col1:
                    st.metric("Prixs Won", prix_stats.prix_wins)
                with prix_col2:
                    st.metric("Total Prixs", prix_stats.total_prix)
                with prix_col3:
                    prix_win_rate = (prix_stats.prix_wins / prix_stats.total_prix * 100) if prix_stats.total_prix > 0 else 0
                    st.metric("Prix Win Rate", f"{prix_win_rate:.1f}%")
                with prix_col4:
                    st.metric("Average Finish Position", f"{prix_stats.average_finish_position:.1f}")
            else:
                st.info("No prix data available yet")

            # Display Race Stats
            if race_stats.total_races > 0:
                race_col1, race_col2, race_col3, race_col4 = st.columns(4)
                with race_col1:
                    st.metric("Races Won", race_stats.race_wins)
                with race_col2:
                    st.metric("Total Races", race_stats.total_races)
                with race_col3:
                    race_win_rate = (race_stats.race_wins / race_stats.total_races * 100) if race_stats.total_races > 0 else 0
                    st.metric("Race Win Rate", f"{race_win_rate:.1f}%")
                with race_col4:
                    st.metric("Average Points per Race", f"{race_stats.average_points:.1f}")
            else:
                st.info("No race data available yet")

            st.subheader('Favourite Kart Combo')
            favkart_combo = (
                db.query(
                    KartCombo.character_name,
                    KartCombo.vehicle_name,
                    KartCombo.tire_name,
                    KartCombo.glider_name,
                    func.count(distinct(Prix.prix_id)).label('total_prixs')
                )
                .join(Race, Race.prix_id == Prix.prix_id)
                .join(RaceResult, RaceResult.race_id == Race.race_id)
                .join(Player, Player.player_id == RaceResult.player_id)
                .join(KartCombo, KartCombo.combo_id == RaceResult.combo_id)
                .filter(Player.player_nickname == selected_player)
                .group_by(KartCombo.character_name, KartCombo.vehicle_name, KartCombo.tire_name, KartCombo.glider_name)
                .order_by(desc(func.count(distinct(Prix.prix_id))))
                .first()
            )

            if favkart_combo:
                kart_col1, kart_col2, kart_col3, kart_col4= st.columns(4)
                
                # Load and resize images to consistent height of 100px while maintaining aspect ratio
                from PIL import Image
                
                def resize_image(image_path, target_height=100):
                    img = Image.open(image_path)
                    aspect_ratio = img.width / img.height
                    new_width = int(target_height * aspect_ratio)
                    return img.resize((new_width, target_height))
                
                with kart_col1:
                    img = resize_image("images/characters/test_character.png")
                    st.image(img, caption=favkart_combo.character_name)
                
                with kart_col2:
                    img = resize_image("images/vehicles/test_vehicle.png")
                    st.image(img, caption=favkart_combo.vehicle_name)
                
                with kart_col3:
                    img = resize_image("images/tires/test_tires.png")
                    st.image(img, caption=favkart_combo.tire_name)
                
                with kart_col4:
                    img = resize_image("images/gliders/test_glider.png")
                    st.image(img, caption=favkart_combo.glider_name)
            else:
                st.info("No kart combo data available yet")

            st.subheader(f"Top 10 tracks by avg points per race")
            
            st.subheader(f"Track specific stats")
            # Create track selection dropdown
            selected_track = st.selectbox(
                "Select Track",
                options=TRACK_LIST,
                key="track_stats_selector"
            )
            
            st.subheader(f"Prix History for {selected_player}")

            # Get all prix history for selected player
            all_prix_history = (
                db.query(
                    Prix.prix_id,
                    Prix.date_played,
                    Player.player_nickname,
                    Prix.number_of_players.label('num_players'),
                    Prix.race_count.label('num_races'),
                    func.sum(RaceResult.points_earned).label('total_points'),
                    func.rank().over(
                        partition_by=Prix.prix_id,
                        order_by=func.sum(RaceResult.points_earned).desc()
                        ).label('finish_position')
                )
                .join(Race, Race.prix_id == Prix.prix_id)
                .join(RaceResult, RaceResult.race_id == Race.race_id)
                .join(Player, Player.player_id == RaceResult.player_id)
                .group_by(Prix.prix_id, Prix.date_played, Player.player_nickname)
                .subquery()
            )

            # Get prix history for selected player 
            prix_history_filtered = (
                db.query(
                    all_prix_history.c.prix_id,
                    all_prix_history.c.date_played,
                    all_prix_history.c.num_players,
                    all_prix_history.c.num_races,
                    all_prix_history.c.total_points,
                    all_prix_history.c.finish_position
                )
                .filter(all_prix_history.c.player_nickname == selected_player)
                .order_by(all_prix_history.c.date_played.desc())
                .all()
            )
            
            if prix_history_filtered:
                for prix in prix_history_filtered:
                    # Create expander for each prix
                    with st.expander(
                        f"{prix.date_played.strftime('%Y-%m-%d')} - {prix.num_races} Races - "
                        f"{prix.finish_position}{['st','nd','rd','th'][min(int(prix.finish_position)-1,3)]} Place"
                    ):
                        # Get detailed race results for this prix
                        race_details = (
                            db.query(
                                Race.race_number,
                                Track.track_name,
                                RaceResult.finish_position,
                                RaceResult.points_earned
                            )
                            .join(Track, Race.track_id == Track.track_id)
                            .join(RaceResult, RaceResult.race_id == Race.race_id)
                            .join(Player, RaceResult.player_id == Player.player_id)
                            .filter(
                                Race.prix_id == prix.prix_id,
                                Player.player_nickname == selected_player
                            )
                            .order_by(Race.race_number)
                            .all()
                        )
                        
                        # Create DataFrame for race details
                        races_df = pd.DataFrame([
                            {
                                'Race': f"Race {race.race_number}",
                                'Track': race.track_name,
                                'Position': f"{race.finish_position}{['st','nd','rd','th'][min(race.finish_position-1,3)]}",
                                'Points': race.points_earned
                            }
                            for race in race_details
                        ])
                        
                        # Show prix summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Points", prix.total_points)
                        with col2:
                            st.metric("Number of Races", prix.num_races)
                        with col3:
                            st.metric("Total Players", prix.num_players)
                        
                        # Show race details table
                        st.dataframe(
                            races_df,
                            column_config={
                                'Race': st.column_config.TextColumn(
                                    'Race',
                                    help='Race number in the prix'
                                ),
                                'Track': st.column_config.TextColumn(
                                    'Track',
                                    help='Track name'
                                ),
                                'Position': st.column_config.TextColumn(
                                    'Position',
                                    help='Finish position'
                                ),
                                'Points': st.column_config.NumberColumn(
                                    'Points',
                                    help='Points earned in this race'
                                )
                            },
                            hide_index=True,
                            use_container_width=True
                        )
            else:
                st.info(f"No prix history found for {selected_player}")

with tab3:
    st.header("Create Prix")

    # Player selection section (outside the form)
    st.subheader("Select Players")
    
    with get_db_context() as db:
        # Get players sorted by their most recent race
        players = (
            db.query(Player.player_nickname, func.max(Race.created_at).label('last_race'))
            .outerjoin(RaceResult, Player.player_id == RaceResult.player_id)
            .outerjoin(Race, RaceResult.race_id == Race.race_id)
            .group_by(Player.player_nickname)
            .order_by(func.max(Race.created_at).desc().nulls_last(), Player.player_nickname)
            .all()
        )
    existing_players = [
        p.player_nickname
        for p in players
        if p.player_nickname not in st.session_state.selected_players_for_prix
    ]
    player_options = existing_players + ["+ Add New Player"]

    if st.session_state.reset_player_selector:
        st.session_state.player_selector = player_options[0]
        st.session_state.reset_player_selector = False

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
            
            # Check for existing player immediately when nickname is entered
            if nickname:
                with get_db_context() as db:
                    existing_player = db.query(Player).filter(Player.player_nickname == nickname).first()
                    if existing_player:
                        st.error(f"Player with nickname '{nickname}' already exists!")
                        player_to_add = None
                    else:
                        player_to_add = nickname
            else:
                player_to_add = None

        else:
            player_to_add = selected_option

        if player_to_add:  # Only show kart selection if we have a valid player
            # Get player's most recent kart combo
            recent_character = None
            recent_vehicle = None
            recent_tire = None
            recent_glider = None
            
            with get_db_context() as db:
                most_recent_combo = (
                    db.query(KartCombo)
                    .join(RaceResult, RaceResult.combo_id == KartCombo.combo_id)
                    .join(Race, Race.race_id == RaceResult.race_id)
                    .join(Player, Player.player_id == RaceResult.player_id)
                    .filter(Player.player_nickname == player_to_add)
                    .order_by(Race.created_at.desc())
                    .first()
                )
                
                if most_recent_combo:
                    recent_character = most_recent_combo.character_name
                    recent_vehicle = most_recent_combo.vehicle_name
                    recent_tire = most_recent_combo.tire_name
                    recent_glider = most_recent_combo.glider_name

            # Vehicle customization for all players
            st.write("Kart Combo")
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
                    index=([
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
                    ].index(recent_character) if recent_character else 0)
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
                        "Tri-Speeder", # 21 widmer go to the first parking lot two p signs first one in. go up to concierge 
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
                    index=([
                        "Standard Kart",
                        "Pipe Frame",
                        "Mach 8",
                        "Steel Driver",
                        "Cat Cruiser",
                        "Circuit Special",
                        "Tri-Speeder", # 21 widmer go to the first parking lot two p signs first one in. go up to concierge 
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
                    ].index(recent_vehicle) if recent_vehicle else 0)
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
                    index=([
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
                    ].index(recent_tire) if recent_tire else 0)
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
                        "Paper Glider",
                    ],
                    index=([
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
                        "Paper Glider",
                    ].index(recent_glider) if recent_glider else 0)
                )

            if st.button("Add to Prix"):
                # If this is a new player, add them to the database
                if selected_option == "+ Add New Player":
                    # Create new player
                    new_player = Player(
                        player_first_name=first_name,
                        player_last_name=last_name,
                        player_nickname=nickname,
                    )
                    with get_db_context() as db:
                        db.add(new_player)
                        db.commit()
                
                st.session_state.combo_selections[player_to_add] = {
                    "character": character,
                    "kart": kart,
                    "wheels": wheels,
                    "glider": glider,
                }
                # Add to selected players
                st.session_state.selected_players_for_prix.append(player_to_add)
                
                # Set flag to reset selector on next rerun
                st.session_state.reset_player_selector = True
                st.rerun()

    # Display selected players with remove buttons
    if st.session_state.selected_players_for_prix:
        st.write("Selected Players:")
        for idx, player in enumerate(st.session_state.selected_players_for_prix):
            col1, col2 = st.columns([3, 1])
            with col1:
                vehicle = st.session_state.combo_selections[player]
                st.write(
                    f"{idx + 1}. {player} "
                    f"({vehicle['character']}, {vehicle['kart']}, "
                    f"{vehicle['wheels']}, {vehicle['glider']})"
                )
            with col2:
                if st.button(f"Remove {player}", key=f"remove_{player}"):
                    st.session_state.selected_players_for_prix.remove(player)
                    del st.session_state.combo_selections[player]
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
                    "Bob-ombs Only",
                    "Coins Only",
                    "Frantic Items"
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
                options=["All Vehicles", "Karts Only", "Bikes Only"],
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
            options=[4, 6, 8, 12, 16, 24, 48, 64],
            index=0,
        )

        submit_setup = st.form_submit_button("Start Prix")

        if submit_setup and st.session_state.selected_players_for_prix:
            # Create new prix in database
            with get_db_context() as db:
                new_prix = Prix(
                    number_of_players=len(st.session_state.selected_players_for_prix),
                    race_count=num_races,
                    cc_class=150 if cc_class == "Mirror" else int(cc_class.replace("cc", "")),
                    is_teams_mode=teams_enabled,
                    items_setting=ITEMS_MAPPING[items_setting],
                    com_level=com_level.lower(),
                    com_vehicles=COM_VEHICLES_MAPPING[com_vehicles],
                    courses_setting=COURSE_SETTING_MAPPING[course_setting],
                    prix_type="vs_race",
                    is_mirror_mode=cc_class == "Mirror",
                )
                db.add(new_prix)
                db.commit()
                
                # Store prix_id in session state for later use
                st.session_state.current_prix = {
                    "prix_id": new_prix.prix_id,
                    "players": st.session_state.selected_players_for_prix,
                    "races": [],
                    "num_races": num_races
                }
                
                # Store kart combo selections in database
                for player_nickname in st.session_state.combo_selections:
                    combo = st.session_state.combo_selections[player_nickname]
                    player = db.query(Player).filter(Player.player_nickname == player_nickname).first()
                    
                    # Check if combo already exists
                    existing_combo = db.query(KartCombo).filter(
                        KartCombo.character_name == combo["character"],
                        KartCombo.vehicle_name == combo["kart"], 
                        KartCombo.tire_name == combo["wheels"],
                        KartCombo.glider_name == combo["glider"]
                    ).first()

                    if existing_combo:
                        kart_combo = existing_combo
                    else:
                        kart_combo = KartCombo(
                            character_name=combo["character"],
                            vehicle_name=combo["kart"],
                            tire_name=combo["wheels"],
                            glider_name=combo["glider"]
                        )
                        db.add(kart_combo)
                        db.commit()
                    
                    # Store the combo_id in session state for later use with race results
                    if "combo_ids" not in st.session_state:
                        st.session_state.combo_ids = {}
                    st.session_state.combo_ids[player_nickname] = kart_combo.combo_id

            # Clear the selected players list
            st.session_state.selected_players_for_prix = []
            st.success("Prix created! Enter race results below.")
            st.rerun()
        elif submit_setup:
            st.error("Please select at least one player")

    # Race Results Input
    if "current_prix" in st.session_state:
        st.subheader(f"Enter Results")

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
                    if len(selected_positions) != len(st.session_state.current_prix["players"]):
                        st.error("Each player must have a unique position!")
                    else:
                        with get_db_context() as db:
                            # Get or create track
                            db_track = db.query(Track).filter(Track.track_name == track).first()

                            # Create new race
                            new_race = Race(
                                prix_id=st.session_state.current_prix["prix_id"],
                                track_id=db_track.track_id,
                                race_number=race_num
                            )
                            db.add(new_race)
                            db.commit()

                            # Add race results for each player
                            for player_nickname, position in placements.items():
                                # Get player
                                player = db.query(Player).filter(Player.player_nickname == player_nickname).first()
                                
                                # Calculate points based on position
                                points = 15 if position == 1 else (
                                    12 if position == 2 else (
                                        10 if position == 3 else (13 - position)
                                    )
                                )

                                # Create race result
                                race_result = RaceResult(
                                    race_id=new_race.race_id,
                                    player_id=player.player_id,
                                    combo_id=st.session_state.combo_ids[player_nickname],
                                    finish_position=position,
                                    points_earned=points
                                )
                                db.add(race_result)
                            db.commit()

                        # Store race results in session state (for display purposes)
                        st.session_state.current_prix["races"].append({
                            "number": race_num,
                            "track": track,
                            "placements": placements,
                        })
                        st.rerun()

        # Show submit prix button when all races are completed
        if (
            len(st.session_state.current_prix["races"])
            == st.session_state.current_prix["num_races"]
        ):
            if st.button("Submit Prix Results"):
                with get_db_context() as db:
                    # Get final standings for this prix
                    prix_results = (
                        db.query(
                            Player.player_id,
                            Player.player_nickname,
                            Player.elo_rating,
                            func.sum(RaceResult.points_earned).label('total_points')
                        )
                        .join(RaceResult, Player.player_id == RaceResult.player_id)
                        .join(Race, RaceResult.race_id == Race.race_id)
                        .filter(Race.prix_id == st.session_state.current_prix["prix_id"])
                        .group_by(Player.player_id, Player.player_nickname, Player.elo_rating)
                        .order_by(desc('total_points'))
                        .all()
                    )

                    # Calculate new ELO ratings
                    placements = [(result.player_nickname, idx + 1) for idx, result in enumerate(prix_results)]
                    current_ratings = {result.player_nickname: result.elo_rating for result in prix_results}
                    
                    # Calculate ELO changes
                    elo_adjustments = calculate_elo_adjustments(placements, current_ratings)
                    updated_ratings = apply_elo_adjustments(current_ratings, elo_adjustments)
                    
                    # Update player ELO ratings
                    for player_nickname, new_elo in updated_ratings.items():
                        db.query(Player).filter(Player.player_nickname == player_nickname).update(
                            {'elo_rating': new_elo}
                        )
                    db.commit()

                # Clean up session state
                del st.session_state.current_prix
                st.success("Prix completed and ELO ratings updated!")
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
    
    with get_db_context() as db:
        # Get all prix with their winners
        all_prix_history = (
            db.query(
                Prix.prix_id,
                Prix.date_played,
                Player.player_nickname,
                Prix.number_of_players.label('num_players'),
                Prix.race_count.label('num_races'),
                func.sum(RaceResult.points_earned).label('total_points'),
                func.rank().over(
                    partition_by=Prix.prix_id,
                    order_by=func.sum(RaceResult.points_earned).desc()
                    ).label('finish_position')
            )
            .join(Race, Race.prix_id == Prix.prix_id)
            .join(RaceResult, RaceResult.race_id == Race.race_id)
            .join(Player, Player.player_id == RaceResult.player_id)
            .group_by(Prix.prix_id, Prix.date_played, Player.player_nickname)
            .subquery()
        )

        prix_list = (
            db.query(
                all_prix_history.c.prix_id,
                all_prix_history.c.date_played,
                all_prix_history.c.num_players,
                all_prix_history.c.num_races,
                all_prix_history.c.total_points.label('winning_points'),
                func.string_agg(all_prix_history.c.player_nickname, ' and ').label('winners')
            )
            .filter(all_prix_history.c.finish_position == 1)
            .group_by(all_prix_history.c.prix_id, all_prix_history.c.date_played, all_prix_history.c.num_players, all_prix_history.c.num_races, all_prix_history.c.total_points)
            .order_by(all_prix_history.c.date_played.desc())
            .all()
        )

        if prix_list:
            for prix in prix_list:
                # Create expander for each prix
                with st.expander(
                    f"{prix.date_played.strftime('%Y-%m-%d')} - {prix.num_races} Races - "
                    f"Winner: {prix.winners} ({prix.winning_points} pts)"
                ):
                    # Get all race results for this prix
                    race_results = (
                        db.query(
                            Player.player_nickname,
                            Race.race_number,
                            Track.track_name,
                            RaceResult.finish_position,
                            RaceResult.points_earned,
                            func.sum(RaceResult.points_earned).over(
                                partition_by=Player.player_id
                            ).label('total_points')
                        )
                        .join(RaceResult, Player.player_id == RaceResult.player_id)
                        .join(Race, RaceResult.race_id == Race.race_id)
                        .join(Track, Race.track_id == Track.track_id)
                        .filter(Race.prix_id == prix.prix_id)
                        .subquery()
                    )

                    race_results_ranked = (
                        db.query(
                            race_results.c.player_nickname,
                            race_results.c.race_number,
                            race_results.c.track_name,
                            race_results.c.points_earned,
                            race_results.c.finish_position,
                            race_results.c.total_points,
                            func.dense_rank().over(
                                order_by=race_results.c.total_points.desc()
                            ).label('prix_position')
                        )
                        .order_by(
                            race_results.c.total_points.desc(),
                            race_results.c.race_number
                        )
                        .all()
                    )

                    # Create DataFrame
                    data = {}
                    for r in race_results_ranked:
                        if r.player_nickname not in data:
                            data[r.player_nickname] = {
                                'Position': f"{r.prix_position}",
                                'Total': r.total_points
                            }
                        race_key = f"Race {r.race_number} ({r.track_name})"
                        data[r.player_nickname][race_key] = f"{r.points_earned} ({r.finish_position})"

                    # Create DataFrame with player as index
                    df = pd.DataFrame.from_dict(data, orient='index')
                    
                    # Reset index to make player a column
                    df = df.reset_index().rename(columns={'index': 'Player'})
                    
                    # Ensure races are in correct order
                    race_cols = [col for col in df.columns if col.startswith('Race')]
                    race_cols.sort(key=lambda x: int(x.split()[1]))
                    
                    # Reorder columns: Position, Player, Races, Total
                    df = df[['Position', 'Player'] + race_cols + ['Total']]

                    # Display the table
                    st.dataframe(
                        df,
                        column_config={
                            'Position': st.column_config.TextColumn(
                                'Position',
                                help='Final position in the prix'
                            ),
                            'Player': st.column_config.TextColumn(
                                'Player',
                                help='Player nickname'
                            ),
                            'Total': st.column_config.NumberColumn(
                                'Total Points',
                                help='Total points earned'
                            ),
                            **{
                                col: st.column_config.TextColumn(
                                    col,
                                    help='Points earned (Finish position)'
                                )
                                for col in race_cols
                            }
                        },
                        use_container_width=True,
                        hide_index=True  # Hide the index since we now have position column
                    )
        else:
            st.info("No prix history available yet. Create a Prix to get started!")