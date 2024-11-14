import streamlit as st
from modules.cloud import query_feature_set, query_all_card_types
from modules.processing import agg_by_set, agg_by_release, select_by_date, clip_sets, get_winners, get_ripe_boxes, get_baby_sets, get_baby_boxes
from modules.analysis import summarize_dataframe
from modules.viz import Plotter
from modules.config import feature_descriptions, intro_md
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np


st.set_page_config(page_title="Pokémon Market Analysis", layout="centered")

#st.title('PokeAnalytics')
st.markdown(intro_md)


data_load_state = st.text('loading data...')
df = query_feature_set(limit=300000)
data_load_state.text("Data loaded")
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# raw / summary
summary_df = summarize_dataframe(df)

# Selection and clipping
start = '2021-01'
end = '2024-11' # yyyy-mm of current month

filtered_df = select_by_date(df, start, end)
start_formatted = datetime.strptime(start, "%Y-%m").strftime("%m-%Y")
end_formatted = datetime.strptime(end, "%Y-%m").strftime("%m-%Y")
# remove 1st 2 months of release data per set
filtered_df = clip_sets(filtered_df)
filtered_df = filtered_df.loc[filtered_df.price>0]



##------------------------------------------------------------------------------------------------------------
st.markdown("---")
title="Price Movement Predictor"
st.subheader(title)
# (card prices are very difficult to predict accurately even month to month due many factors like - hype in the collector space, subjectivity of what the fanbase deems a cool card, and perhaps not enough descriptive features in this model. As such, it is advised to use this tool merely for entertainment purposes or scrappy experimentation)
st.markdown("in progress")
fastapi_url="https://"
with st.form(key='input_form'):
    # Collecting input from user
    mos_since_release = st.text_input('Months since set was released', value=1)
    num_grade = st.slider('PSA Grade (8 for near mint/raw cards)', min_value=1, max_value=10, value=8)
    is_secret = st.checkbox('Secret rare')
    is_full_art = st.checkbox('Full Art')
    is_tag_team = st.checkbox('Tag Team')
    is_alt_art = st.checkbox('Alt Art')
    is_eeveelution = st.checkbox('Eeveelution')
    is_legendary = st.checkbox('Legendary (gen1-4)')
    is_og_char = st.checkbox('Nolstagic Favorite (see below)')
    ir_score = st.text_input('Illustration Rare Score (0=NA, 1=IR, 2=SIR)', value="0")
    num_predictions = st.slider('Num predictions (past the first month)', min_value=2, max_value=11, value=2)

    # Submit button for the form
    submit_button = st.form_submit_button(label='Predict Price Movements (Coming soon)')

# Convert input data to the appropriate format
if submit_button:
    input_data = {
        "mos_since_release": mos_since_release,
        "num_grade": num_grade,
        "is_secret": int(is_secret),  # FastAPI expects boolean 0 or 1
        "is_full_art": int(is_full_art),
        "is_tag_team": int(is_tag_team),
        "is_alt_art": int(is_alt_art),
        "is_eeveelution": int(is_eeveelution),
        "is_legendary": int(is_legendary),
        "is_og_char": int(is_og_char),
        "ir_score": int(ir_score),
        "num_predictions": int(num_predictions)
    }

st.markdown("built with XGBoost and FastAPI, working on deploying with either Heroku or SageMaker endpoints...")
    # Send the data to the FastAPI model for prediction
    #try:
    #    response = requests.post(fastapi_url, json=input_data)
    #    
    #    if response.status_code == 200:
    #        # Parse and display the result
    #        result = response.json()
    #        st.write(f"Predicted Price: ${result['price']:.2f}")
    #    else:
    #        st.error(f"Error: {response.status_code} - {response.text}")
    #except Exception as e:
    #    st.error(f"An error occurred: {e}")

# Given user inputs, search df for cards with matching attributes/filters, average, plot and validate    
# against our [%,%,%,%] and avg % prediction payloads
# plot here title = "Cards like this performed like"

st.markdown("\n")
title="Feature Importance"
st.subheader(title)
image_path = "modules/images/feature_importance.png"
st.image(image_path, caption="learning_rate=0.1, max_depth=5, n_estimators=250, RSME~=60", use_column_width=True)

