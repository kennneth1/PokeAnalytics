import streamlit as st
from modules.cloud import query_feature_set, query_all_card_types
from modules.processing import agg_by_set, agg_by_release, select_by_date, clip_sets, get_winners, get_ripe_boxes, get_baby_sets, get_baby_boxes
from modules.analysis import summarize_dataframe
from modules.viz import Plotter
from modules.config import feature_descriptions, intro_md
from datetime import datetime
from dateutil.relativedelta import relativedelta

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
end = '2024-11' # yyyy-mm of current month

filtered_df = select_by_date(df, start, end)
start_formatted = datetime.strptime(start, "%Y-%m").strftime("%m-%Y")
end_formatted = datetime.strptime(end, "%Y-%m").strftime("%m-%Y")
st.markdown(f"""*selected data date range: ({start_formatted} to {end_formatted})*""")
# remove 1st 2 months of release data per set
filtered_df = clip_sets(filtered_df)
st.markdown(f'*data of dimensions: {filtered_df.shape}*')
st.markdown("---")

last_month = datetime.today()- relativedelta(months=1)
clipped_tail = last_month.strftime("%Y-%m")


### Set Values
agg_by_set_df = agg_by_set(filtered_df)
agg_by_release_df = agg_by_release(filtered_df)

modern_line_plts = Plotter(title="", xlabel="date (monthly)", ylabel="price (USD)")
feature = "top10_nm_card_mo_sum_in_set"
title = "All set card values: sum of top 10 cards" # basically ~= average cost of near mint
st.subheader(title)
top10_nm_card_mo_sum_in_set = modern_line_plts.plot_basic(agg_by_set_df, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(top10_nm_card_mo_sum_in_set)
st.markdown("\n")

big_sets = get_winners(agg_by_set_df)
winners = agg_by_set_df[agg_by_set_df['set_name'].isin(big_sets)]
winners=winners.loc[winners.date<clipped_tail]
title = "Mid range sets ($700-1250): sum of top 10 cards"
st.subheader(title)
semi_winners = winners[~winners['set_name'].isin(['evolving-skies', 'team-up'])]
top10_nm_card_mo_sum_in_winning_sets = modern_line_plts.plot_basic(semi_winners, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(top10_nm_card_mo_sum_in_winning_sets)
st.markdown("\n")

small_sets = get_baby_sets(agg_by_set_df)
baby_sets = agg_by_set_df[agg_by_set_df['set_name'].isin(small_sets)]
baby_sets = baby_sets.loc[baby_sets.date<=clipped_tail]
title = "Unripe sets (less than $700): sum of top 10 cards"
st.subheader(title)
top10_nm_card_mo_sum_in_winning_sets = modern_line_plts.plot_basic(baby_sets, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(top10_nm_card_mo_sum_in_winning_sets)
st.markdown("\n")

modern_sets = filtered_df.loc[filtered_df.release_date>="2022"].reset_index()
modern_sets = modern_sets.loc[modern_sets.date<clipped_tail]
agg_modern_sets = agg_by_set(modern_sets)
title = "Modern sets (2022+ release): sum of top 10 cards"
st.subheader(title)
top10_nm_card_mo_sum_modern = modern_line_plts.plot_basic(agg_modern_sets, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(top10_nm_card_mo_sum_modern)
st.markdown("\n")

st.markdown("---")

### Booster Boxes
feature = "bb_mo_price_by_set"
title = "All booster boxes: sell prices"
st.subheader(title)
exclude_words = ['crown-zenith', 'scarlet-&-violet-151', 'champions-path', 'paldean fates', 'hidden-fates', 'shining-fates']
bb_mo_price_by_set = modern_line_plts.plot_basic(agg_by_set_df[~agg_by_set_df['set_name'].isin(exclude_words)], x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(bb_mo_price_by_set)
st.markdown("\n")

exclude_words = ['crown-zenith', 'scarlet-&-violet-151', 'champions-path', 'paldean fates', 'hidden-fates', 'shining-fates']
ripe_boxes_set_names = get_ripe_boxes(agg_by_set_df)
ripe_boxes = agg_by_set_df[agg_by_set_df['set_name'].isin(ripe_boxes_set_names)]
title = "Matured booster boxes: sell price \$200-$1000"
exclude_words = ['crown-zenith', 'scarlet-&-violet-151', 'champions-path', 'paldean fates', 'hidden-fates', 'shining-fates']
st.subheader(title)
bb_mo_price_by_set_ripe = modern_line_plts.plot_basic(ripe_boxes, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(bb_mo_price_by_set_ripe)
st.markdown("\n")


young_boxes_set_names = get_baby_boxes(agg_by_set_df)
young_boxes = agg_by_set_df[agg_by_set_df['set_name'].isin(young_boxes_set_names)]
title = "Cheaper booster boxes: sell price <$200"
st.subheader(title)
bb_mo_price_by_set_ripe = modern_line_plts.plot_basic(young_boxes, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(bb_mo_price_by_set_ripe)
st.markdown("\n")

st.markdown("---")

### --- Other comparisons
title = "Average PSA 10 Price per set"
st.subheader(title)

feature = 'avg_mo_price_psa_10_in_set'
avg_mo_price_psa_10_in_set = modern_line_plts.plot_basic(agg_by_set_df, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(avg_mo_price_psa_10_in_set)
st.markdown("\n")

feature = 'avg_mo_price_sealed_in_set'
title = "Average sealed price per set"
st.subheader(title)
avg_mo_price_sealed_in_set = modern_line_plts.plot_basic(agg_by_set_df, x='date', y=feature, kind="line", hue="set_name", marker='o')
st.pyplot(avg_mo_price_sealed_in_set)
st.markdown("\n")


modern_line_plts = Plotter(title="", xlabel="date (monthly)", ylabel="")
feature = 'top10_mo_card_sum_to_bb_cost_ratio'
title = "Top 10 card value to Booster box cost ratio"
st.subheader(title)
top10_mo_card_sum_to_bb_cost_ratio = modern_line_plts.plot_basic(agg_by_set_df.loc[agg_by_set_df.date>='2022-01'], x='date', y=feature, kind="line", hue="set_name", marker='o')
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


st.subheader('Raw dataset')
st.write(df)
st.markdown("---")



st.write(" Thanks for visiting!")
st.write("💡Have ideas or want to collaborate? Feel free to reach out!")
st.write("[LinkedIn](https://www.linkedin.com/in/kennethh123/) | [Github](https://github.com/kennneth1)")
st.write("— Kenneth H.")
