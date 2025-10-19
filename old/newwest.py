import random
from collections import Counter, defaultdict
from datetime import datetime

class SpecialRouletteAnalyzer:
    def __init__(self):
        self.wheel_type = 'special'
        self.reset_session()
        
        # Define the special wheel layout based on your image
        # The wheel has specific numbers in specific positions
        self.wheel_numbers = {
            'positions': {
                1: [20, 21, 24, 27, 30, 33, 36],  # Bottom section
                2: [10, 33, 30],  # First section
                3: [20, 21, 24, 27, 30, 33, 36]   # Second bottom section (same as first)
            },
            'all_numbers': [20, 21, 24, 27, 30, 33, 36, 10]  # Unique numbers
        }
        
        # Color mapping for standard roulette colors
        self.color_map = {
            10: 'red', 20: 'black', 21: 'red', 24: 'black', 
            27: 'red', 30: 'black', 33: 'red', 36: 'black'
        }
        
        # Position weights (probability of ball landing in each position)
        self.position_weights = {
            1: 0.4,  # Bottom section - most likely
            2: 0.3,  # First section
            3: 0.3   # Second bottom section
        }

    def reset_session(self):
        """Reset all session data"""
        self.spin_history = []
        self.position_history = []  # Track which position was hit
        self.bet_history = []
        self.bankroll = 1000
        self.session_start = datetime.now()

    def load_history(self, history_list):
        """Load an external history list"""
        self.spin_history = history_list

    def spin(self):
        """Simulate a spin on this special wheel"""
        # First select position based on weights
        position = random.choices(
            list(self.position_weights.keys()),
            weights=list(self.position_weights.values()),
            k=1
        )[0]
        
        # Then select number from that position
        available_numbers = self.wheel_numbers['positions'][position]
        result = random.choice(available_numbers)
        
        # Handle "two numbers slow" scenario (5% chance)
        if random.random() < 0.05:  # 5% chance of hitting two numbers
            second_number = random.choice([n for n in available_numbers if n != result])
            # For now, we'll use the first number as result, but track both
            self.position_history.append((position, f"double:{result}+{second_number}"))
        else:
            self.position_history.append((position, "single"))
        
        self.spin_history.append(result)
        return result, position

    def get_color(self, number):
        """Get color for a number"""
        return self.color_map.get(number, 'unknown')

    def get_recent_spins(self, count=10):
        """Get the most recent spins"""
        return self.spin_history[-count:] if self.spin_history else []

    def analyze_special_patterns(self, lookback=15):
        """Analyze patterns specific to this wheel layout"""
        if len(self.spin_history) < 5:
            return {"error": "Not enough data"}
        
        recent = self.get_recent_spins(lookback)
        recent_colors = [self.get_color(num) for num in recent]
        
        analysis = {}
        
        # Position analysis
        if self.position_history:
            recent_positions = [pos for pos, _ in self.position_history[-lookback:]]
            position_count = Counter(recent_positions)
            analysis['position_stats'] = dict(position_count)
        
        # Color analysis
        color_count = Counter(recent_colors)
        total_spins = len(recent_colors)
        
        analysis['color_stats'] = {
            color: {'count': count, 'percentage': (count/total_spins)*100}
            for color, count in color_count.items()
        }
        
        # Number frequency
        number_count = Counter(recent)
        analysis['hot_numbers'] = number_count.most_common(3)
        analysis['cold_numbers'] = [n for n in self.wheel_numbers['all_numbers'] 
                                  if n not in number_count]
        
        # Special predictions for this wheel
        suggestions = []
        
        # Position-based suggestions
        if 'position_stats' in analysis:
            pos_stats = analysis['position_stats']
            if len(pos_stats) > 1:
                most_common_pos = max(pos_stats.items(), key=lambda x: x[1])
                least_common_pos = min(pos_stats.items(), key=lambda x: x[1])
                
                # Get numbers from least common position
                least_pos_numbers = self.wheel_numbers['positions'][least_common_pos[0]]
                suggestions.append(f"Position {least_common_pos[0]} under-represented. Consider: {least_pos_numbers}")
        
        # Color balance
        red_count = color_count.get('red', 0)
        black_count = color_count.get('black', 0)
        
        if red_count > black_count + 2:
            # Find black numbers that haven't appeared recently
            black_candidates = [n for n in self.wheel_numbers['all_numbers'] 
                              if self.get_color(n) == 'black' and n not in recent]
            if black_candidates:
                suggestions.append(f"Red dominant. Try black numbers: {black_candidates}")
        elif black_count > red_count + 2:
            red_candidates = [n for n in self.wheel_numbers['all_numbers'] 
                            if self.get_color(n) == 'red' and n not in recent]
            if red_candidates:
                suggestions.append(f"Black dominant. Try red numbers: {red_candidates}")
        
        analysis['suggestions'] = suggestions
        
        # Generate next bet recommendations
        recommendations = []
        
        # Recommendation 1: Based on position frequency
        if 'position_stats' in analysis and analysis['position_stats']:
            least_common_pos = min(analysis['position_stats'].items(), key=lambda x: x[1])
            pos_numbers = self.wheel_numbers['positions'][least_common_pos[0]]
            recommendations.append({
                'type': 'position_balance',
                'numbers': pos_numbers,
                'reason': f'Position {least_common_pos[0]} due for hits'
            })
        
        # Recommendation 2: Based on cold numbers
        if analysis['cold_numbers']:
            recommendations.append({
                'type': 'cold_numbers',
                'numbers': analysis['cold_numbers'][:2],
                'reason': 'These numbers haven\'t appeared recently'
            })
        
        # Recommendation 3: Based on color balance
        if red_count != black_count:
            target_color = 'black' if red_count > black_count else 'red'
            target_numbers = [n for n in self.wheel_numbers['all_numbers'] 
                            if self.get_color(n) == target_color]
            recommendations.append({
                'type': 'color_balance',
                'numbers': target_numbers[:3],
                'reason': f'{target_color.upper()} due for reversion'
            })
        
        analysis['recommendations'] = recommendations
        
        return analysis

    def place_bet(self, bet_type, amount, bet_value=None):
        """Place a bet on this special wheel"""
        if amount > self.bankroll:
            return {"error": "Insufficient funds"}
        
        self.bankroll -= amount
        last_spin = self.spin_history[-1] if self.spin_history else None
        
        if last_spin is None:
            self.bankroll += amount
            return {"error": "No spin data available"}
        
        win = False
        payout = 0
        
        # Betting options for this special wheel
        if bet_type == 'number':
            if last_spin == bet_value:
                win = True
                payout = amount * 8  # Higher payout for fewer numbers
        elif bet_type == 'color':
            if self.get_color(last_spin) == bet_value:
                win = True
                payout = amount * 2
        elif bet_type == 'position':
            # Bet on which position will hit
            last_position = self.position_history[-1][0] if self.position_history else None
            if last_position == bet_value:
                win = True
                payout = amount * 3
        
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
        """Get session statistics"""
        if not self.spin_history:
            return {"error": "No spins recorded"}
        
        total_spins = len(self.spin_history)
        colors = [self.get_color(num) for num in self.spin_history]
        color_stats = Counter(colors)
        
        stats = {
            'session_duration': str(datetime.now() - self.session_start),
            'total_spins': total_spins,
            'color_distribution': dict(color_stats),
            'current_bankroll': self.bankroll,
            'total_bets': len(self.bet_history),
            'winning_bets': len([b for b in self.bet_history if b['win']]),
            'profit_loss': self.bankroll - 1000
        }
        
        return stats

    def display_wheel_info(self):
        """Display information about this special wheel"""
        print("\n🎯 SPECIAL WHEEL CONFIGURATION")
        print("=" * 40)
        print("Position 1 (Bottom):", self.wheel_numbers['positions'][1])
        print("Position 2 (1st):   ", self.wheel_numbers['positions'][2])
        print("Position 3 (2nd Bottom):", self.wheel_numbers['positions'][3])
        print("\nAll possible numbers:", sorted(self.wheel_numbers['all_numbers']))
        print("Position weights:", self.position_weights)

