import pandas as pd
from modules.config import feature_descriptions

def summarize_dataframe(df):
    summary = pd.DataFrame({
        'dtype': df.dtypes,
        'non_null_count': df.count(),
        'unique_count': df.nunique(),
        'min': df.min(numeric_only=True),
        'max': df.max(numeric_only=True),
        'mean': df.mean(numeric_only=True)
    })
    
    summary['min'] = summary['min'].fillna('N/A')
    summary['max'] = summary['max'].fillna('N/A')
    summary['mean'] = summary['mean'].round(3).fillna('N/A')
    
    descriptions = pd.DataFrame(list(feature_descriptions.items()), columns=['Column Name', 'Description']).set_index('Column Name')

    summary = summary.join(descriptions, how='left')
    return summary
