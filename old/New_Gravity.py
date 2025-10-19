import random
from collections import Counter
from datetime import datetime

class RouletteAnalyzer:
    def __init__(self, wheel_type='european'):
        """
        Initialize the roulette analyzer
        wheel_type: 'european' (single zero) or 'american' (double zero)
        """
        self.wheel_type = wheel_type
        self.reset_session()
        
        # European wheel layout (0-36)
        self.numbers = list(range(37))
        
        # Color mapping for European roulette
        self.color_map = {
            **{i: 'red' for i in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]},
            **{i: 'black' for i in [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]},
            **{0: 'green'}
        }
        
        # Probabilities
        if wheel_type == 'european':
            self.total_numbers = 37
            self.probability = {
                'red': 18/37, 'black': 18/37, 'green': 1/37,
                'even': 18/37, 'odd': 18/37,
                'low': 18/37, 'high': 18/37
            }
        else: # american
            self.total_numbers = 38
            self.probability = {
                'red': 18/38, 'black': 18/38, 'green': 2/38,
                'even': 18/38, 'odd': 18/38,
                'low': 18/38, 'high': 18/38
            }

    def reset_session(self):
        """Reset all session data"""
        self.spin_history = []
        self.bet_history = []
        self.bankroll = 1000  # Starting bankroll
        self.session_start = datetime.now()

    def load_history(self, history_list):
        """Load an external history list (e.g., from an image)"""
        self.spin_history = history_list

    def spin(self):
        """Simulate a roulette spin"""
        result = random.choice(self.numbers)
        self.spin_history.append(result)
        return result

    def get_color(self, number):
        """Get color for a number"""
        return self.color_map.get(number, 'unknown')

    def get_recent_spins(self, count=20):
        """Get the most recent spins, default to 20 for analysis"""
        return self.spin_history[-count:] if self.spin_history else []

    def analyze_patterns(self, lookback=20):
        """Analyze recent patterns and provide betting suggestions"""
        if len(self.spin_history) < 5:
            return {"error": "Not enough data. Need at least 5 spins."}

        # Use max(lookback, len(self.spin_history)) to avoid errors if history is shorter than lookback
        recent = self.get_recent_spins(min(lookback, len(self.spin_history)))
        recent_colors = [self.get_color(num) for num in recent]
        
        analysis = {}
        
        # Color frequency analysis
        color_count = Counter(recent_colors)
        total_spins = len(recent_colors)
        
        analysis['color_stats'] = {
            color: {'count': count, 'percentage': (count/total_spins)*100}
            for color, count in color_count.items()
        }
        
        # Streak analysis
        analysis['current_streak'] = self._get_current_streak(recent_colors)
        
        # Pattern-based suggestions (Gambler's Fallacy approach)
        suggestions = []
        
        # Color bias detection
        red_count = color_count.get('red', 0)
        black_count = color_count.get('black', 0)
        green_count = color_count.get('green', 0)
        
        # Suggest the opposite of a strong bias (a common gambler strategy)
        if red_count > black_count + 3:
            suggestions.append("Black appears 'due' based on recent red dominance")
        elif black_count > red_count + 3:
            suggestions.append("Red appears 'due' based on recent black dominance")
        
        # Green prediction (very basic)
        if green_count == 0 and len(recent) >= 15:
            suggestions.append("Green (Zero) hasn't appeared in a while, but probability remains low")
        
        # Hot/Cold numbers
        number_count = Counter(recent)
        hot_numbers = number_count.most_common(3)
        cold_numbers = [num for num in self.numbers if num not in number_count][:3]
        
        analysis['hot_numbers'] = hot_numbers
        analysis['cold_numbers'] = cold_numbers
        analysis['suggestions'] = suggestions
        
        # Next bet recommendation (based on flawed pattern logic)
        if suggestions:
            # Prioritize the most direct pattern suggestion (Red/Black "due")
            if "Black" in suggestions[0]:
                analysis['next_bet_suggestion'] = "Black (White)"
            elif "Red" in suggestions[0]:
                analysis['next_bet_suggestion'] = "Red"
            else:
                analysis['next_bet_suggestion'] = "No strong Red/Black suggestion"
        else:
            analysis['next_bet_suggestion'] = "No clear pattern"
        
        return analysis

    def _get_current_streak(self, colors):
        """Get the current color streak"""
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

    def place_bet(self, bet_type, amount, bet_value=None):
        """Place a bet and calculate payout"""
        # ... (rest of the place_bet method remains as provided) ...
        if amount > self.bankroll:
            return {"error": "Insufficient funds"}
        
        self.bankroll -= amount
        last_spin = self.spin_history[-1] if self.spin_history else None
        
        if last_spin is None:
            # Refund the bet if no spin occurred
            self.bankroll += amount
            return {"error": "No spin data available. Simulate a spin first."}
        
        win = False
        payout = 0
        
        # Check if bet wins
        if bet_type == 'color':
            # Handle 'white' as 'black'
            normalized_value = 'black' if bet_value == 'white' else bet_value
            if self.get_color(last_spin) == normalized_value:
                win = True
                payout = amount * 2
        elif bet_type == 'number':
            if last_spin == bet_value:
                win = True
                payout = amount * 36
        elif bet_type == 'even_odd':
            if (bet_value == 'even' and last_spin % 2 == 0 and last_spin != 0) or \
               (bet_value == 'odd' and last_spin % 2 == 1):
                win = True
                payout = amount * 2
        
        if win:
            self.bankroll += payout
        
        bet_record = {
            'timestamp': datetime.now(),
            'bet_type': bet_type,
            'bet_value': bet_value,
            'amount': amount,
            'win': win,
            'payout': payout if win else 0,
            'result': last_spin,
            'bankroll_after': self.bankroll
        }
        
        self.bet_history.append(bet_record)
        return bet_record

    def get_session_stats(self):
        """Get comprehensive session statistics"""
        # ... (rest of the get_session_stats method remains as provided) ...
        if not self.spin_history:
            return {"error": "No spins recorded"}
        
        total_spins = len(self.spin_history)
        colors = [self.get_color(num) for num in self.spin_history]
        color_stats = Counter(colors)
        
        stats = {
            'session_duration': str(datetime.now() - self.session_start),
            'total_spins': total_spins,
            'color_distribution': dict(color_stats),
            'expected_distribution': self.probability,
            'current_bankroll': self.bankroll,
            'total_bets': len(self.bet_history),
            'winning_bets': len([b for b in self.bet_history if b['win']]),
            'profit_loss': self.bankroll - 1000  # Starting bankroll was 1000
        }
        
        return stats

    def display_recent_spins(self, count=10):
        """Display recent spins in a readable format"""
        # ... (rest of the display_recent_spins method remains as provided) ...
        recent = self.get_recent_spins(count)
        if not recent:
            print("No spins recorded.")
            return
        
        print(f"\nLast {len(recent)} spins:")
        print("Spin# | Number | Color")
        print("-" * 25)
        # Displaying the *last* 'count' spins, starting from the most recent (reversed)
        for i, spin in enumerate(reversed(recent), 1):
            color = self.get_color(spin)
            color_display = color.upper() if color != 'green' else 'GREEN'
            print(f"{i:5} | {spin:6} | {color_display}")

