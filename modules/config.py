# Define a dictionary with column names as keys and descriptions as values
feature_descriptions = {
    "grade": "Grade of the card (NM / PSA7-10 / BGS9.5)",
    "mos_since_release": "Months since the release of the card set",
    "is_secret": "Whether the card is a secret rare",
    "is_full_art": "Whether the card is a full art",
    "is_full_art_secret": "Whether the card is a full art secret rare",
    "is_ir": "Whether the card is an Illustration Rare (IR)",
    "is_sir": "Whether the card is a Special Illustration Rare (SIR)",
    "is_ultra_rare": "Whether the card is an ultra-rare",
    "is_shiny_rare": "Whether the card is a shiny rare",
    "is_eeveelution": "Whether the card is an Eeveelution",
    "is_legendary": "Whether the card is a Legendary Pokémon from gen1-4",
    "is_og_char": "Whether the card features a nostalgic non-legendary character (e.g., Charizard, Blastoise, Venusaur, Gengar, Alakazam, Snorlax, Pikachu, Dragonite, Gyarados)",
    "is_gallery": "Whether the card is part of the gallery series",
    "avg_mo_price_sealed_in_set": "Average market price of sealed products per set",
    "max_mo_price_sealed_in_set": "Maximum market price of sealed products per set",
    "avg_mo_price_card_in_set": "Average market price of the card per set",
    "max_mo_price_card_in_set": "Maximum market price of the card per set",
    "top10_nm_card_mo_sum_in_set": "Top 10 most valuable cards (nm) per set, summed",
    "top10_nm_card_mo_avg_in_set": "Top 10 most valuable cards (nm) per set, avg",
    "bb_mo_price_by_set": "Booster box sell price by set",
    "etb_mo_price_by_set": "Elite Trainer Box market price by set",
    "top10_mo_card_sum_to_bb_cost_ratio": "Ratio of the top 10 card sum to booster box cost",
    "avg_mo_price_psa_10_in_set": "Average market price of PSA 10 cards per set",
    "max_mo_price_psa_10_in_set": "Maximum market price of PSA 10 cards per set"
}

intro_md = "Analytics and AI on modern, Pokémon card price data. The data is scraped from PriceCharting and stored in RDS using a serverless, AWS pipeline. "