#!/usr/bin/env python3
"""
Check ZUS Coffee outlets by state/region
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Outlet

def check_outlets_by_state():
    """Check outlets distribution by state/region"""
    with SessionLocal() as db:
        # Get all outlets
        all_outlets = db.query(Outlet).all()
        print(f"📊 Total ZUS Coffee Outlets: {len(all_outlets)}")
        print("=" * 60)
        
        # Categorize by state/region
        state_counts = {}
        
        for outlet in all_outlets:
            address = outlet.address.lower()
            
            # Determine state based on address
            if ('kuala lumpur' in address or 'wilayah persekutuan' in address or 
                ' kl ' in address or address.endswith(' kl')):
                state = "Kuala Lumpur"
            elif 'selangor' in address:
                state = "Selangor"
            elif 'johor' in address:
                state = "Johor"
            elif 'penang' in address or 'pulau pinang' in address:
                state = "Penang"
            elif 'perak' in address:
                state = "Perak"
            elif 'pahang' in address:
                state = "Pahang"
            elif 'negeri sembilan' in address:
                state = "Negeri Sembilan"
            elif 'melaka' in address or 'malacca' in address:
                state = "Melaka"
            elif 'kelantan' in address:
                state = "Kelantan"
            elif 'terengganu' in address:
                state = "Terengganu"
            elif 'kedah' in address:
                state = "Kedah"
            elif 'perlis' in address:
                state = "Perlis"
            elif 'sabah' in address:
                state = "Sabah"
            elif 'sarawak' in address:
                state = "Sarawak"
            elif 'putrajaya' in address:
                state = "Putrajaya"
            elif 'labuan' in address:
                state = "Labuan"
            else:
                state = "Other/Unknown"
                print(f"🔍 Unknown location: {outlet.name} - {outlet.address}")
            
            state_counts[state] = state_counts.get(state, 0) + 1
        
        # Display results
        print("\n🗺️ ZUS Coffee Outlets by State/Region:")
        print("-" * 40)
        
        total_checked = 0
        for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(all_outlets)) * 100
            print(f"{state:20} {count:3d} outlets ({percentage:5.1f}%)")
            total_checked += count
        
        print("-" * 40)
        print(f"{'TOTAL':20} {total_checked:3d} outlets")
        
        # Show sample outlets from other states (non-KL, non-Selangor)
        print(f"\n🏪 Sample outlets from other states:")
        print("-" * 50)
        
        other_states_shown = set()
        for outlet in all_outlets:
            address = outlet.address.lower()
            
            if not ('kuala lumpur' in address or 'wilayah persekutuan' in address or 
                   ' kl ' in address or address.endswith(' kl') or 'selangor' in address):
                
                # Determine state
                state = "Unknown"
                if 'johor' in address:
                    state = "Johor"
                elif 'penang' in address or 'pulau pinang' in address:
                    state = "Penang"
                elif 'perak' in address:
                    state = "Perak"
                elif 'pahang' in address:
                    state = "Pahang"
                elif 'negeri sembilan' in address:
                    state = "Negeri Sembilan"
                elif 'melaka' in address or 'malacca' in address:
                    state = "Melaka"
                elif 'kelantan' in address:
                    state = "Kelantan"
                elif 'terengganu' in address:
                    state = "Terengganu"
                elif 'kedah' in address:
                    state = "Kedah"
                elif 'perlis' in address:
                    state = "Perlis"
                elif 'sabah' in address:
                    state = "Sabah"
                elif 'sarawak' in address:
                    state = "Sarawak"
                elif 'putrajaya' in address:
                    state = "Putrajaya"
                elif 'labuan' in address:
                    state = "Labuan"
                
                # Show one example per state
                if state not in other_states_shown:
                    print(f"\n📍 {state}:")
                    print(f"   • {outlet.name}")
                    print(f"   • {outlet.address}")
                    other_states_shown.add(state)
        
        print(f"\n✅ Analysis complete!")

if __name__ == "__main__":
    check_outlets_by_state()