def main():
    """Main function: Loads history, performs prediction, and starts the interactive CLI."""
    
    # 1. EXTRACTED HISTORY FROM IMAGE
    # Reads numbers top-to-bottom, left-to-right from the 'History' column in the image.
    image_history = [18, 19, 32, 33, 25, 0, 4, 13, 0, 27, 12, 20, 34, 0, 30, 34,
                      17, 23, 4, 18, 28, 22, 23, 12, 31, 13, 12, 35, 32, 2, 12,
                        36, 26, 6, 15, 17, 35, 18, 1, 1, 0, 20, 35, 33,
                      11, 4, 8, 1, 6, 27, 19, 16, 4, 3, 12, 2, 25, 3, 15, 0, 34, 31, 6, 19,25,35,
                      29,12,20,32,36,32,26,1,9,14,2,3,36,36,9,10,23,16,18,13,28,19,16,33,6,19,22,30,19,27,13,20,
                      4,36,12,34,10,28]
    
    analyzer = RouletteAnalyzer('european')
    # Load the history before the user loop starts
    analyzer.load_history(image_history)

    print("=" * 60)
    print("ROULETTE ANALYSIS TOOL (History Loaded from Image)")
    print("=" * 60)
    print(f"Loaded {len(analyzer.spin_history)} spins. Last result: {analyzer.spin_history[-1]} ({analyzer.get_color(analyzer.spin_history[-1]).upper()})\n")
    
    # 2. INITIAL PREDICTION
    print("--- Initial Next Bet Prediction Based on Image History ---")
    analysis = analyzer.analyze_patterns(lookback=20)
    
    next_bet = analysis.get('next_bet_suggestion', 'No strong suggestion')
    print(f"💰 Recommended Next Bet: {next_bet}")
    print(f"Current Streak: {analysis['current_streak']['color'].upper()} - {analysis['current_streak']['length']} spins")
    
    # Show the relevant stats for the prediction
    print("\nColor Distribution (Last 20 Spins):")
    for color, stats in analysis['color_stats'].items():
        # Handle 'white' interpretation for the user
        color_display = color.upper() + (" (WHITE)" if color == 'black' else "")
        print(f"  {color_display}: {stats['count']} spins ({stats['percentage']:.1f}%)")
        
    print("\nDISCLAIMER: This tool uses pattern recognition (Gambler's Fallacy).")
    print("Roulette is random. Past results do not influence future outcomes.")
    print("------------------------------------------------------------------")
    
    while True:
        print("\nOptions:")
        print("1. Simulate **New Spin**")
        print("2. Analyze Patterns & Get Suggestions")
        print("3. Place a Bet (based on last spin)")
        print("4. Show Session Statistics")
        print("5. Show Recent Spins")
        print("6. Reset Session (Clears all history)")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            result = analyzer.spin()
            color = analyzer.get_color(result)
            print(f"\n🎰 Spin result: {result} ({color.upper()})")
            
        elif choice == '2':
            print("\n🔍 Pattern Analysis:")
            analysis = analyzer.analyze_patterns()
            
            if 'error' in analysis:
                print(analysis['error'])
            else:
                print(f"Next Bet Suggestion: {analysis['next_bet_suggestion']}")
                print(f"Current Streak: {analysis['current_streak']['color']} - {analysis['current_streak']['length']} spins")
                
                print("\nColor Distribution (last 20 spins):")
                for color, stats in analysis['color_stats'].items():
                    print(f"  {color.upper()}: {stats['count']} spins ({stats['percentage']:.1f}%)")
                    
                print(f"\nHot Numbers: {[num for num, count in analysis['hot_numbers']]}")
                print(f"Cold Numbers: {analysis['cold_numbers'][:3]}")
                
                if analysis['suggestions']:
                    print("\nSuggestions (based on pattern recognition):")
                    for suggestion in analysis['suggestions']:
                        print(f"  • {suggestion}")
                        
        elif choice == '3':
            if not analyzer.spin_history:
                print("Please simulate at least one spin first.")
                continue
                
            print("\nBet Types: color, number, even_odd")
            bet_type = input("Enter bet type: ").strip().lower()
            
            if bet_type == 'color':
                bet_value = input("Enter color (red/black/green/white): ").strip().lower()
                # Use 'black' if user inputs 'white'
                if bet_value == 'white': bet_value = 'black'
            elif bet_type == 'number':
                try:
                    bet_value = int(input("Enter number (0-36): "))
                except ValueError:
                    print("Invalid number.")
                    continue
            elif bet_type == 'even_odd':
                bet_value = input("Enter (even/odd): ").strip().lower()
            else:
                print("Invalid bet type")
                continue
                
            try:
                amount = float(input("Enter bet amount: "))
            except ValueError:
                print("Invalid amount.")
                continue
                
            result = analyzer.place_bet(bet_type, amount, bet_value)
            if 'error' in result:
                print(f"Error: {result['error']}")
            else:
                outcome = "WIN! 🎉" if result['win'] else "LOSE 💸"
                print(f"Result: {outcome}")
                print(f"Payout: {result['payout']}")
                print(f"Current Bankroll: {result['bankroll_after']:.2f}")
                
        elif choice == '4':
            stats = analyzer.get_session_stats()
            if 'error' in stats:
                print(stats['error'])
            else:
                print("\n📊 Session Statistics:")
                print(f"Session Duration: {stats['session_duration'].split('.')[0]}")
                print(f"Total Spins: {stats['total_spins']}")
                print(f"Current Bankroll: ${stats['current_bankroll']:.2f}")
                print(f"Profit/Loss: ${stats['profit_loss']:.2f}")
                print(f"Bets Placed: {stats['total_bets']}")
                
                if stats['total_bets'] > 0:
                    win_rate = (stats['winning_bets'] / stats['total_bets']) * 100
                    print(f"Win Rate: {win_rate:.1f}%")
                    
        elif choice == '5':
            # Display all history initially, or a large number if the history is long
            analyzer.display_recent_spins(count=len(analyzer.spin_history))
            
        elif choice == '6':
            analyzer.reset_session()
            print("Session reset. New session started.")
            
        elif choice == '7':
            print("Thank you for using the Roulette Analysis Tool!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()