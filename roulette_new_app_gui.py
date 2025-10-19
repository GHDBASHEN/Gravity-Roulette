# roulette_app_gui.py

import tkinter as tk
from tkinter import messagebox
from collections import Counter
import pandas as pd
import os
import sys
import subprocess # Used to run the ML scripts

# --- CONFIGURATION ---
EXCEL_FILE = 'roulette_history.xlsx'
EXPORTER_SCRIPT = 'roulette_exporter.py' # Script for training/saving the model
PREDICTOR_SCRIPT = 'roulette_new_predictor.py' # Script for loading and predicting (fast)

class RouletteAnalyzer:
    """
    Handles history loading, saving, and deterministic pattern analysis.
    The ML logic is delegated to external scripts.
    """
    def __init__(self, wheel_type='european'):
        self.wheel_type = wheel_type
        self.spin_history = []
        self.numbers = list(range(37))
        
        # Color mapping for European roulette
        self.color_map = {
            **{i: 'red' for i in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]},
            **{i: 'black' for i in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]},
            **{0: 'green'}
        }

    def get_color(self, number):
        return self.color_map.get(number, 'unknown')

    def load_history_from_excel(self):
        """Loads all spin data from the Excel file."""
        if not os.path.exists(EXCEL_FILE):
            self.spin_history = []
            return 0
        try:
            df = pd.read_excel(EXCEL_FILE)
            if 'Number' in df.columns:
                self.spin_history = df['Number'].astype(int).tolist()
                return len(self.spin_history)
            else:
                self.spin_history = []
                return 0
        except Exception:
            self.spin_history = []
            return 0

    def save_spin_to_excel(self, number):
        """Appends a new spin and its color to the Excel file."""
        color = self.get_color(number)
        
        new_data = pd.DataFrame({
            'Timestamp': [pd.Timestamp.now()],
            'Number': [number],
            'Color': [color]
        })

        if os.path.exists(EXCEL_FILE):
            try:
                df_existing = pd.read_excel(EXCEL_FILE)
                df_updated = pd.concat([df_existing, new_data], ignore_index=True)
            except Exception:
                 # Handle corrupted/empty file by creating new DataFrame
                 df_updated = new_data
        else:
            df_updated = new_data
            
        try:
            df_updated.to_excel(EXCEL_FILE, index=False)
            self.spin_history.append(number) 
            return True
        except Exception as e:
            messagebox.showerror("File Error", f"Could not save data to Excel: {e}")
            return False

    def get_recent_spins(self, count=20):
        return self.spin_history[-count:] if self.spin_history else []

    def _get_current_streak(self, colors):
        if not colors:
            return {'color': None, 'length': 0}
        current_color = colors[-1]
        streak_length = 1
        for color in reversed(colors[:-1]):
            if color == current_color:
                streak_length += 1
            else:
                break
        return {'color': current_color, 'length': streak_length}

    def analyze_patterns(self, lookback=20):
        """Analyzes patterns (Gambler's Fallacy bias) for the top display."""
        if len(self.spin_history) < 5:
            return {"error": f"Not enough data. Current: {len(self.spin_history)}"}

        recent = self.get_recent_spins(min(lookback, len(self.spin_history)))
        recent_colors = [self.get_color(num) for num in recent]
        
        color_count = Counter(recent_colors)
        
        red_count = color_count.get('red', 0)
        black_count = color_count.get('black', 0)
        
        prediction = "No clear pattern"
        if red_count > black_count + 3:
            prediction = "BLACK (White) appears due"
        elif black_count > red_count + 3:
            prediction = "RED appears due"
        
        return {
            'next_bet_suggestion': prediction,
            'color_stats': color_count,
            'current_streak': self._get_current_streak(recent_colors),
            'last_spin': self.spin_history[-1],
            'last_color': self.get_color(self.spin_history[-1]).upper(),
            'total_spins': len(self.spin_history)
        }