st.markdown("\n")
##------------------------------------------------------------------------------------------------------------
st.markdown("---")
st.subheader("Price Tracking")
# Select the 3 most recent prices for each poke_id
#latest_prices = df[df['price'] > 0]
df = df.sort_values(by='date', ascending=True)
latest_prices = df.groupby(['poke_id', 'grade']).tail(3)

# Aggregate by poke_name, poke_id, grade, and set_name to include the set_name in the result
last_3mo_avg = latest_prices.groupby(['poke_name', 'poke_no', 'grade', 'set_name']).agg({'price': 'mean'}).reset_index()

# Calculate the price for the most recent month (first price for each poke_id, grouped by grade)
last_mo = latest_prices.groupby(['poke_name', 'poke_no', 'grade', 'set_name']).agg({'price': 'last'}).reset_index()
# Merge the two DataFrames on poke_name, grade, poke_id, and set_name
metrics = last_3mo_avg.merge(last_mo, on=["poke_name", "grade", "poke_no", "set_name"])

# Rename the columns for clarity
metrics.rename(columns={'price_x': 'last_3mo_avg_price', 'price_y': 'last_mo_price'}, inplace=True)

# Calculate the percent change between last_3mo_avg_price and last_mo_price
metrics['perc_change'] = ((metrics['last_mo_price'] - metrics['last_3mo_avg_price']) / metrics['last_3mo_avg_price']) * 100
metrics['perc_change'].replace([np.inf, -np.inf, np.nan], 0, inplace=True)

# Round the perc_change column to integers
metrics['perc_change'] = metrics['perc_change'].round(0).astype(int)

release_data = df[['set_name', 'release_date']].groupby("set_name").first()
metrics = metrics.merge(release_data, on='set_name', how='left')
import pandas as pd
# Ensure 'release_date' is in datetime format
metrics['release_date'] = pd.to_datetime(metrics['release_date'])

# Sort the set_name filter by release_date
sorted_sets = metrics.sort_values('release_date', ascending=False)['set_name'].unique()

# Order the grade filter manually
grade_order = ['nearmint', 'psa_10', 'psa_9', 'psa_8', 'psa_7', 'bgs_9_half']

# Set 'grade' as a categorical column with the custom order
metrics['grade'] = pd.Categorical(metrics['grade'], categories=grade_order, ordered=True)

# Now, use the categories to sort the unique values in the 'grade' column
sorted_grades = metrics['grade'].cat.categories

# Set up Streamlit filters
set_name_filter = st.selectbox("Select Set", sorted_sets)
grade_filter = st.selectbox("Select Grade", sorted_grades)

# Filter the view based on selected set_name and grade
view = metrics[(metrics['set_name'] == set_name_filter) & (metrics['grade'] == grade_filter)]

# Drop the set_name column for clarity in the final display
view = view.drop(columns=['set_name', 'release_date'])

# Display the filtered and sorted view in Streamlit
st.dataframe(view.sort_values("last_mo_price", ascending=False))
##-----------------------
st.markdown("---")
st.subheader("Top raw movers over 25 USD")
# Select the 3 most recent prices for each poke_id
raw = df.loc[df.grade=="nearmint"]
latest_prices = raw.groupby('poke_id').tail(3)
# Aggregate by poke_name, poke_id, grade, and set_name to include the set_name in the result
last_3mo_avg = latest_prices.groupby(['poke_name', 'set_name', 'poke_no']).agg({'price': 'mean'}).reset_index()

# Calculate the price for the most recent month (first price for each poke_id, grouped by grade)
last_mo = latest_prices.groupby(['poke_name', 'set_name', 'poke_no']).agg({'price': 'last'}).reset_index()

# Merge the two DataFrames on poke_name, grade, poke_id, and set_name
metrics = last_3mo_avg.merge(last_mo, on=["poke_name", 'set_name', "poke_no"])

# Rename the columns for clarity
metrics.rename(columns={'price_x': 'last_3mo_avg_price', 'price_y': 'last_mo_price'}, inplace=True)

# Calculate the percent change between last_3mo_avg_price and last_mo_price
metrics['perc_change'] = ((metrics['last_mo_price'] - metrics['last_3mo_avg_price']) / metrics['last_3mo_avg_price']) * 100
metrics['perc_change'].replace([np.inf, -np.inf, np.nan], 0, inplace=True)

