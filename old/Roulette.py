import tkinter as tk
from tkinter import messagebox
from collections import Counter
from datetime import datetime

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

    def load_history(self, history_list):
        """Load an external history list."""
        self.spin_history = history_list

    def add_spin(self, number):
        """Add a single spin result to the history."""
        self.spin_history.append(number)

    def get_color(self, number):
        """Get color for a number."""
        return self.color_map.get(number, 'unknown')

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
            return {"error": "Not enough data. Need at least 5 spins."}

        recent = self.get_recent_spins(min(lookback, len(self.spin_history)))
        recent_colors = [self.get_color(num) for num in recent]
        
        analysis = {}
        
        # Color frequency analysis
        color_count = Counter(recent_colors)
        total_spins = len(recent_colors)
        
        # Color bias detection (Gambler's Fallacy logic)
        red_count = color_count.get('red', 0)
        black_count = color_count.get('black', 0)
        
        suggestions = []
        if red_count > black_count + 3:
            suggestions.append("Black appears 'due' based on recent red dominance")
        elif black_count > red_count + 3:
            suggestions.append("Red appears 'due' based on recent black dominance")
        
        # Next bet recommendation
        if suggestions:
            if "Black" in suggestions[0]:
                analysis['next_bet_suggestion'] = "BLACK (White)"
            elif "Red" in suggestions[0]:
                analysis['next_bet_suggestion'] = "RED"
            else:
                analysis['next_bet_suggestion'] = "No strong Red/Black bias"
        else:
            analysis['next_bet_suggestion'] = "No clear pattern"

        analysis['color_stats'] = color_count
        analysis['current_streak'] = self._get_current_streak(recent_colors)
        analysis['last_spin'] = self.spin_history[-1]
        analysis['last_color'] = self.get_color(self.spin_history[-1]).upper()
        
        return analysis


class RouletteGUI:
    def __init__(self, master):
        self.master = master
        master.title("Roulette Pattern Predictor")
        master.geometry("450x450")
        
        self.analyzer = RouletteAnalyzer('european')
        
        # Initial history from your image (reversed order)
        initial_history = [18, 19, 32, 33, 25, 0, 4, 13, 0, 27, 12, 20, 34, 0, 30, 34,
                      17, 23, 4, 18, 28, 22, 23, 12, 31, 13, 12, 35, 32, 2, 12,
                        36, 26, 6, 15, 17, 35, 18, 1, 1, 0, 20, 35, 33,
                      11, 4, 8, 1, 6, 27, 19, 16, 4, 3, 12, 2, 25, 3, 15, 0, 34, 31, 6, 19,25,35,
                      29,12,20,32,36,32,26,1,9,14,2,3,36,36,9,10,23,16,18,13,28,19,16,33,6,19,22,30,19,27,13,20,
                      4,36,12,34,10,28,4,32,24,31,7,22,28,0,14]
        self.analyzer.load_history(initial_history)
        
        # --- GUI Elements Setup ---

        # 1. New Spin Input Frame
        self.spin_frame = tk.LabelFrame(master, text="Insert New Spin Result (0-36)", padx=10, pady=10)
        self.spin_frame.pack(padx=10, pady=10, fill="x")
        
        self.spin_label = tk.Label(self.spin_frame, text="Number:")
        self.spin_label.pack(side="left")
        
        self.spin_entry = tk.Entry(self.spin_frame, width=5)
        self.spin_entry.pack(side="left", padx=5)
        
        self.add_button = tk.Button(self.spin_frame, text="Add & Analyze", command=self.add_and_analyze)
        self.add_button.pack(side="left", padx=10)
        
        # 2. Results Display Frame
        self.results_frame = tk.LabelFrame(master, text="Analysis & Prediction (Last 20 Spins)", padx=10, pady=10)
        self.results_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.last_spin_label = tk.Label(self.results_frame, text="", font=('Arial', 12, 'bold'))
        self.last_spin_label.pack(pady=5)
        
        self.prediction_label = tk.Label(self.results_frame, text="NEXT BET PREDICTION:", font=('Arial', 14, 'bold'), fg='blue')
        self.prediction_label.pack(pady=10)
        
        self.bet_value_label = tk.Label(self.results_frame, text="N/A", font=('Arial', 18, 'bold'), bg='#f0f0f0', width=15)
        self.bet_value_label.pack(pady=5)
        
        self.streak_label = tk.Label(self.results_frame, text="Current Streak: N/A", font=('Arial', 10))
        self.streak_label.pack(pady=5)
        
        self.stats_label = tk.Label(self.results_frame, justify=tk.LEFT, text="")
        self.stats_label.pack(pady=10)
        
        # 3. Initial Analysis on Load
        self.update_gui()

    def add_and_analyze(self):
        """Handles the button click to add a spin and update the analysis."""
        try:
            new_number = int(self.spin_entry.get())
            if 0 <= new_number <= 36:
                self.analyzer.add_spin(new_number)
                self.spin_entry.delete(0, tk.END) # Clear the input field
                self.update_gui()
            else:
                messagebox.showerror("Invalid Input", "Roulette number must be between 0 and 36.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer (0-36).")
            
    def update_gui(self):
        """Performs the analysis and updates all labels in the GUI."""
        analysis = self.analyzer.analyze_patterns()
        
        if 'error' in analysis:
            self.bet_value_label.config(text="Need more data")
            self.stats_label.config(text=analysis['error'])
            self.last_spin_label.config(text="")
            self.streak_label.config(text="")
            return

        # 1. Last Spin Info
        last_spin = analysis['last_spin']
        last_color = analysis['last_color']
        color_code = {'RED': 'red', 'BLACK': 'black', 'GREEN': 'green'}.get(last_color, 'white')
        
        self.last_spin_label.config(
            text=f"Last Spin: {last_spin} ({last_color})",
            bg=color_code,
            fg='white' if color_code != 'green' and color_code != 'black' else 'white' if color_code == 'black' else 'black' # Adjusted for visibility
        )

        # 2. Prediction
        prediction = analysis['next_bet_suggestion']
        pred_color = prediction.split()[0].upper()
        
        self.bet_value_label.config(text=prediction, fg='black', bg='yellow')

        # 3. Streak
        streak_info = analysis['current_streak']
        self.streak_label.config(text=f"Current Streak: {streak_info['color'].upper()} - {streak_info['length']} spins")

        # 4. Detailed Stats (Last 20)
        stats_text = "Color Distribution (Last 20 Spins):\n"
        for color, count in analysis['color_stats'].items():
            display_color = color.upper() if color != 'black' else "BLACK (WHITE)"
            stats_text += f"  {display_color}: {count} spins\n"
        
        self.stats_label.config(text=stats_text)


if __name__ == "__main__":
    root = tk.Tk()
    app = RouletteGUI(root)
    root.mainloop()