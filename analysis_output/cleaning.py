import pandas as pd

## dataset
spotify_history = pd.read_csv(
    "/Users/betsyhahn/spotify-streaming-data/data/spotify_history.csv"
)

## data inspection
print("\n--- First 5 Rows ---")
print(spotify_history.head())

print("\n--- Dataset Shape ---")
print(spotify_history.shape)

print("\n--- Column Names ---")
print(spotify_history.columns)

print("\n--- Dataset Info ---")
spotify_history.info()

print("\n--- Missing Values ---")
print(spotify_history.isnull().sum())

## quality checks

print("\n--- Duplicate Rows ---")
print(spotify_history.duplicated().sum())

print("\n--- Listening Duration Statistics (ms) ---")
print(spotify_history["ms_played"].describe())

print("\n--- Zero or Negative Listening Durations ---")
print((spotify_history["ms_played"] <= 0).sum())

print("\n--- Skipped Track Counts ---")
print(spotify_history["skipped"].value_counts())

print("\n--- Shuffle Counts ---")
print(spotify_history["shuffle"].value_counts())

print("\n--- Timestamp Range ---")
print(spotify_history["ts"].min())
print(spotify_history["ts"].max())

######## data cleaning & new features ########

## copy of the raw dataset
spotify_clean = spotify_history.copy()

## converting the timestamp to datetime
spotify_clean["ts"] = pd.to_datetime(spotify_clean["ts"])

## converting listening time from milliseconds to minutes
spotify_clean["minutes_played"] = spotify_clean["ms_played"] / 60000

## creating date-related variables
spotify_clean["date"] = spotify_clean["ts"].dt.date
spotify_clean["year"] = spotify_clean["ts"].dt.year
spotify_clean["month"] = spotify_clean["ts"].dt.month
spotify_clean["hour"] = spotify_clean["ts"].dt.hour
spotify_clean["day_of_week"] = spotify_clean["ts"].dt.day_name()

## flagging duplicate records (without removing them yet)
spotify_clean["duplicate_flag"] = spotify_clean.duplicated()

## also flagging zero-duration records
spotify_clean["zero_duration_flag"] = spotify_clean["ms_played"] == 0

## now inspecting the cleaned dataset
print("\n--- Cleaned Dataset Preview ---")
print(spotify_clean.head())

print("\n--- Updated Data Types ---")
print(spotify_clean.dtypes)

print("\n--- Duplicate Flags ---")
print(spotify_clean["duplicate_flag"].value_counts())

print("\n--- Zero-Duration Flags ---")
print(spotify_clean["zero_duration_flag"].value_counts())


######## duplicates??? ########

## compare duplicate vs non-duplicate records
print("\n--- Duplicate vs Non-Duplicate Duration ---")
print(
    spotify_clean.groupby("duplicate_flag")["ms_played"]
    .describe()
)

## then compare duplicate vs non-duplicate skip behavior
print("\n--- Duplicate vs Non-Duplicate Skip Rate ---")
print(
    spotify_clean.groupby("duplicate_flag")["skipped"]
    .mean()
)

## display sample duplicates
print("\n--- Duplicate Sample ---")
print(
    spotify_clean[spotify_clean["duplicate_flag"]][
        ["ts", "track_name", "artist_name", "ms_played", "skipped"]
    ].head(15)
)

## what the duplicate investigation tells us --- Non-duplicate skip rate = 5.29% 
## vs Duplicate skip rate = 0.08%

## keeping duplicates for now, but will remove them later if needed. 
## the duplicates are likely due to the same track being played multiple times in a row, which is common behavior on Spotify.

######## eda ########

######## how has listening changed over time? ########

## create weekday/weekend variable
spotify_clean["day_type"] = spotify_clean["ts"].dt.dayofweek.map(
    lambda day: "Weekend" if day >= 5 else "Weekday"
)

## annual listening activity
annual_listening = spotify_clean.groupby("year").agg(
    total_streams=("spotify_track_uri", "count"),
    total_minutes=("minutes_played", "sum"),
    unique_artists=("artist_name", "nunique"),
    unique_tracks=("spotify_track_uri", "nunique")
).reset_index()

print("\n--- Annual Listening Summary ---")
print(annual_listening.to_string(index=False))

## monthly listening activity
monthly_listening = spotify_clean.groupby(
    ["year", "month"]
).agg(
    total_streams=("spotify_track_uri", "count"),
    total_minutes=("minutes_played", "sum")
).reset_index()

print("\n--- Monthly Listening Summary (First 15 Rows) ---")
print(monthly_listening.head(15).to_string(index=False))

## weekday vs weekend
day_comparison = spotify_clean.groupby("day_type").agg(
    total_streams=("spotify_track_uri", "count"),
    total_minutes=("minutes_played", "sum"),
    average_minutes=("minutes_played", "mean")
).reset_index()

print("\n--- Weekday vs Weekend ---")
print(day_comparison.to_string(index=False))

