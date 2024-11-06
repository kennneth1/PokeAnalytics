import pandas as pd
import numpy as np


def conform_dtypes(df):
    print("conform_dtypes(): df has column dtypes:", df.dtypes)
    return df

def clip_sets(df):
    print(f"clip_sets(): Filtering df with len of {len(df)}, selecting sets where months_release>2")
    df = df.loc[df.mos_since_release>2]
    print(f"clip_sets(): returning df with len of {len(df)}, selecting sets where months_release>2")

    return df

def agg_by_set(df):
    # feature_set data is denormalized and aggregated, since that we just need to take the mean to get the respective metric (max, mean, min, etc) per set
    df['date'] = pd.to_datetime(df['date'])

    df.set_index('date', inplace=True)
    agg = df.groupby(['set_name']).resample('ME').agg({
        'avg_mo_price_sealed_in_set': 'mean',
        'avg_mo_price_card_in_set': 'mean',
        'top10_nm_card_mo_avg_in_set': 'mean',
        'top10_nm_card_mo_sum_in_set': 'mean',
        'bb_mo_price_by_set' : 'mean',
        'avg_mo_price_psa_10_in_set' : 'mean',
        'top10_mo_card_sum_to_bb_cost_ratio' : 'mean'
    }).reset_index()

    return agg

def agg_by_release(df):
    agg = df.groupby(['set_name', 'mos_since_release'], as_index=False).agg({
        'avg_mo_price_sealed_in_set': 'mean',
        'avg_mo_price_card_in_set': 'mean',
        'top10_nm_card_mo_avg_in_set': 'mean',
        'top10_nm_card_mo_sum_in_set': 'mean',
        'bb_mo_price_by_set' : 'mean',
        'avg_mo_price_psa_10_in_set' : 'mean',
        'top10_mo_card_sum_to_bb_cost_ratio' : 'mean'
    })

    # Create a new DataFrame to fill in missing months for each set
    max_months = agg['mos_since_release'].max()
    all_months = pd.DataFrame({'mos_since_release': np.arange(0, max_months + 1)})

    # Create a DataFrame for each set with all months
    result = (
        agg
        .set_index(['set_name', 'mos_since_release'])
        .unstack(level=0)
    )

    # Merge with all_months to ensure all months are represented
    result = result.reindex(all_months['mos_since_release'].values, fill_value=np.nan).reset_index()

    # Reset column names for better handling
    result.columns = ['mos_since_release'] + [f'avg_price_{col}' for col in result.columns[1:]]

    # Fill missing values with forward fill (or you can use any method that suits your analysis)
    #result.fillna(method='ffill', inplace=True)

    return result

# based on top 10 card valuation
def get_winners(df):
    mid_range_sets = df[(df['top10_nm_card_mo_sum_in_set'] >= 700)]['set_name'].unique()
    return mid_range_sets

def get_ripe_boxes(df):
    # find the maximum value of 'bb_mo_price_by_set' for each group
    grouped = df.groupby('set_name')['bb_mo_price_by_set'].max()

    # max 'bb_mo_price_by_set' is between 500 and 1000
    filtered_sets = grouped[(grouped >= 500) & (grouped <= 1000)].index.tolist()
    return filtered_sets

def get_baby_boxes(df):
    grouped = df.groupby('set_name')['bb_mo_price_by_set'].max()

    filtered_sets = grouped[(grouped <= 200)].index.tolist()
    return filtered_sets

def get_baby_sets(df):
    grouped_max = df.groupby('set_name')['top10_nm_card_mo_sum_in_set'].max()

    sets_never_exceeding_700 = grouped_max[grouped_max <= 700].index.tolist()
    return sets_never_exceeding_700

def create_major_index(df):
    """
    i.e. filter by something and averages the DF into 1 line chart, representing broad index like 2021 sets, top50 charizard index, alt art index,
                gallery_index  
    """
    return df

# yyyy-mm or yyyy
def select_by_date(df, head, tail):
    df = df.loc[(df.date >= head) & (df.date <= tail)]
    return df
