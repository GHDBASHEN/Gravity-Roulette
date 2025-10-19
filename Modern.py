import tkinter as tk
from tkinter import messagebox
from collections import Counter
import pandas as pd
import os # To check for file existence

# --- CONFIGURATION ---
EXCEL_FILE = 'roulette_history.xlsx' 

class RouletteAnalyzer:
    def __init__(self, wheel_type='european'):
        """
        Initialize the roulette analyzer for European Roulette.
        """
        self.wheel_type = wheel_type
        self.spin_history = []
        self.numbers = list(range(37))
        
        # Color mapping for European roulette (0=Green, 18 Red, 18 Black)
        self.color_map = {
            **{i: 'red' for i in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]},
            **{i: 'black' for i in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]},
            **{0: 'green'}
        }

    def get_color(self, number):
        """Get color for a number."""
        return self.color_map.get(number, 'unknown')

    # --- NEW EXCEL STORAGE METHODS ---

    def load_history_from_excel(self):
        """Loads all spin data from the Excel file."""
        if not os.path.exists(EXCEL_FILE):
            print(f"File not found: {EXCEL_FILE}. Starting with empty history.")
            self.spin_history = []
            return 0
        try:
            df = pd.read_excel(EXCEL_FILE)
            # Ensure the 'Number' column exists and is an integer list
            if 'Number' in df.columns:
                self.spin_history = df['Number'].astype(int).tolist()
                print(f"Successfully loaded {len(self.spin_history)} spins from Excel.")
                return len(self.spin_history)
            else:
                print("Error: 'Number' column missing in Excel file.")
                self.spin_history = []
                return 0
        except Exception as e:
            print(f"Error loading Excel file: {e}")
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
            # Read existing data and append the new spin
            df_existing = pd.read_excel(EXCEL_FILE)
            df_updated = pd.concat([df_existing, new_data], ignore_index=True)
        else:
            # Create a new file
            df_updated = new_data
            
        try:
            df_updated.to_excel(EXCEL_FILE, index=False)
            self.spin_history.append(number) # Update in-memory history
            return True
        except Exception as e:
            messagebox.showerror("File Error", f"Could not save data to Excel: {e}")
            return False

    # --- EXISTING ANALYSIS METHODS (Simplified) ---
    
    def get_recent_spins(self, count=20):
        """Get the most recent spins."""
        return self.spin_history[-count:] if self.spin_history else []

    def _get_current_streak(self, colors):
        """Get the current color streak."""
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
        """Analyze recent patterns and provide betting suggestions."""
        if len(self.spin_history) < 5:
            return {"error": f"Not enough data. Need at least 5 spins. Current: {len(self.spin_history)}"}

        recent = self.get_recent_spins(min(lookback, len(self.spin_history)))
        recent_colors = [self.get_color(num) for num in recent]
        
        color_count = Counter(recent_colors)
        
        # Color bias detection (Gambler's Fallacy logic)
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


