import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import base64
import matplotlib.pyplot as plt
from io import BytesIO

# Set up credentials
client_id = '15622248357f489e87796f8c9dabe1d1'  # replace with your Spotify client ID
client_secret = 'c34328e2ed554c81b35350e5863f124d'  # replace with your Spotify client secret

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to fetch song or playlist information
def get_info(url):
    try:
        if 'track' in url:
            # Handle individual track URL
            track_id = url.split('/')[-1].split('?')[0]
            track_info = sp.track(track_id)

            # Extract track details
            song_details = {
                'Track Name': track_info.get('name', 'N/A'),
                'Artist': track_info['artists'][0].get('name', 'N/A') if track_info.get('artists') else 'N/A',
                'Album': track_info['album'].get('name', 'N/A'),
                'Release Date': track_info['album'].get('release_date', 'N/A'),
                'Track Popularity': track_info.get('popularity', 'N/A'),
                'Track URL': track_info['external_urls'].get('spotify', 'N/A'),
                'Track Duration': f"{track_info['duration_ms'] / 1000:.2f} seconds" if track_info.get('duration_ms') else 'N/A',
            }

            # Optional: Fetch artist's genre
            artist_id = track_info['artists'][0].get('id', None)
            if artist_id:
                artist_info = sp.artist(artist_id)
                artist_genres = artist_info.get('genres', [])
                song_details['Artist Genre'] = ', '.join(artist_genres)
            else:
                song_details['Artist Genre'] = 'N/A'

            return song_details

        elif 'playlist' in url:
            # Handle playlist URL with pagination
            playlist_id = url.split('/')[-1].split('?')[0]
            playlist_details = []
            results = sp.playlist_tracks(playlist_id)

            # Add first batch of tracks
            for item in results['items']:
                track = item.get('track', {})
                song_details = {
                    'Track Name': track.get('name', 'N/A'),
                    'Artist': track['artists'][0].get('name', 'N/A') if track.get('artists') else 'N/A',
                    'Album': track['album'].get('name', 'N/A'),
                    'Track URL': track['external_urls'].get('spotify', 'N/A'),
                    'Release Date': track['album'].get('release_date', 'N/A'),
                    'Track Popularity': track.get('popularity', 'N/A'),
                    'Track Duration': f"{track['duration_ms'] / 1000:.2f} seconds" if track.get('duration_ms') else 'N/A',
                }
                playlist_details.append(song_details)

            # Paginate through the rest of the tracks
            while results['next']:
                results = sp.next(results)
                for item in results['items']:
                    track = item.get('track', {})
                    song_details = {
                        'Track Name': track.get('name', 'N/A'),
                        'Artist': track['artists'][0].get('name', 'N/A') if track.get('artists') else 'N/A',
                        'Album': track['album'].get('name', 'N/A'),
                        'Track URL': track['external_urls'].get('spotify', 'N/A'),
                        'Release Date': track['album'].get('release_date', 'N/A'),
                        'Track Popularity': track.get('popularity', 'N/A'),
                        'Track Duration': f"{track['duration_ms'] / 1000:.2f} seconds" if track.get('duration_ms') else 'N/A',
                    }
                    playlist_details.append(song_details)

            return playlist_details

        else:
            return None
    except spotipy.exceptions.SpotifyException as e:
        st.error("Spotify API Error: Ensure your credentials and URL are valid.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# Function to add background image using base64 encoding
def add_bg_from_local(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
        }}
        .stApp * {{
            color: black !important;  /* Set all font colors to dark black */
        }}
        .stButton > button {{
            display: block;
            margin: 0 auto;  /* Center the button horizontally */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Plot pie chart for popularity by artist
def plot_pie_chart_by_artist(data):
    # Group by Artist and sum popularity values
    artist_popularity = data.groupby('Artist')['Track Popularity'].mean()

    # Plot the pie chart
    artist_popularity.plot(kind='pie', autopct='%1.1f%%', startangle=90, figsize=(6, 6), colors=['#ff9999','#66b3ff','#99ff99','#ffcc99'])
    plt.title('Artist-Based Popularity Distribution')
    plt.tight_layout()
    st.pyplot(plt)

# Streamlit App
st.set_page_config(page_title="Spotify", page_icon="icons8-headphones-64.png")
st.title('Spotify Track/Playlist Info Finder')

# Add the background image (use the path to your image)
add_bg_from_local("headphone-3661771.jpg")  # Adjust the path if needed

# Input field for Spotify track or playlist URL
url = st.text_input("Enter Spotify Track or Playlist URL:")

# Buttons for actions
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    explore_button = st.button('Explore Pie Chart')
with col2:
    get_info_button = st.button('Get Info')
with col3:
    download_button = st.button('Download CSV & Excel')

# Action on explore button click
if explore_button:
    st.subheader("Explore Pie Chart")
    if url:
        try:
            info = get_info(url)
            if isinstance(info, list):
                df = pd.DataFrame(info)
                plot_pie_chart_by_artist(df)
            else:
                st.warning("Please enter a valid playlist URL to explore the pie chart.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid Spotify track/playlist URL.")

# Action on get info button click
if get_info_button:
    if url:
        try:
            info = get_info(url)
            st.subheader("Details:")
            if isinstance(info, list):
                # If it's a playlist, display all tracks
                for idx, song_info in enumerate(info, 1):
                    st.write(f"**Track {idx}:**")
                    for key, value in song_info.items():
                        st.write(f"{key}: {value}")
                    st.write('---')
            else:
                # If it's a track, display single track info
                for key, value in info.items():
                    st.write(f"{key}: {value}")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid Spotify track/playlist URL.")

# Action on download button click
if download_button:
    if url:
        try:
            info = get_info(url)
            df = pd.DataFrame(info)
            
            # Create Excel file in memory
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Spotify Info')

            # Seek to the beginning of the buffer
            excel_buffer.seek(0)
            
            # Create CSV file in memory
            csv_data = df.to_csv(index=False)

            # Provide download options for both files separately
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="spotify_info.csv",
                mime="text/csv"
            )

            st.download_button(
                label="Download Excel",
                data=excel_buffer,
                file_name="spotify_info.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid Spotify track/playlist URL.")