######## daily listening analysis ########

## summarize listening by calendar date
daily_listening = spotify_clean.groupby("date").agg(
    total_streams=("spotify_track_uri", "count"),
    total_minutes=("minutes_played", "sum")
).reset_index()

## add weekday/weekend classification
daily_listening["day_type"] = pd.to_datetime(
    daily_listening["date"]
).dt.dayofweek.map(
    lambda day: "Weekend" if day >= 5 else "Weekday"
)

## compare average activity per recorded calendar day
daily_comparison = daily_listening.groupby("day_type").agg(
    number_of_days=("date", "count"),
    average_streams_per_day=("total_streams", "mean"),
    average_minutes_per_day=("total_minutes", "mean")
).reset_index()

print("\n--- Average Listening Per Calendar Day ---")
print(daily_comparison.to_string(index=False))


######## annual listening per recorded day ########

daily_listening["year"] = pd.to_datetime(
    daily_listening["date"]
).dt.year

annual_daily = daily_listening.groupby("year").agg(
    recorded_days=("date", "count"),
    average_minutes_per_day=("total_minutes", "mean"),
    average_streams_per_day=("total_streams", "mean")
).reset_index()

print("\n--- Annual Average Listening Per Recorded Day ---")
print(annual_daily.to_string(index=False))


import matplotlib.pyplot as plt
import os

# create a folder for the graphs
os.makedirs("analysis_output/figures", exist_ok=True)



###### graph 1: total listening minutes by year ######

plt.figure(figsize=(10, 5))

plt.plot(
    annual_listening["year"],
    annual_listening["total_minutes"],
    marker="o"
)

plt.title("Total Spotify Listening Time by Year")
plt.xlabel("Year")
plt.ylabel("Total Listening Minutes")
plt.xticks(annual_listening["year"])
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    "analysis_output/figures/annual_listening_minutes.png",
    dpi=300
)
plt.show()


###### graph 2: average listening ######

plt.figure(figsize=(10, 5))

plt.plot(
    annual_daily["year"],
    annual_daily["average_minutes_per_day"],
    marker="o"
)

plt.title("Average Daily Listening Time by Year")
plt.xlabel("Year")
plt.ylabel("Average Minutes per Recorded Day")
plt.xticks(annual_daily["year"])
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    "analysis_output/figures/average_daily_listening.png",
    dpi=300
)
plt.show()

###### graph 3 weekday vs. weekend ######

plt.figure(figsize=(8, 5))

plt.bar(
    daily_comparison["day_type"],
    daily_comparison["average_minutes_per_day"]
)

plt.title("Average Daily Listening: Weekday vs. Weekend")
plt.xlabel("Day Type")
plt.ylabel("Average Listening Minutes")
plt.tight_layout()

plt.savefig(
    "analysis_output/figures/weekday_weekend_comparison.png",
    dpi=300
)
plt.show()


###### graph 4 ######

quality_counts = pd.Series({
    "Exact Duplicates": spotify_clean["duplicate_flag"].sum(),
    "Zero-Duration Records": spotify_clean["zero_duration_flag"].sum()
})

plt.figure(figsize=(8, 5))

plt.bar(
    quality_counts.index,
    quality_counts.values
)

plt.title("Data Quality: Records Flagged for Investigation")
plt.xlabel("Record Type")
plt.ylabel("Number of Records")
plt.tight_layout()

plt.savefig(
    "analysis_output/figures/data_quality_flags.png",
    dpi=300
)
plt.show()


###### top songs and albums ######
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


## top tracks

top_tracks = (
    spotify_history.groupby(["track_name", "artist_name"])
    .size()
    .reset_index(name="streams")
    .sort_values("streams", ascending=False)
    .head(10)
)

top_tracks["label"] = (
    top_tracks["track_name"] + " - " + top_tracks["artist_name"]
)

plt.figure(figsize=(12, 7))

plt.barh(top_tracks["label"][::-1], top_tracks["streams"][::-1])

plt.title("Top 10 Most Played Tracks")
plt.xlabel("Number of Streams")
plt.ylabel("Track")
plt.tight_layout()

plt.savefig("analysis_output/top_tracks.png", dpi=300)
plt.close()


## top albums

top_albums = (
    spotify_history.groupby(["album_name", "artist_name"])
    .size()
    .reset_index(name="streams")
    .sort_values("streams", ascending=False)
    .head(10)
)

top_albums["label"] = (
    top_albums["album_name"] + " - " + top_albums["artist_name"]
)

plt.figure(figsize=(12, 7))

plt.barh(top_albums["label"][::-1], top_albums["streams"][::-1])

plt.title("Top 10 Most Played Albums")
plt.xlabel("Number of Streams")
plt.ylabel("Album")
plt.tight_layout()

plt.savefig("analysis_output/top_albums.png", dpi=300)
plt.close()

print("Top tracks and top albums figures saved.")