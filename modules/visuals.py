import streamlit as st
from pathlib import Path
from PIL import Image

# TODO: Put Average all time PSA 10 prices next to each of these sprites! Easier if we had a table to query from for this and many other aggs in this app
def add_pokemon_sprites():
    pokemon_names = [
        "charizard", "venusaur", "blastoise", "articuno", "zapdos", "moltres", "dratini", "dragonair", 
        "dragonite", "mewtwo", "mew", "gengar", "skarmory", "raikou", "entei", "suicune", "lugia", "ho-oh", 
        "treecko", "grovyle", "sceptile", "torchic", "combusken", "blaziken", "mudkip", "marshtomp", "swampert", 
        "flygon", "altaria", "milotic", "salamence", "metagross", "regirock", "registeel", "regice", "latias", 
        "latios", "kyogre", "groudon", "rayquaza", "jirachi", "deoxys-normal"
    ]
    
    # Loop through the list of Pokémon names
    for pokemon in pokemon_names:
        # Construct the image path based on the Pokémon name
        image_path = Path(__file__).parent / "images" / f"{pokemon.lower()}.png"
        
        # Open the image using PIL to resize it
        with Image.open(image_path) as img:
            # Resize the image to half of its original width (adjust as necessary)
            width, height = img.size
            new_width = int(width * 0.7)  # Resize to 50% of the original width
            new_height = int(height * 0.7)  # Resize to 50% of the original height
            img = img.resize((new_width, new_height))

            # Save the resized image temporarily
            resized_image_path = Path(__file__).parent / "images" / f"resized_{pokemon.lower()}.png"
            img.save(resized_image_path)

        # Display the resized image in the sidebar
        st.sidebar.image(str(resized_image_path), use_column_width=False)

        # Add some vertical space between the images
        st.sidebar.markdown("<br>", unsafe_allow_html=True)