class RouletteGUI:
    def __init__(self, master):
        self.master = master
        master.title("Roulette Predictor with Excel Storage")
        master.geometry("450x480")
        
        self.analyzer = RouletteAnalyzer('european')
        
        # --- INITIAL LOAD ---
        self.analyzer.load_history_from_excel()
        
        # --- GUI Elements Setup ---

        # 1. New Spin Input Frame
        self.spin_frame = tk.LabelFrame(master, text="Insert New Spin Result (0-36) and Save", padx=10, pady=10)
        self.spin_frame.pack(padx=10, pady=10, fill="x")
        
        self.spin_label = tk.Label(self.spin_frame, text="Number:")
        self.spin_label.pack(side="left")
        
        self.spin_entry = tk.Entry(self.spin_frame, width=5)
        self.spin_entry.pack(side="left", padx=5)
        
        self.add_button = tk.Button(self.spin_frame, text="Add Spin, Save & Analyze", command=self.add_and_analyze)
        self.add_button.pack(side="left", padx=10)
        
        self.file_label = tk.Label(self.spin_frame, text=f"File: {EXCEL_FILE}", fg='gray')
        self.file_label.pack(side="right")
        
        # 2. Results Display Frame
        self.results_frame = tk.LabelFrame(master, text="Analysis & Prediction (Last 20 Spins)", padx=10, pady=10)
        self.results_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.total_spins_label = tk.Label(self.results_frame, text="", font=('Arial', 10, 'italic'))
        self.total_spins_label.pack(pady=2)

        self.last_spin_label = tk.Label(self.results_frame, text="", font=('Arial', 12, 'bold'))
        self.last_spin_label.pack(pady=5)
        
        self.prediction_label = tk.Label(self.results_frame, text="NEXT BET PREDICTION:", font=('Arial', 14, 'bold'), fg='blue')
        self.prediction_label.pack(pady=10)
        
        self.bet_value_label = tk.Label(self.results_frame, text="---", font=('Arial', 18, 'bold'), bg='#f0f0f0', width=20)
        self.bet_value_label.pack(pady=5)
        
        self.streak_label = tk.Label(self.results_frame, text="Current Streak: N/A", font=('Arial', 10))
        self.streak_label.pack(pady=5)
        
        self.stats_label = tk.Label(self.results_frame, justify=tk.LEFT, text="")
        self.stats_label.pack(pady=10)
        
        # 3. Initial Analysis on Load
        self.update_gui()

    def add_and_analyze(self):
        """Handles the button click to add a spin, save it to Excel, and update the analysis."""
        try:
            new_number = int(self.spin_entry.get())
            if 0 <= new_number <= 36:
                # 1. Save to Excel
                if self.analyzer.save_spin_to_excel(new_number):
                    self.spin_entry.delete(0, tk.END) # Clear the input field
                    # 2. Analyze and Update GUI
                    self.update_gui()
                    messagebox.showinfo("Success", f"Spin {new_number} saved to {EXCEL_FILE}")
                # Else, the save_spin_to_excel method showed an error
            else:
                messagebox.showerror("Invalid Input", "Roulette number must be between 0 and 36.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer (0-36).")
            
    def update_gui(self):
        """Performs the analysis and updates all labels in the GUI."""
        analysis = self.analyzer.analyze_patterns()
        
        self.total_spins_label.config(text=f"Total Spins in History: {len(self.analyzer.spin_history)}")

        if 'error' in analysis:
            self.bet_value_label.config(text="NEED MORE DATA", bg='red', fg='white')
            self.last_spin_label.config(text=analysis['error'], bg='lightgray')
            self.streak_label.config(text="")
            self.stats_label.config(text="")
            return

        # 1. Last Spin Info
        last_spin = analysis['last_spin']
        last_color = analysis['last_color']
        color_code = {'RED': 'red', 'BLACK': 'black', 'GREEN': 'green'}.get(last_color, 'white')
        
        self.last_spin_label.config(
            text=f"Last Spin: {last_spin} ({last_color})",
            bg=color_code,
            fg='white' if color_code != 'green' and color_code != 'black' else 'white' if color_code == 'black' else 'black' 
        )

        # 2. Prediction
        prediction = analysis['next_bet_suggestion']
        
        self.bet_value_label.config(text=prediction.upper(), fg='black', bg='yellow')

        # 3. Streak
        streak_info = analysis['current_streak']
        self.streak_label.config(text=f"Current Streak: {streak_info['color'].upper()} - {streak_info['length']} spins")

        # 4. Detailed Stats (Last 20)
        stats_text = "Color Distribution (Last 20 Spins):\n"
        color_count = analysis['color_stats']
        for color in ['red', 'black', 'green']:
            count = color_count.get(color, 0)
            display_color = color.upper() if color != 'black' else "BLACK (WHITE)"
            stats_text += f"  {display_color}: {count} spins\n"
        
        self.stats_label.config(text=stats_text)


if __name__ == "__main__":
    # Ensure pandas and openpyxl are installed: pip install pandas openpyxl
    root = tk.Tk()
    app = RouletteGUI(root)
    root.mainloop()