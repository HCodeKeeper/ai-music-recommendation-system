# Similar Item Recommendation System

A K-Nearest Neighbors based recommendation system for suggesting similar music tracks based on various audio features, artist, and year information.

## Installation

1. Clone the repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from src.model import SimilarItemRec

# Initialize the model
model = SimilarItemRec()

# Train the model with your music data
model.train(music_df)

# Get recommendations for a track
recommendations = model.get_full_recommendations("TRACK_ID")
```

### Example with Custom Weights

```python
# Initialize and train with custom weights for artist and year similarity
model = SimilarItemRec()
model.train(music_df, artist_weight=300, year_weight=30)

# Get recommendations
recommendations = model.get_full_recommendations("TRACK_ID", n_recommendations=10)
```

### Updating the Model

```python
# Add new music data to the existing model
model.update(new_music_df)
```

## Input Data Format

The model expects a pandas DataFrame with the following columns:

- track_id: Unique identifier for each track
- name: Track name
- artist: Artist name
- year: Release year
- genre: Music genre
- duration_ms: Duration in milliseconds
- danceability: Danceability score
- energy: Energy score
- key: Musical key
- loudness: Loudness in dB
- mode: Musical mode
- speechiness: Speechiness score
- acousticness: Acousticness score
- instrumentalness: Instrumentalness score
- liveness: Liveness score
- valence: Valence score
- tempo: Tempo in BPM
- time_signature: Time signature

## Model Features

- KNN-based similarity computation
- Customizable weights for artist and year influence
- Standardized audio features
- Support for model updates with new data
- Detailed recommendation information including similarity scores

## Return Format

The `get_full_recommendations` method returns a list of dictionaries, each containing:

```python
{
    'name': 'Track Name',
    'artist': 'Artist Name',
    'year': 2020,
    'distance': 0.123  # Similarity score (lower is more similar)
}
```