# Round the perc_change column to integers
metrics['perc_change'] = metrics['perc_change'].round(0).astype(int)

top_50 = metrics.loc[metrics.last_mo_price>=25].sort_values("perc_change", ascending=False)
st.dataframe(top_50)


##------------------------------------------------------------------------------------------------------------
st.markdown("---")
st.subheader('Visualizations')
st.markdown("*Card Price Predictor was trained on a subset of this data* ")

st.markdown(f"""- selected data date range: ({start_formatted} to {end_formatted})\n- data of dimension: {filtered_df.shape}""")


last_month = datetime.today()- relativedelta(months=1)
clipped_tail = last_month.strftime("%Y-%m")


### Set Values
agg_by_set_df = agg_by_set(filtered_df)
agg_by_release_df = agg_by_release(filtered_df)

modern_line_plts = Plotter(title="", xlabel="date (monthly)", ylabel="price (USD)")
feature = "top10_nm_card_mo_sum_in_set"
title = "All set card values: sum of top 10 cards" # basically ~= average cost of near mint
st.subheader(title)
top10_nm_card_mo_sum_in_set = modern_line_plts.plot_basic(agg_by_set_df, x='date', y=feature, kind="line", hue="set_name")
st.pyplot(top10_nm_card_mo_sum_in_set)
st.markdown("\n")

big_sets = get_winners(agg_by_set_df)
winners = agg_by_set_df[agg_by_set_df['set_name'].isin(big_sets)]
winners=winners.loc[winners.date<clipped_tail]
title = "Mid range sets ($700-1250): sum of top 10 cards"
st.subheader(title)
semi_winners = winners[~winners['set_name'].isin(['evolving-skies', 'team-up'])]
top10_nm_card_mo_sum_in_winning_sets = modern_line_plts.plot_basic(semi_winners, x='date', y=feature, kind="line", hue="set_name")
st.pyplot(top10_nm_card_mo_sum_in_winning_sets)
st.markdown("\n")

small_sets = get_baby_sets(agg_by_set_df)
baby_sets = agg_by_set_df[agg_by_set_df['set_name'].isin(small_sets)]
baby_sets = baby_sets.loc[baby_sets.date<=clipped_tail]
title = "Unripe sets (less than $700): sum of top 10 cards"
st.subheader(title)
top10_nm_card_mo_sum_in_winning_sets = modern_line_plts.plot_basic(baby_sets, x='date', y=feature, kind="line", hue="set_name")
st.pyplot(top10_nm_card_mo_sum_in_winning_sets)
st.markdown("\n")

modern_sets = filtered_df.loc[filtered_df.release_date>="2022"].reset_index()
modern_sets = modern_sets.loc[modern_sets.date<clipped_tail]
agg_modern_sets = agg_by_set(modern_sets)
title = "Modern sets (2022+ release): sum of top 10 cards"
st.subheader(title)
top10_nm_card_mo_sum_modern = modern_line_plts.plot_basic(agg_modern_sets, x='date', y=feature, kind="line", hue="set_name")
st.pyplot(top10_nm_card_mo_sum_modern)
st.markdown("\n")

st.markdown("---")

### Booster Boxes
feature = "bb_mo_price_by_set"
title = "All booster boxes: sell prices"
st.subheader(title)
exclude_words = ['crown-zenith', 'scarlet-&-violet-151', 'champions-path', 'paldean fates', 'hidden-fates', 'shining-fates']
bb_mo_price_by_set = modern_line_plts.plot_basic(agg_by_set_df[~agg_by_set_df['set_name'].isin(exclude_words)], x='date', y=feature, kind="line", hue="set_name")
st.pyplot(bb_mo_price_by_set)
st.markdown("\n")

