import tkinter as tk
from tkinter import messagebox
from collections import Counter
import pandas as pd
import os

# --- CONFIGURATION ---
EXCEL_FILE = 'roulette_history.xlsx' 

class RouletteAnalyzer:
    def __init__(self):
        self.spin_history = []
        self.color_map = {
            **{i: 'red' for i in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]},
            **{i: 'black' for i in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]},
            **{0: 'green'}
        }

    def get_color(self, number):
        return self.color_map.get(number, 'unknown')

    def load_history(self):
        if not os.path.exists(EXCEL_FILE):
            self.spin_history = []
            return
        try:
            df = pd.read_excel(EXCEL_FILE)
            if 'Number' in df.columns:
                self.spin_history = df['Number'].astype(int).tolist()
        except Exception:
            self.spin_history = []

    def get_last_history_info(self):
        total = len(self.spin_history)
        if total > 0:
            last_num = self.spin_history[-1]
            last_col = self.get_color(last_num).upper()
            return last_num, last_col, total
        return "--", "--", 0

    def save_spin(self, number):
        color = self.get_color(number)
        new_data = pd.DataFrame({'Timestamp': [pd.Timestamp.now()], 'Number': [number], 'Color': [color]})
        
        if os.path.exists(EXCEL_FILE):
            try:
                df_existing = pd.read_excel(EXCEL_FILE)
                df_updated = pd.concat([df_existing, new_data], ignore_index=True)
            except:
                df_updated = new_data
        else:
            df_updated = new_data
            
        try:
            df_updated.to_excel(EXCEL_FILE, index=False)
            self.spin_history.append(number)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save to Excel: {e}")
            return False

    def analyze(self, lookback=20):
        if len(self.spin_history) < 3:
            return {"suggestion": "WAITING FOR DATA...", "code": None}

        recent = self.spin_history[-min(lookback, len(self.spin_history)):]
        recent_colors = [self.get_color(num) for num in recent]
        counts = Counter(recent_colors)
        
        reds = counts.get('red', 0)
        blacks = counts.get('black', 0)
        
        suggestion = "NO CLEAR PATTERN"
        code = None

        if reds > blacks + 2:
            suggestion = "BET BLACK"
            code = 'black'
        elif blacks > reds + 2:
            suggestion = "BET RED"
            code = 'red'
        
        return {
            'suggestion': suggestion,
            'code': code
        }

class CleanRouletteGUI:
    def __init__(self, master):
        self.master = master
        master.title("Gravity Roulette | Analytics Pro")
        master.geometry("450x650")
        master.configure(bg="#2c3e50") 

        self.analyzer = RouletteAnalyzer()
        self.analyzer.load_history()

        # Session Stats
        self.wins = 0
        self.losses = 0
        self.skips = 0
        self.pending_bet = None
        self.is_first_spin = True

        # --- UI LAYOUT ---

        # 1. DATABASE STATS (Top Grey Bar)
        self.db_frame = tk.Frame(master, bg="#34495e", pady=8, padx=10)
        self.db_frame.pack(fill="x")
        
        last_num, last_col, total_stored = self.analyzer.get_last_history_info()
        
        self.db_label = tk.Label(self.db_frame, 
                                 text=f"Last History: {last_num} ({last_col})  |  Total Stored: {total_stored}", 
                                 font=("Arial", 10), fg="#bdc3c7", bg="#34495e")
        self.db_label.pack()

        # 2. SESSION SCOREBOARD (Blue Bar)
        self.score_frame = tk.Frame(master, bg="#2980b9", pady=10)
        self.score_frame.pack(fill="x")

        self.stats_label = tk.Label(self.score_frame, 
                                    text="WINS: 0   LOSS: 0   SKIPS: 0", 
                                    font=("Helvetica", 12, "bold"), fg="white", bg="#2980b9")
        self.stats_label.pack()
        
        self.rate_label = tk.Label(self.score_frame, 
                                   text="Win Rate: 0.0%", 
                                   font=("Helvetica", 10), fg="#d6eaf8", bg="#2980b9")
        self.rate_label.pack()

        # 3. PREDICTION AREA
        self.pred_frame = tk.Frame(master, bg="#2c3e50", pady=30)
        self.pred_frame.pack()

        tk.Label(self.pred_frame, text="NEXT BET PREDICTION:", font=("Arial", 10, "bold"), fg="#7f8c8d", bg="#2c3e50").pack()
        self.pred_label = tk.Label(self.pred_frame, text="ENTER SPIN", font=("Arial", 26, "bold"), fg="white", bg="#2c3e50")
        self.pred_label.pack(pady=5)

        # 4. INPUT AREA
        self.input_frame = tk.Frame(master, bg="#2c3e50", pady=20)
        self.input_frame.pack()

        tk.Label(self.input_frame, text="Enter New Number:", font=("Arial", 11), fg="white", bg="#2c3e50").pack()
        
        self.entry = tk.Entry(self.input_frame, font=("Arial", 24), width=5, justify='center', bg="#ecf0f1")
        self.entry.pack(pady=10)
        self.entry.bind('<Return>', self.process_spin)
        self.entry.focus_set()

        self.btn = tk.Button(self.input_frame, text="ADD SPIN", font=("Arial", 12, "bold"), 
                             command=self.process_spin, bg="#27ae60", fg="white", 
                             activebackground="#2ecc71", activeforeground="white",
                             height=2, width=15, borderwidth=0)
        self.btn.pack(pady=10)

    def process_spin(self, event=None):
        try:
            val = self.entry.get()
            if not val: return
            number = int(val)
            
            if 0 <= number <= 36:
                # 1. Check Previous Bet Result
                if self.pending_bet:
                    actual_col = self.analyzer.get_color(number)
                    if actual_col == self.pending_bet:
                        self.wins += 1
                        self.flash_screen("#27ae60")
                    elif actual_col == 'green':
                         self.losses += 1
                    else:
                        self.losses += 1
                        self.flash_screen("#c0392b")
                else:
                    if not self.is_first_spin:
                        self.skips += 1
                
                self.is_first_spin = False

                # 2. Save & Update Logic
                if self.analyzer.save_spin(number):
                    result = self.analyzer.analyze()
                    self.pending_bet = result['code']
                    self.update_display(result, number)
                    self.entry.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Number must be 0-36")
        except ValueError:
            pass

    def update_display(self, result, current_number):
        total_bets = self.wins + self.losses
        win_rate = round((self.wins / total_bets) * 100, 1) if total_bets > 0 else 0.0
        
        self.stats_label.config(text=f"WINS: {self.wins}   LOSS: {self.losses}   SKIPS: {self.skips}")
        self.rate_label.config(text=f"Win Rate: {win_rate}%")

        last_col = self.analyzer.get_color(current_number).upper()
        total_stored = len(self.analyzer.spin_history)
        self.db_label.config(text=f"Last History: {current_number} ({last_col})  |  Total Stored: {total_stored}")

        suggestion = result['suggestion']
        
        fg_color = "white"
        if "RED" in suggestion: fg_color = "#e74c3c"
        if "BLACK" in suggestion: fg_color = "#3498db"
        if "NO CLEAR" in suggestion: fg_color = "#f1c40f"
        
        self.pred_label.config(text=suggestion, fg=fg_color)

    def flash_screen(self, color):
        original = "#2c3e50"
        self.master.configure(bg=color)
        self.master.after(100, lambda: self.master.configure(bg=original))

if __name__ == "__main__":
    root = tk.Tk()
    app = CleanRouletteGUI(root)
    root.mainloop()
