[![hackmd-github-sync-badge](https://hackmd.io/Z-DERt3HTxG9nVIeX3wNZA/badge)](https://hackmd.io/Z-DERt3HTxG9nVIeX3wNZA)

## General info: BigQuery Metadata search

- ref Rob Edwards blog post [here](https://edwards.flinders.edu.au/identifying-metagenomes-from-the-sra-in-the-cloud/)

### To get all Metagenome / Microbiome / Metatranscriptome data: 
> We use temporary tables to store the two main searches: what are amplicon projects and what are metagenome/microbiome/metatranscriptome projects, and then we find the projects that are metagenomes:

first, just look at the accs:
```
create temp table AMPLICON(acc STRING) as select acc as amplicon from `nih-sra-datastore.sra.metadata` where assay_type = 'AMPLICON' or libraryselection = 'PCR';
create temp table METAGENOMES(acc STRING) as select acc from `nih-sra-datastore.sra.metadata` where librarysource = "METAGENOMIC" or librarysource = 'METATRANSCRIPTOMIC' or organism like "%microbiom%" OR organism like "%metagenom%"  or organism like '%metatran%';
select acc from METAGENOMES where acc not in (select acc from AMPLICON);
```

if we want ALL metadata:
```
create temp table AMPLICON(acc STRING) as select acc as amplicon from `nih-sra-datastore.sra.metadata` where assay_type = 'AMPLICON' or libraryselection = 'PCR';
select * from `nih-sra-datastore.sra.metadata` where acc not in (select acc from AMPLICON) and (librarysource = "METAGENOMIC" or librarysource = 'METATRANSCRIPTOMIC' or organism like "%microbiom%" OR organism like "%metagenom%");
```


This file is too big to download. You can, however **manually** save the json to google drive or click the 'Explore Data' and select the 'Explore with Python Notebook' option to open a colab script.

- manually save json file to google drive. File saved as: `bq-results-20230424-230240-1682377425632.json`

- extract the SRA metagenome accessions
`jq -r '.acc' bq-results-20230424-230240-1682377425632.json > SRA-metagenomes.txt`

#### Use Google CoLab

Setup
```
# @title Setup
from google.colab import auth
from google.cloud import bigquery
from google.colab import data_table

project = 'bigquery-gps' # Project ID inserted based on the query results selected to explore
location = 'US' # Location inserted based on the query results selected to explore
client = bigquery.Client(project=project, location=location)
data_table.enable_dataframe_formatter()
auth.authenticate_user()
```

```
# Running this code will display the query used to generate your previous job

job = client.get_job('script_job_2e450d0b1e4a89bdf8943aaaa1ea7713_1') # Job ID inserted based on the query results selected to explore
print(job.query)
```

Read BigQuery Results to DataFrame
```
# Running this code will read results from your previous job

job = client.get_job('script_job_2e450d0b1e4a89bdf8943aaaa1ea7713_1') # Job ID inserted based on the query results selected to explore
results = job.to_dataframe()
results
```

```
results.describe()
```

#### save dataframe to parquet and download

---
---

# Find pig-associated microbiome samples (Aug 2023)

get accs/ count pig-associated samples:

```
CREATE TEMP TABLE AMPLICON(acc STRING) AS 
SELECT acc AS amplicon 
FROM `nih-sra-datastore.sra.metadata` 
WHERE assay_type = 'AMPLICON' OR libraryselection = 'PCR';

CREATE TEMP TABLE METAGENOMES(acc STRING) AS 
SELECT acc 
FROM `nih-sra-datastore.sra.metadata` 
WHERE (librarysource = "METAGENOMIC" OR librarysource = 'METATRANSCRIPTOMIC' 
       OR organism LIKE "%microbiom%" OR organism LIKE "%metagenom%" 
       OR organism LIKE '%metatran%')
       AND (organism LIKE "%pig%" OR organism LIKE "%Sus scrofa%");

SELECT acc FROM METAGENOMES WHERE acc NOT IN (SELECT acc FROM AMPLICON);
SELECT COUNT(*) FROM METAGENOMES WHERE acc NOT IN (SELECT acc FROM AMPLICON);
```
**count = 8864**

## Modify to get all metadata instead of just acc

```
CREATE TEMP TABLE AMPLICON(acc STRING) AS 
SELECT acc AS amplicon 
FROM `nih-sra-datastore.sra.metadata` 
WHERE assay_type = 'AMPLICON' OR libraryselection = 'PCR';

select * from `nih-sra-datastore.sra.metadata`
WHERE acc not in (select acc from AMPLICON) 
AND (librarysource = "METAGENOMIC" OR librarysource = 'METATRANSCRIPTOMIC' 
       OR organism LIKE "%microbiom%" OR organism LIKE "%metagenom%" 
       OR organism LIKE '%metatran%')
       AND (organism LIKE "%pig%" OR organism LIKE "%Sus scrofa%");
```

This produces results that we can work with in google colab. Strategy: click the 'Explore Data' and select the 'Explore with Python Notebook' option to open a colab script. Explore the table with pandas. When satisfied, use `to_csv` or `to_parquet` to save the table; then download from the files tab on the left.


:::info

## Rabbit Hole: Did we find all accessions?

**tl:dr - probably? Including more 'pig' text variations doesn't help. Is there another metadata column we should look in?**

Including other options increases results by ~100 samples

```
FROM `nih-sra-datastore.sra.metadata` 
WHERE assay_type = 'AMPLICON' OR libraryselection = 'PCR';

CREATE TEMP TABLE METAGENOMES(acc STRING) AS 
SELECT acc 
FROM `nih-sra-datastore.sra.metadata` 
WHERE (librarysource = "METAGENOMIC" OR librarysource = 'METATRANSCRIPTOMIC' 
       OR organism LIKE "%microbiom%" OR organism LIKE "%metagenom%" 
       OR organism LIKE '%metatran%')
       AND (organism LIKE "%pig%" OR organism LIKE "%swine%" OR organism LIKE "%piglet%"
       OR organism LIKE "%hog%" OR organism LIKE "%sow%" OR organism LIKE "%boar%" 
       OR organism LIKE "%Sus scrofa%" OR organism LIKE "%Sus domesticus%" OR organism LIKE "%Sus scrofa domesticus%" 
       OR organism = "9823");

SELECT acc FROM METAGENOMES WHERE acc NOT IN (SELECT acc FROM AMPLICON);
SELECT COUNT(*) FROM METAGENOMES WHERE acc NOT IN (SELECT acc FROM AMPLICON);
```

**count = 8959**

Get all metadata instead of just 'acc':
for metagenome SELECT from the `nih-sra-datastore.sra.metadata`, get '*' instead of just 'acc'.

full query:

```
CREATE TEMP TABLE AMPLICON(acc STRING) AS 
SELECT acc AS amplicon 
FROM `nih-sra-datastore.sra.metadata` 
WHERE assay_type = 'AMPLICON' OR libraryselection = 'PCR';

select * from `nih-sra-datastore.sra.metadata`
WHERE acc not in (select acc from AMPLICON) 
       AND (librarysource = "METAGENOMIC" OR librarysource = 'METATRANSCRIPTOMIC' 
       OR organism LIKE "%microbiom%" OR organism LIKE "%metagenom%" 
       OR organism LIKE '%metatran%')
       AND (organism LIKE "%pig%" OR organism LIKE "%swine%"
       OR organism LIKE "%hog%" OR organism LIKE "%sow%" OR organism LIKE "%boar%" 
       OR organism LIKE "%Sus scrofa%" OR organism LIKE "%Sus domesticus%" OR organism LIKE "%Sus scrofa domesticus%" 
       OR organism = "9823");
```

This produces results that we can work with in google colab.

The resulting table contains the following 'organism' counts:

```
pig gut metagenome             7182
pig metagenome                 1191
Sus scrofa                      352
Sus scrofa domesticus           136
African swine fever virus        89
Trichoglossus moluccanus          4
Dolosigranulum pigrum             2
Ptychographa xylographoides       1
Trichoglossum hirsutum            1
Desulfovibrio piger               1
```

Upon examination, these include 8861 pig microbiome samples:
```
pig gut metagenome             7182
pig metagenome                 1191
Sus scrofa                      352
Sus scrofa domesticus           136
```

98 non-pig samples:

organism includes 'swine':
```
African swine fever virus        89
```
organism includes 'hog':
```
Trichoglossus moluccanus          4
Ptychographa xylographoides       1
Trichoglossum hirsutum            1

```
organism includes 'pig':
```
Dolosigranulum pigrum             2
Desulfovibrio piger               1
```
:::





