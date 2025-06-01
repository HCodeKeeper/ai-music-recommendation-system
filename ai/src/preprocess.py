from __future__ import annotations
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, LabelEncoder, LabelBinarizer, MultiLabelBinarizer
from typing import Tuple
from pathlib import Path

from config import (
    SCALER_RANGE, ARTIST_WEIGHT, YEAR_WEIGHT, TAGS_WEIGHT, GENRE_WEIGHT,
    DURATION_MS_WEIGHT, DANCEABILITY_WEIGHT, ENERGY_WEIGHT, KEY_WEIGHT,
    LOUDNESS_WEIGHT, MODE_WEIGHT, SPEECHINESS_WEIGHT, ACOUSTICNESS_WEIGHT,
    INSTRUMENTALNESS_WEIGHT, LIVENESS_WEIGHT, VALENCE_WEIGHT, TEMPO_WEIGHT,
    TIME_SIGNATURE_WEIGHT
)

class DataPreprocessor:
    """Prepare Music Info data for ML models."""

    NUMERIC_COLS = [
        'duration_ms', 'danceability', 'energy', 'key',
        'loudness', 'mode', 'speechiness', 'acousticness',
        'instrumentalness', 'liveness', 'valence', 'tempo',
        'time_signature',
    ]

    COLS_TO_DROP = [
        'name', 'spotify_preview_url', 'spotify_id', 'pathToTrack'
    ]
    
    # Feature weights mapping
    FEATURE_WEIGHTS = {
        'duration_ms': DURATION_MS_WEIGHT,
        'danceability': DANCEABILITY_WEIGHT,
        'energy': ENERGY_WEIGHT,
        'key': KEY_WEIGHT,
        'loudness': LOUDNESS_WEIGHT,
        'mode': MODE_WEIGHT,
        'speechiness': SPEECHINESS_WEIGHT,
        'acousticness': ACOUSTICNESS_WEIGHT,
        'instrumentalness': INSTRUMENTALNESS_WEIGHT,
        'liveness': LIVENESS_WEIGHT,
        'valence': VALENCE_WEIGHT,
        'tempo': TEMPO_WEIGHT,
        'time_signature': TIME_SIGNATURE_WEIGHT,
    }

    def __init__(self, genre_col: str = 'genre', artist_col: str = 'artist',
                 track_id_col: str = 'track_id', year_col: str = 'year'):
        self.genre_col = genre_col
        self.artist_col = artist_col
        self.track_id_col = track_id_col
        self.year_col = year_col
        self.scaler: MinMaxScaler | None = None
        self.label_encoder: LabelEncoder | None = None
        self.tags_encoder: LabelBinarizer | MultiLabelBinarizer | None = None
        self._genre_cols: list[str] = []
        self._tags_cols: list[str] = []
        self._has_multi_tags: bool = False

    def fit_transform(self, path: str | Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Read CSV -> returns (raw_df, encoded_df)."""
        raw_df = pd.read_csv(path)
        return self.fit_transform_dataframe(raw_df)
    
    def fit_transform_dataframe(self, raw_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Process DataFrame directly -> returns (raw_df, encoded_df)."""
        # Create encoded copy and drop unnecessary columns
        df = raw_df.copy()
        
        # Only drop columns that exist in the DataFrame
        cols_to_drop = [col for col in self.COLS_TO_DROP if col in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)
        
        # Handle tags if present
        if 'tags' in df.columns:
            df['tags'] = df['tags'].fillna('unknown')
            
            # Check if any tags contain commas (multiple tags)
            has_comma_tags = df['tags'].str.contains(',', na=False).any()
            self._has_multi_tags = has_comma_tags
            
            if has_comma_tags:
                # Multiple tags case: use MultiLabelBinarizer
                print("Detected comma-separated tags, using MultiLabelBinarizer")
                
                # Convert comma-separated strings to lists
                tag_lists = df['tags'].apply(lambda x: [tag.strip() for tag in str(x).split(',') if tag.strip()])
                
                # Fit and transform with MultiLabelBinarizer
                self.tags_encoder = MultiLabelBinarizer()
                tags_encoded = self.tags_encoder.fit_transform(tag_lists)
                
                # Create DataFrame with tag columns
                tag_feature_names = [f'tags_{tag}' for tag in self.tags_encoder.classes_]
                tags_df = pd.DataFrame(tags_encoded, columns=tag_feature_names, index=df.index)
                
                # Drop original tags column and concatenate encoded tags
                df = df.drop(columns=['tags'])
                df = pd.concat([df, tags_df], axis=1)
                
                self._tags_cols = tag_feature_names
            else:
                # Single tag case: use LabelBinarizer
                print("Detected single tags, using LabelBinarizer")
                
                self.tags_encoder = LabelBinarizer()
                tags_encoded = self.tags_encoder.fit_transform(df['tags'])
                
                # Create DataFrame with tag columns
                if tags_encoded.shape[1] == 1:
                    # Binary case (only 2 unique tags)
                    tag_feature_names = [f'tags_{self.tags_encoder.classes_[1]}']
                else:
                    # Multi-class case
                    tag_feature_names = [f'tags_{tag}' for tag in self.tags_encoder.classes_]
                
                tags_df = pd.DataFrame(tags_encoded, columns=tag_feature_names, index=df.index)
                
                # Drop original tags column and concatenate encoded tags
                df = df.drop(columns=['tags'])
                df = pd.concat([df, tags_df], axis=1)
                
                self._tags_cols = tag_feature_names
            
            # Apply tags weight to all tag columns
            for col in self._tags_cols:
                df[col] = df[col] * TAGS_WEIGHT
        
        # Handle genre
        df[self.genre_col] = df[self.genre_col].fillna('unknown')
        df = pd.get_dummies(df, columns=[self.genre_col], prefix=[self.genre_col])
        self._genre_cols = [c for c in df.columns if c.startswith(f"{self.genre_col}_")]
        # Apply genre weight to all genre columns
        for col in self._genre_cols:
            df[col] = df[col] * GENRE_WEIGHT
        
        # Handle artist
        self.label_encoder = LabelEncoder()
        df[self.artist_col] = self.label_encoder.fit_transform(df[self.artist_col])
        
        # Convert booleans to numeric
        df = df.replace({True: 1, False: 0})
        
        # Scale numeric columns individually and apply their specific weights
        numeric_cols_to_scale = [col for col in self.NUMERIC_COLS if col in df.columns]
        if numeric_cols_to_scale:
            self.scaler = MinMaxScaler(feature_range=SCALER_RANGE)
            df[numeric_cols_to_scale] = self.scaler.fit_transform(df[numeric_cols_to_scale])
            
            # Apply individual weights to each audio feature
            for col in numeric_cols_to_scale:
                if col in self.FEATURE_WEIGHTS:
                    df[col] = df[col] * self.FEATURE_WEIGHTS[col]
        
        # Scale and weight artist and year
        if self.artist_col in df.columns:
            artist_scaler = MinMaxScaler(feature_range=SCALER_RANGE)
            df[self.artist_col] = artist_scaler.fit_transform(df[[self.artist_col]]) * ARTIST_WEIGHT
        
        if self.year_col in df.columns:
            year_scaler = MinMaxScaler(feature_range=SCALER_RANGE)
            df[self.year_col] = year_scaler.fit_transform(df[[self.year_col]]) * YEAR_WEIGHT
        
        # Ensure no missing values and reset index
        encoded_df = df.dropna().reset_index(drop=True)
        return raw_df, encoded_df

    def encode_new(self, new_songs: pd.DataFrame) -> pd.DataFrame:
        """Encode new songs with the fitted encoders/scaler."""
        if self.label_encoder is None or self.scaler is None:
            raise RuntimeError("Preprocessor must be fit before encoding new data.")
            
        df = new_songs.copy()
        df = df.drop(columns=[col for col in self.COLS_TO_DROP if col in df.columns])
        
        # Handle tags if present
        if 'tags' in df.columns and self.tags_encoder is not None:
            df['tags'] = df['tags'].fillna('unknown')
            
            if self._has_multi_tags:
                # Multiple tags case: use fitted MultiLabelBinarizer
                tag_lists = df['tags'].apply(lambda x: [tag.strip() for tag in str(x).split(',') if tag.strip()])
                tags_encoded = self.tags_encoder.transform(tag_lists)
                
                # Create DataFrame with tag columns
                tag_feature_names = [f'tags_{tag}' for tag in self.tags_encoder.classes_]
                tags_df = pd.DataFrame(tags_encoded, columns=tag_feature_names, index=df.index)
                
                # Drop original tags column and concatenate encoded tags
                df = df.drop(columns=['tags'])
                df = pd.concat([df, tags_df], axis=1)
            else:
                # Single tag case: use fitted LabelBinarizer
                tags_encoded = self.tags_encoder.transform(df['tags'])
                
                # Create DataFrame with tag columns
                if tags_encoded.shape[1] == 1:
                    # Binary case (only 2 unique tags)
                    tag_feature_names = [f'tags_{self.tags_encoder.classes_[1]}']
                else:
                    # Multi-class case
                    tag_feature_names = [f'tags_{tag}' for tag in self.tags_encoder.classes_]
                
                tags_df = pd.DataFrame(tags_encoded, columns=tag_feature_names, index=df.index)
                
                # Drop original tags column and concatenate encoded tags
                df = df.drop(columns=['tags'])
                df = pd.concat([df, tags_df], axis=1)
            
            # Align tag columns with training set
            for col in self._tags_cols:
                if col not in df.columns:
                    df[col] = 0
                else:
                    df[col] = df[col] * TAGS_WEIGHT
        
        # Handle genre
        df[self.genre_col] = df[self.genre_col].fillna('unknown')
        df = pd.get_dummies(df, columns=[self.genre_col], prefix=[self.genre_col])
        
        # Align genre columns with training set
        for col in self._genre_cols:
            if col not in df.columns:
                df[col] = 0
            else:
                df[col] = df[col] * GENRE_WEIGHT
                
        # Handle artist
        df[self.artist_col] = self.label_encoder.transform(df[self.artist_col])
        
        # Convert booleans to numeric
        df = df.replace({True: 1, False: 0})
        
        # Scale numeric features and apply individual weights
        numeric_cols_to_scale = [col for col in self.NUMERIC_COLS if col in df.columns]
        if numeric_cols_to_scale:
            df[numeric_cols_to_scale] = self.scaler.transform(df[numeric_cols_to_scale])
            
            # Apply individual weights to each audio feature
            for col in numeric_cols_to_scale:
                if col in self.FEATURE_WEIGHTS:
                    df[col] = df[col] * self.FEATURE_WEIGHTS[col]
        
        # Scale and weight artist and year
        if self.artist_col in df.columns:
            artist_scaler = MinMaxScaler(feature_range=SCALER_RANGE)
            df[self.artist_col] = artist_scaler.fit_transform(df[[self.artist_col]]) * ARTIST_WEIGHT
            
        if self.year_col in df.columns:
            year_scaler = MinMaxScaler(feature_range=SCALER_RANGE)
            df[self.year_col] = year_scaler.fit_transform(df[[self.year_col]]) * YEAR_WEIGHT
        
        return df

    @property
    def genre_dummy_cols(self) -> list[str]:
        """Get the list of genre dummy columns created during fit_transform."""
        return self._genre_cols.copy()  # Return a copy to prevent modification
    
    @property
    def tags_dummy_cols(self) -> list[str]:
        """Get the list of tags dummy columns created during fit_transform."""
        return self._tags_cols.copy()  # Return a copy to prevent modification