import streamlit as st
from modules.cloud import query_feature_set, query_all_card_types
from modules.processing import agg_by_set, agg_by_release, select_by_date, clip_sets, get_winners, get_ripe_boxes, get_baby_sets
from modules.analysis import summarize_dataframe
from modules.viz import Plotter
from modules.config import feature_descriptions, intro_md
from datetime import datetime

st.set_page_config(page_title="Pokémon Market Analysis", layout="centered")

st.title('PokeAnalytics')
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
end = '2024-11'

filtered_df = select_by_date(df, start, end)
start_formatted = datetime.strptime(start, "%Y-%m").strftime("%m-%Y")
end_formatted = datetime.strptime(end, "%Y-%m").strftime("%m-%Y")
st.markdown(f"""*selected data date range: ({start_formatted} to {end_formatted})*""")
# remove 1st 2 months of release data per set
filtered_df = clip_sets(filtered_df)
st.markdown(f'*data of dimensions: {filtered_df.shape}*')
st.markdown("---")



# aggregating by set, then by months released for life_time plots
agg_by_set_df = agg_by_set(filtered_df)
agg_by_release_df = agg_by_release(filtered_df)

modern_line_plts = Plotter(title="", xlabel="date (monthly)", ylabel="price (USD)")
feature = "top10_nm_card_mo_sum_in_set"
title = "All set card values: sum of top 10 cards"
st.subheader(title)
top10_nm_card_mo_sum_in_set = modern_line_plts.plot_basic(agg_by_set_df, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(top10_nm_card_mo_sum_in_set)

big_sets = get_winners(agg_by_set_df)
winners = agg_by_set_df[agg_by_set_df['set_name'].isin(big_sets)]
title = "Mid range sets ($700-1250): sum of top 10 cards"
st.subheader(title)
semi_winners = winners[~winners['set_name'].isin(['evolving-skies', 'team-up'])]
top10_nm_card_mo_sum_in_winning_sets = modern_line_plts.plot_basic(semi_winners, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(top10_nm_card_mo_sum_in_winning_sets)

small_sets = get_baby_sets(agg_by_set_df)
baby_sets = agg_by_set_df[agg_by_set_df['set_name'].isin(small_sets)]
title = "Unripe sets (less than $700): sum of top 10 cards"
st.subheader(title)
top10_nm_card_mo_sum_in_winning_sets = modern_line_plts.plot_basic(baby_sets, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(top10_nm_card_mo_sum_in_winning_sets)
st.markdown("---")


feature = "bb_mo_price_by_set"
title = "All booster boxes: sell prices"
st.subheader(title)
bb_mo_price_by_set = modern_line_plts.plot_basic(agg_by_set_df, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(bb_mo_price_by_set)

# set_names where their bb price over 500 but not over 1000
ripe_boxes_set_names = get_ripe_boxes(agg_by_set_df)
ripe_boxes = agg_by_set_df[agg_by_set_df['set_name'].isin(ripe_boxes_set_names)]
title = "Mid range booster boxes: sell price \$500-$1000"
st.subheader(title)
bb_mo_price_by_set_ripe = modern_line_plts.plot_basic(ripe_boxes, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(bb_mo_price_by_set_ripe)
st.markdown("---")

# deduplicate and copy
print(f'...saving copy of deduped data (by poke_id & set_year) to analyze later...starting with {len(df)} rows')
unique_df = filtered_df.drop_duplicates(subset=['poke_name', "poke_id", 'set_year'], keep='first')
unique_df = unique_df.loc[unique_df.product_type == "card"]
unique_summary = summarize_dataframe(filtered_df)

# non-aggregate visualizations (deduplicated/unique pokemon df usually)
plotter = Plotter(title="", xlabel="card type", ylabel="Percentage")
fig = plotter.plot_is_columns_bar_plot(unique_summary)
st.subheader(f"Card types breakdown out of all unique, scraped cards ({len(unique_df)})")
st.pyplot(fig)
st.markdown(f'- og_char: {feature_descriptions["is_og_char"]}')
st.markdown(f'- legendary: {feature_descriptions["is_legendary"]}')
st.markdown("---")


card_types = query_all_card_types()
st.markdown(f"{len(card_types)} most common card types (50 or more cards)")

plotter = Plotter(title="Card Type Histogram", xlabel="Card Type", ylabel="Frequency")
# Plot histogram of card types with at least 3 occurrences
fig = plotter.plot_histogram(data=card_types, x='card_type', weights_column='count', bins=10)
st.pyplot(fig)

st.markdown("---")


st.subheader('Dataframe dtypes and metrics')
st.write(summary_df)


st.subheader('Raw dataset')
st.write(df)