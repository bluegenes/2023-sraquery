import pandas as pd
import db_dtypes
pq_file = '2023-08-02.sra-mgx-metadata.parquet'
df = pd.read_parquet(pq_file)

# select dataframe rows where the organism column contains the word 'human'
df['organism'] = df['organism'].fillna('') # organism column contains NAs, which screws up the contains() method
human_df = df[df['organism'].str.contains('human', case=False)]

# count organism column values
human_df['organism'].value_counts()

# look at platform counts 
human_df['platform'].value_counts()


# write the human metadata to a csv file
human_df.to_csv("20230802-human-mgx.metadata.csv.gz", index=False)

# write just the accession and organism columns to a csv file
human_df[['acc', 'organism']].to_csv("20230802-human-mgx.acc-organism.csv.gz", index=False)

# write acc organism file for just illumina platform
human_df[human_df['platform'] == 'ILLUMINA'][['acc', 'organism']].to_csv("20230802-human-mgx.acc-organism.illumina.csv.gz", index=False)