# roulette_trainer.py
import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import sys
import os

EXCEL_FILE = 'roulette_history.xlsx'

def get_color_map():
    """Returns the color mapping."""
    return {
        **{i: 'red' for i in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]},
        **{i: 'black' for i in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]},
        **{0: 'green'}
    }

def create_sequences(data, sequence_length):
    """Converts a flat list of numbers into input/output sequences for LSTM."""
    X, y = [], []
    # Loop until the second-to-last element to predict the next one
    for i in range(len(data) - sequence_length):
        # The input sequence is the numbers from i to i + sequence_length
        X.append(data[i:i + sequence_length])
        # The output (label) is the number immediately following the sequence
        y.append(data[i + sequence_length])
    return np.array(X), np.array(y)

def train_and_predict():
    """Main function to load data, train LSTM, and predict the next spin."""
    if not os.path.exists(EXCEL_FILE):
        return {"error": "History file not found. Cannot train model.", "prediction": "No Prediction"}

    try:
        df = pd.read_excel(EXCEL_FILE)
        if df.empty or len(df) < 20: # Need enough data for sequences
            return {"error": "Not enough data (need > 20 spins) to train LSTM.", "prediction": "No Prediction"}

        # 1. DATA PREPARATION
        # We need to predict the *outcome category* (color), so we use the 'Color' column
        colors_raw = df['Color'].tolist()

        # Encode colors to numerical values (Red: 0, Black: 1, Green: 2)
        le = LabelEncoder()
        colors_encoded = le.fit_transform(colors_raw)
        
        # Sequence length: how many past spins the model looks at (a hyperparameter)
        SEQUENCE_LENGTH = 10 
        
        X_seq, y_labels = create_sequences(colors_encoded, SEQUENCE_LENGTH)
        
        # Reshape X for LSTM input: [samples, timesteps, features] (features=1, as we only use color)
        X_seq = X_seq.reshape(X_seq.shape[0], X_seq.shape[1], 1)
        
        # 2. MODEL BUILDING AND TRAINING
        model = Sequential([
            LSTM(50, activation='relu', input_shape=(SEQUENCE_LENGTH, 1)),
            Dense(len(le.classes_), activation='softmax') # Output layer size = number of unique classes (3: R, B, G)
        ])
        
        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        
        # Use a small portion for validation (not strictly necessary for this prediction, but good practice)
        X_train, _, y_train, _ = train_test_split(X_seq, y_labels, test_size=0.1, random_state=42)
        
        # Train the model quickly (low epochs for fast response)
        model.fit(X_train, y_train, epochs=10, batch_size=1, verbose=0)
        
        # 3. PREDICTION
        # The input for prediction is the last SEQUENCE_LENGTH spins
        last_sequence = colors_encoded[-SEQUENCE_LENGTH:]
        X_predict = last_sequence.reshape(1, SEQUENCE_LENGTH, 1)
        
        # Get probabilities for all three classes
        probabilities = model.predict(X_predict, verbose=0)[0]
        
        # Get the index of the highest probability
        predicted_index = np.argmax(probabilities)
        
        # Decode the predicted index back to a color string
        predicted_color = le.inverse_transform([predicted_index])[0]
        
        # 4. FORMAT OUTPUT
        # Calculate probability percentages for display
        probabilities_dict = {
            le.inverse_transform([i])[0].upper(): f"{p*100:.2f}%" 
            for i, p in enumerate(probabilities)
        }
        
        return {
            "prediction": predicted_color.upper(),
            "probabilities": probabilities_dict
        }

    except Exception as e:
        # Catch any errors during data loading or training
        return {"error": f"ML Training Error: {e}", "prediction": "No Prediction"}

if __name__ == "__main__":
    # When this script is called from the main app, it runs this function
    result = train_and_predict()
    
    # Print the result as a simple string dictionary for the main app to capture
    print(result)