from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "spotify_history.csv"
OUTPUT_DIR = Path(__file__).parent / "analysis_output"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    df["ts"] = pd.to_datetime(df["ts"], errors="coerce")
    df["minutes_played"] = df["ms_played"] / 60_000
    df["date"] = df["ts"].dt.date
    df["hour"] = df["ts"].dt.hour
    df["weekday"] = df["ts"].dt.day_name()
    df["year"] = df["ts"].dt.year
    df["month"] = df["ts"].dt.to_period("M").astype("string")

    print(f"Rows: {len(df):,}")
    print(f"Date range: {df['ts'].min()} to {df['ts'].max()}")
    print(f"Unique tracks: {df['track_name'].nunique():,}")
    print(f"Unique artists: {df['artist_name'].nunique():,}")
    print(f"Total listening time: {df['minutes_played'].sum() / 60:,.1f} hours")
    print(f"Skipped rows: {df['skipped'].fillna(False).sum():,}")

    top_tracks = (
        df.groupby(["track_name", "artist_name"], dropna=False)
        .agg(plays=("spotify_track_uri", "size"), minutes=("minutes_played", "sum"))
        .sort_values("minutes", ascending=False)
        .head(20)
    )
    top_artists = (
        df.groupby("artist_name", dropna=False)["minutes_played"]
        .sum()
        .sort_values(ascending=False)
        .head(20)
    )

    top_tracks.to_csv(OUTPUT_DIR / "top_tracks.csv")
    top_artists.to_csv(OUTPUT_DIR / "top_artists.csv", header=["minutes_played"])

    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(12, 7))
    top_artists.sort_values().plot(kind="barh", ax=ax, color="#1DB954")
    ax.set(title="Top 20 Artists by Listening Time", xlabel="Minutes Played", ylabel="Artist")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "top_artists.png", dpi=150)
    plt.close(fig)

    hourly = df.groupby("hour")["minutes_played"].sum()
    fig, ax = plt.subplots(figsize=(12, 6))
    hourly.plot(kind="bar", ax=ax, color="#1DB954")
    ax.set(title="Listening Time by Hour", xlabel="Hour of Day", ylabel="Minutes Played")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "listening_by_hour.png", dpi=150)
    plt.close(fig)

    monthly = df.groupby("month")["minutes_played"].sum()
    monthly = monthly[monthly.index.notna()].sort_index()
    fig, ax = plt.subplots(figsize=(14, 6))
    monthly.plot(kind="line", marker="o", ax=ax, color="#1DB954")
    ax.set(title="Listening Time by Month", xlabel="Month", ylabel="Minutes Played")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "listening_by_month.png", dpi=150)
    plt.close(fig)

    print(f"Analysis outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
