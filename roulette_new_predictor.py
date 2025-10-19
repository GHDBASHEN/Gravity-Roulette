# roulette_predictor.py
import pandas as pd
import numpy as np
import sys
import os
import pickle
from tensorflow.keras.models import load_model # Used to load the saved model

# --- CONFIGURATION ---
EXCEL_FILE = 'roulette_history.xlsx'
MODEL_FILE = 'roulette_model.h5'
ENCODER_FILE = 'label_encoder.pkl'
SEQUENCE_LENGTH = 10 

def predict_from_saved_model():
    """Loads the model and makes a prediction on the latest data."""
    
    if not os.path.exists(MODEL_FILE) or not os.path.exists(ENCODER_FILE):
        return {"prediction": "No Prediction", "error": "Model or Encoder file missing. Retrain required."}

    try:
        # 1. Load Data
        df = pd.read_excel(EXCEL_FILE)
        colors_raw = df['Color'].tolist()
        
        # 2. Load Model and Encoder
        model = load_model(MODEL_FILE)
        with open(ENCODER_FILE, 'rb') as file:
            le = pickle.load(file)

        # 3. Prepare Prediction Input
        # NOTE: We must use the LabelEncoder to transform colors_raw to ensure we get the right numbers!
        colors_encoded = le.transform(colors_raw) 
        
        last_sequence = colors_encoded[-SEQUENCE_LENGTH:]
        X_predict = last_sequence.reshape(1, SEQUENCE_LENGTH, 1)
        
        # 4. Prediction
        probabilities = model.predict(X_predict, verbose=0)[0]
        predicted_index = np.argmax(probabilities)
        predicted_color = le.inverse_transform([predicted_index])[0]
        
        # 5. Format Output
        probabilities_dict = {
            le.inverse_transform([i])[0].upper(): f"{p*100:.2f}%" 
            for i, p in enumerate(probabilities)
        }
        
        return {
            "prediction": predicted_color.upper(),
            "probabilities": probabilities_dict,
            "error": None
        }

    except Exception as e:
        return {"prediction": "No Prediction", "error": f"Model Prediction Error: {e}"}

if __name__ == '__main__':
    result = predict_from_saved_model()
    print(result)