exclude_words = ['crown-zenith', 'scarlet-&-violet-151', 'champions-path', 'paldean fates', 'hidden-fates', 'shining-fates']
ripe_boxes_set_names = get_ripe_boxes(agg_by_set_df)
ripe_boxes = agg_by_set_df[agg_by_set_df['set_name'].isin(ripe_boxes_set_names)]
title = "Matured booster boxes: sell price \$200-$1000"
exclude_words = ['crown-zenith', 'scarlet-&-violet-151', 'champions-path', 'paldean fates', 'hidden-fates', 'shining-fates']
st.subheader(title)
bb_mo_price_by_set_ripe = modern_line_plts.plot_basic(ripe_boxes, x='date', y=feature, kind="line", hue="set_name")
st.pyplot(bb_mo_price_by_set_ripe)
st.markdown("\n")


young_boxes_set_names = get_baby_boxes(agg_by_set_df)
young_boxes = agg_by_set_df[agg_by_set_df['set_name'].isin(young_boxes_set_names)]
title = "Cheaper booster boxes: sell price <$200"
st.subheader(title)
bb_mo_price_by_set_ripe = modern_line_plts.plot_basic(young_boxes, x='date', y=feature, kind="line", hue="set_name")
st.pyplot(bb_mo_price_by_set_ripe)
st.markdown("\n")

st.markdown("---")

### --- Other comparisons
title = "Average PSA 10 Price per set"
st.subheader(title)

feature = 'avg_mo_price_psa_10_in_set'
avg_mo_price_psa_10_in_set = modern_line_plts.plot_basic(agg_by_set_df, x='date', y=feature, kind="line", hue="set_name")
st.pyplot(avg_mo_price_psa_10_in_set)
st.markdown("\n")

feature = 'avg_mo_price_sealed_in_set'
title = "Average sealed price per set"
st.subheader(title)
avg_mo_price_sealed_in_set = modern_line_plts.plot_basic(agg_by_set_df, x='date', y=feature, kind="line", hue="set_name")
st.pyplot(avg_mo_price_sealed_in_set)
st.markdown("\n")


modern_line_plts = Plotter(title="", xlabel="date (monthly)", ylabel="")
feature = 'top10_mo_card_sum_to_bb_cost_ratio'
title = "Top 10 card value to Booster box cost ratio"
st.subheader(title)
top10_mo_card_sum_to_bb_cost_ratio = modern_line_plts.plot_basic(agg_by_set_df.loc[agg_by_set_df.date>='2022-01'], x='date', y=feature, kind="line", hue="set_name")
st.pyplot(top10_mo_card_sum_to_bb_cost_ratio)
st.markdown("- i.e. a set with a \$500 total top 10 NM card cost, and a booster box cost of $100, has a ratio of 5.0")
st.markdown("\n")

st.markdown("---")

# deduplicate and copy
print(f'...saving copy of deduped data (by poke_id & set_year) to analyze later...starting with {len(df)} rows')
unique_df = filtered_df.drop_duplicates(subset=['poke_name', "poke_id", 'set_year'], keep='first')
unique_df = unique_df.loc[unique_df.product_type == "card"]
unique_summary = summarize_dataframe(filtered_df)

# non-aggregate visualizations (deduplicated/unique pokemon df usually)
plotter = Plotter(title="", xlabel="card type", ylabel="Percentage")
fig = plotter.plot_is_columns_bar_plot(unique_summary)
st.subheader(f"Card types among the unique, scraped cards ({len(unique_df)})")
st.pyplot(fig)
st.markdown(f'- og_char: {feature_descriptions["is_og_char"]}')
st.markdown(f'- legendary: {feature_descriptions["is_legendary"]}')


card_types = query_all_card_types()
st.subheader(f"{len(card_types)} most common PSA card types (50+ req.)")

plotter = Plotter(title="Card Type Histogram", xlabel="Card Type", ylabel="Frequency")
# Plot histogram of card types with at least 3 occurrences
fig = plotter.plot_histogram(data=card_types, x='card_type', weights_column='count', bins=10)
st.pyplot(fig)

st.markdown("---")


st.subheader('Dataframe dtypes and metrics')
st.write(summary_df)


#st.subheader('Raw dataset')
#st.write(df)
st.markdown("---")



st.write(" Thanks for visiting!")
st.write("💡Have ideas, need data, or want to collaborate? Feel free to reach out!")
st.write("[LinkedIn](https://www.linkedin.com/in/kennethh123/) | [Github](https://github.com/kennneth1)")
st.write("— Kenneth H.")



