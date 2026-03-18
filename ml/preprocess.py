"""
preprocess.py — GSS Data Preprocessing Utilities
=================================================
Handles raw CSV export from InfluxDB or direct ADC readings:
  - ADC → voltage conversion
  - Noise filtering (rolling median)
  - Min-max normalization
  - Label encoding for RF classifier
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, LabelEncoder


SENSOR_COLS = ["mq3_v", "mq4_v", "mq5_v", "mq6_v", "mq7_v", "mq8_v",
               "temp", "humidity"]

LABEL_CLASSES = ["Normal", "Dangerous", "Recovery"]


def load_csv(path: str) -> pd.DataFrame:
    """Load a CSV with at minimum SENSOR_COLS + 'label' columns."""
    df = pd.read_csv(path, parse_dates=["time"] if "time" in pd.read_csv(path, nrows=0).columns else False)
    df.dropna(subset=SENSOR_COLS, inplace=True)
    return df


def adc_to_voltage(raw: np.ndarray, adc_max: int = 4095, vref: float = 3.3) -> np.ndarray:
    """Convert raw ESP32 ADC readings to voltage."""
    return raw * (vref / adc_max)


def apply_rolling_median(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Smooth sensor readings to suppress transient noise spikes."""
    df[SENSOR_COLS] = df[SENSOR_COLS].apply(
        lambda col: col.rolling(window, center=True, min_periods=1).median()
    )
    return df


def normalize(df: pd.DataFrame, scaler: MinMaxScaler = None):
    """
    Min-max normalize SENSOR_COLS to [0, 1].
    Returns (normalized_df, fitted_scaler).
    Pass an existing scaler to transform test data consistently.
    """
    if scaler is None:
        scaler = MinMaxScaler()
        df[SENSOR_COLS] = scaler.fit_transform(df[SENSOR_COLS])
    else:
        df[SENSOR_COLS] = scaler.transform(df[SENSOR_COLS])
    return df, scaler


def encode_labels(series: pd.Series, encoder: LabelEncoder = None):
    """
    Encode string labels → integers.
    Returns (encoded_array, fitted_encoder).
    """
    if encoder is None:
        encoder = LabelEncoder()
        encoder.fit(LABEL_CLASSES)
    return encoder.transform(series), encoder


def full_pipeline(csv_path: str, scaler=None, encoder=None):
    """
    End-to-end preprocessing.
    Returns X (np.ndarray), y (np.ndarray), scaler, encoder.
    """
    df = load_csv(csv_path)
    df = apply_rolling_median(df)
    df, scaler = normalize(df, scaler)
    y, encoder = encode_labels(df["label"], encoder)
    X = df[SENSOR_COLS].values
    return X, y, scaler, encoder