# END OF RouletteAnalyzer CLASS

class RouletteGUI:
    def __init__(self, master):
        self.master = master
        master.title("Roulette Predictor with Excel Storage")
        master.geometry("550x550")
        
        self.analyzer = RouletteAnalyzer('european')
        self.analyzer.load_history_from_excel()
        
        # --- GUI Elements Setup ---
        
        self.spin_frame = tk.LabelFrame(master, text="Insert New Spin Result (0-36) and Save", padx=10, pady=10)
        self.spin_frame.pack(padx=10, pady=10, fill="x")
        
        self.spin_label = tk.Label(self.spin_frame, text="Number:")
        self.spin_label.pack(side="left")
        
        self.spin_entry = tk.Entry(self.spin_frame, width=5)
        self.spin_entry.pack(side="left", padx=5)
        
        self.add_button = tk.Button(self.spin_frame, text="Add Spin, Save & ML Analyze", command=self.add_and_analyze)
        self.add_button.pack(side="left", padx=10)
        
        self.file_label = tk.Label(self.spin_frame, text=f"File: {EXCEL_FILE}", fg='gray')
        self.file_label.pack(side="right")
        
        # --- Results Display Frame ---
        self.results_frame = tk.LabelFrame(master, text="Prediction Analysis", padx=10, pady=10)
        self.results_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Pattern Analysis Section (Top)
        self.pattern_header = tk.Label(self.results_frame, text="1. Pattern Bias Prediction (Last 20)", font=('Arial', 12, 'underline'))
        self.pattern_header.pack(pady=(5, 0))
        
        self.total_spins_label = tk.Label(self.results_frame, text="", font=('Arial', 10, 'italic'))
        self.total_spins_label.pack(pady=2)

        self.last_spin_label = tk.Label(self.results_frame, text="", font=('Arial', 12, 'bold'))
        self.last_spin_label.pack(pady=5)
        
        self.bet_value_label = tk.Label(self.results_frame, text="---", font=('Arial', 14, 'bold'), bg='lightgray', width=30)
        self.bet_value_label.pack(pady=5)
        
        self.stats_label = tk.Label(self.results_frame, justify=tk.LEFT, text="")
        self.stats_label.pack(pady=5)
        
        # ML Analysis Section (Bottom)
        self.ml_header = tk.Label(self.results_frame, text="\n2. LSTM Machine Learning Prediction", font=('Arial', 12, 'underline'))
        self.ml_header.pack(pady=(10, 0))
        
        self.ml_prediction_label = tk.Label(self.results_frame, text="ML Prediction: ---", font=('Arial', 14, 'bold'), fg='purple')
        self.ml_prediction_label.pack(pady=5)

        self.ml_probabilities_label = tk.Label(self.results_frame, justify=tk.LEFT, text="Probabilities: N/A")
        self.ml_probabilities_label.pack(pady=5)

        # Initial Analysis on Load
        self.update_gui()

    def run_ml_exporter(self):
        """Executes the external script to train and save the model."""
        try:
            result = subprocess.run([sys.executable, EXPORTER_SCRIPT], 
                                    capture_output=True, text=True, check=True)
            output_dict = eval(result.stdout.strip())
            return output_dict
            
        except subprocess.CalledProcessError as e:
            error_message = f"ML Export Script Error: {e.stderr.strip()}"
            return {"error": error_message, "prediction": "No Prediction"}
        except Exception as e:
            return {"error": f"Internal Export Error: {e}", "prediction": "No Prediction"}

    def run_ml_predictor(self):
        """Executes the external script to load the model and predict."""
        try:
            result = subprocess.run([sys.executable, PREDICTOR_SCRIPT], 
                                    capture_output=True, text=True, check=True)
            output_dict = eval(result.stdout.strip())
            return output_dict
            
        except subprocess.CalledProcessError as e:
            error_message = f"ML Predictor Script Error: {e.stderr.strip()}"
            return {"error": error_message, "prediction": "No Prediction"}
        except Exception as e:
            return {"error": f"Internal Predictor Error: {e}", "prediction": "No Prediction"}


    def add_and_analyze(self):
        """Handles the button click: Save new spin, train the model, and predict."""
        try:
            new_number = int(self.spin_entry.get())
            if 0 <= new_number <= 36:
                if self.analyzer.save_spin_to_excel(new_number):
                    self.spin_entry.delete(0, tk.END)
                    self.update_gui() # Update pattern bias display
                    
                    # 1. RUN EXPORTER (Train & Save Model)
                    export_result = self.run_ml_exporter()
                    
                    # 2. RUN PREDICTOR (Load & Predict)
                    ml_result = self.run_ml_predictor()
                    
                    self.update_ml_gui(ml_result)
                    
                    if export_result.get('status') == 'error':
                        messagebox.showerror("ML Error", export_result.get('message'))
                    else:
                        messagebox.showinfo("Success", f"Spin {new_number} saved and model re-trained.")
            else:
                messagebox.showerror("Invalid Input", "Roulette number must be between 0 and 36.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer (0-36).")
            
    def update_gui(self):
        """Updates the standard pattern analysis section."""
        analysis = self.analyzer.analyze_patterns()
        
        self.total_spins_label.config(text=f"Total Spins in History: {len(self.analyzer.spin_history)}")

        if 'error' in analysis:
            self.bet_value_label.config(text="NEED MORE DATA", bg='red', fg='white')
            self.last_spin_label.config(text=analysis['error'], bg='lightgray')
            self.stats_label.config(text="")
            return

        last_spin = analysis['last_spin']
        last_color = analysis['last_color']
        color_code = {'RED': 'red', 'BLACK': 'black', 'GREEN': 'green'}.get(last_color, 'white')
        
        self.last_spin_label.config(
            text=f"Last Spin: {last_spin} ({last_color})",
            bg=color_code,
            fg='white' if color_code != 'green' and color_code != 'black' else 'white' if color_code == 'black' else 'black' 
        )

        prediction = analysis['next_bet_suggestion']
        self.bet_value_label.config(text=prediction.upper(), fg='black', bg='yellow' if "pattern" in prediction.lower() else 'lightgreen' if "red" in prediction.lower() else 'gray')

        stats_text = f"Current Streak: {analysis['current_streak']['color'].upper()} - {analysis['current_streak']['length']} spins\n"
        stats_text += "Color Distribution (Last 20 Spins):\n"
        color_count = analysis['color_stats']
        for color in ['red', 'black', 'green']:
            count = color_count.get(color, 0)
            display_color = color.upper() if color != 'black' else "BLACK (WHITE)"
            stats_text += f"  {display_color}: {count} spins\n"
        
        self.stats_label.config(text=stats_text)

    def update_ml_gui(self, ml_result):
        """Updates the ML prediction section."""
        if 'error' in ml_result:
            self.ml_prediction_label.config(text=f"ML Status: {ml_result['error']}", fg='red')
            self.ml_probabilities_label.config(text="Probabilities: N/A")
            return
            
        prediction = ml_result['prediction']
        probs = ml_result['probabilities']
        
        pred_color = {'RED': 'red', 'BLACK': 'black', 'GREEN': 'green'}.get(prediction, 'black')
        
        self.ml_prediction_label.config(
            text=f"ML PREDICTS: {prediction}!", 
            font=('Arial', 16, 'bold'),
            fg=pred_color
        )
        
        probs_text = "\n".join([f"{k}: {v}" for k, v in probs.items()])
        self.ml_probabilities_label.config(text=f"Probabilities:\n{probs_text}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RouletteGUI(root)
    
    # Perform initial ML analysis on load
    ml_initial_result = app.run_ml_predictor()
    app.update_ml_gui(ml_initial_result)
    
    root.mainloop()