def main():
    """Main function for the special roulette analyzer"""
    analyzer = SpecialRouletteAnalyzer()
    
    # Load some initial history based on your image data
    initial_history = [18, 19, 32, 33, 25, 0, 4, 13, 0, 27, 12, 20, 34, 0, 30, 34,
                      17, 23, 4, 18, 28, 22, 23, 12, 31, 13, 12, 35, 32, 2, 12,
                        36, 26, 6, 15, 17, 35, 18, 1, 1, 0, 20, 35, 33,
                      11, 4, 8, 1, 6, 27, 19, 16, 4, 3, 12, 2, 25, 3, 15, 0, 34, 31, 6, 19,25,35,
                      29,12,20,32,36,32,26,1,9,14,2,3,36,36,9,10,23,16,18,13,28,19,16,33,6,19]
    analyzer.load_history(initial_history)
    
    print("=" * 60)
    print("SPECIAL ROULETTE ANALYZER")
    print("=" * 60)
    print("Custom wheel with positions and specific numbers")
    print("Ball can hit one number or two numbers (slow ball)")
    
    analyzer.display_wheel_info()
    
    while True:
        print("\nOptions:")
        print("1. Simulate New Spin")
        print("2. Analyze Special Patterns")
        print("3. Place a Bet")
        print("4. Show Session Statistics")
        print("5. Show Recent Spins")
        print("6. Show Wheel Configuration")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            result, position = analyzer.spin()
            color = analyzer.get_color(result)
            print(f"\n🎰 Spin result: {result} ({color.upper()})")
            print(f"   Position: {position}")
            
        elif choice == '2':
            print("\n🔍 Special Pattern Analysis:")
            analysis = analyzer.analyze_special_patterns()
            
            if 'error' in analysis:
                print(analysis['error'])
            else:
                print("\n📊 POSITION ANALYSIS:")
                if 'position_stats' in analysis:
                    for position, count in analysis['position_stats'].items():
                        print(f"  Position {position}: {count} hits")
                
                print("\n🎯 COLOR DISTRIBUTION:")
                for color, stats in analysis['color_stats'].items():
                    print(f"  {color.upper()}: {stats['count']} spins ({stats['percentage']:.1f}%)")
                
                print(f"\n🔥 HOT NUMBERS: {[num for num, count in analysis['hot_numbers']]}")
                print(f"❄️  COLD NUMBERS: {analysis['cold_numbers']}")
                
                print("\n💡 RECOMMENDATIONS:")
                if analysis['recommendations']:
                    for rec in analysis['recommendations']:
                        print(f"  {rec['type'].replace('_', ' ').title()}:")
                        print(f"    Numbers: {rec['numbers']}")
                        print(f"    Reason: {rec['reason']}")
                else:
                    print("  No strong patterns detected")
                
                if analysis['suggestions']:
                    print("\n💭 STRATEGY SUGGESTIONS:")
                    for suggestion in analysis['suggestions']:
                        print(f"  • {suggestion}")
                        
        elif choice == '3':
            if not analyzer.spin_history:
                print("Please simulate at least one spin first.")
                continue
                
            print("\nAvailable Bet Types:")
            print("  - number (pays 8:1)")
            print("  - color (pays 2:1)") 
            print("  - position (pays 3:1)")
            
            bet_type = input("Enter bet type: ").strip().lower()
            
            if bet_type == 'number':
                try:
                    bet_value = int(input("Enter number: "))
                    if bet_value not in analyzer.wheel_numbers['all_numbers']:
                        print("Invalid number for this wheel")
                        continue
                except ValueError:
                    print("Invalid number")
                    continue
            elif bet_type == 'color':
                bet_value = input("Enter color (red/black): ").strip().lower()
                if bet_value not in ['red', 'black']:
                    print("Invalid color")
                    continue
            elif bet_type == 'position':
                try:
                    bet_value = int(input("Enter position (1, 2, 3): "))
                    if bet_value not in [1, 2, 3]:
                        print("Invalid position")
                        continue
                except ValueError:
                    print("Invalid position")
                    continue
            else:
                print("Invalid bet type")
                continue
                
            try:
                amount = float(input("Enter bet amount: "))
            except ValueError:
                print("Invalid amount")
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
            recent = analyzer.get_recent_spins(10)
            if not recent:
                print("No spins recorded.")
            else:
                print(f"\nLast {len(recent)} spins:")
                for i, spin in enumerate(reversed(recent), 1):
                    color = analyzer.get_color(spin)
                    print(f"  {i:2}. {spin} ({color.upper()})")
                    
        elif choice == '6':
            analyzer.display_wheel_info()
            
        elif choice == '7':
            print("Thank you for using the Special Roulette Analyzer!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()