# roulette_exporter.py
import pandas as pd
import numpy as np
import random
import sys
import os
import pickle # Used to save the LabelEncoder

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import set_random_seed
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# --- CONFIGURATION ---
EXCEL_FILE = 'roulette_history.xlsx'
MODEL_FILE = 'roulette_model.h5'
ENCODER_FILE = 'label_encoder.pkl' # New file to save the encoder
SEED_VALUE = 42
SEQUENCE_LENGTH = 10 

def set_fixed_seeds(seed_value):
    os.environ['PYTHONHASHSEED'] = str(seed_value)
    random.seed(seed_value)
    np.random.seed(seed_value)
    set_random_seed(seed_value)

def create_sequences(data, sequence_length):
    X, y = [], []
    for i in range(len(data) - sequence_length):
        X.append(data[i:i + sequence_length])
        y.append(data[i + sequence_length])
    return np.array(X), np.array(y)

def train_and_export():
    """Trains the model and saves both the model and the LabelEncoder."""
    
    set_fixed_seeds(SEED_VALUE)
    
    if not os.path.exists(EXCEL_FILE):
        return {"status": "error", "message": "History file not found."}

    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty or len(df) < SEQUENCE_LENGTH + 1:
            return {"status": "error", "message": "Not enough data (need > 11 spins) for training."}

        # 1. DATA PREPARATION
        colors_raw = df['Color'].tolist()
        le = LabelEncoder()
        colors_encoded = le.fit_transform(colors_raw)
        
        X_seq, y_labels = create_sequences(colors_encoded, SEQUENCE_LENGTH)
        X_seq = X_seq.reshape(X_seq.shape[0], X_seq.shape[1], 1)
        
        # 2. MODEL BUILDING AND TRAINING
        model = Sequential([
            LSTM(50, activation='relu', input_shape=(SEQUENCE_LENGTH, 1)),
            Dense(len(le.classes_), activation='softmax')
        ])
        
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        
        X_train, _, y_train, _ = train_test_split(X_seq, y_labels, test_size=0.1, random_state=SEED_VALUE)
        
        model.fit(X_train, y_train, epochs=10, batch_size=1, verbose=0)
        
        # 3. EXPORT MODEL and ENCODER
        model.save(MODEL_FILE)
        with open(ENCODER_FILE, 'wb') as file:
            pickle.dump(le, file)
        
        return {"status": "success", "total_spins": len(df)}

    except Exception as e:
        return {"status": "error", "message": f"ML Export Error: {e}"}

if __name__ == '__main__':
    # This script is called by the GUI to train and save the model
    result = train_and_export()
    print(result) # Print for the GUI to capture