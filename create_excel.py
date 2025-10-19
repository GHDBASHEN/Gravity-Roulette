import pandas as pd
from datetime import datetime
import os

# --- CONFIGURATION ---
EXCEL_FILE = 'roulette_history.xlsx'

# --- YOUR NEW DATA EXTRACTED FROM THE EXCEL IMAGE ---
NEW_HISTORY_LIST = [
    18, 19, 32, 33, 25, 0, 4, 13, 0, 27, 12, 20, 34, 0, 30, 34, 17, 23, 4, 18, 28, 22, 23, 12, 31, 13, 12, 35, 32, 2, 12, 36, 26, 6, 15, 17, 35, 18, 1, 1, 0, 20, 35, 33, 11, 4, 8, 1, 6, 27, 19, 16, 4, 3, 12, 2, 25, 3, 15, 0, 34, 31, 6, 19, 25, 35, 29, 12, 20, 32, 36, 32, 26, 1, 9, 14, 2, 3, 36, 36, 9, 10, 23, 16, 18, 13, 28, 19, 
    16, 33, 6, 19, 22, 30, 19, 27, 13, 20, 4, 36, 12, 34, 10, 28, 4, 32, 24, 31, 7, 22, 28, 0, 14,1,28,5,33
]

# --- ROULETTE LOGIC ---
COLOR_MAP = {
    **{i: 'red' for i in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]},
    **{i: 'black' for i in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]},
    **{0: 'green'}
}

def get_color(number):
    return COLOR_MAP.get(number, 'unknown')

def create_excel_history(history_list):
    """Creates a DataFrame and saves it to the Excel file."""
    
    data = {
        'Timestamp': [datetime.now()] * len(history_list),
        'Number': history_list,
        'Color': [get_color(num) for num in history_list]
    }
    
    df = pd.DataFrame(data)
    
    try:
        df.to_excel(EXCEL_FILE, index=False)
        print("=" * 50)
        print(f"✅ Success! {len(history_list)} spins written to {EXCEL_FILE}")
        print(f"Last spin recorded: {history_list[-1]} ({get_color(history_list[-1]).upper()})")
        print("=" * 50)
    except Exception as e:
        print(f"❌ Error saving to Excel: {e}")

if __name__ == "__main__":
    try:
        import pandas as pd
        create_excel_history(NEW_HISTORY_LIST)
    except ImportError:
        print("\n❌ Error: Pandas not found. Please run: pip install pandas openpyxl")