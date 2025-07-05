#!/usr/bin/env python3
"""
Clean up dummy data from ZUS Coffee database
Remove outlets that are not in KL or Selangor and have dummy/placeholder data
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Outlet

def clean_dummy_outlets():
    """Remove dummy outlets and keep only real KL and Selangor outlets"""
    with SessionLocal() as db:
        # Get all outlets
        all_outlets = db.query(Outlet).all()
        print(f"📊 Total outlets before cleanup: {len(all_outlets)}")
        
        # Identify dummy outlets to remove
        outlets_to_remove = []
        
        for outlet in all_outlets:
            address = outlet.address.lower()
            name = outlet.name.lower()
            
            # Check for dummy indicators
            is_dummy = False
            
            # Check for placeholder text
            if ("are you ready to take zus to the next level" in address or
                "tell" in address or
                "zus, coffee meets pastry" in address or
                len(address) < 20):  # Very short addresses are likely incomplete
                is_dummy = True
                
            # Check if outside KL/Selangor (except Putrajaya which is real)
            if not ('kuala lumpur' in address or 'wilayah persekutuan' in address or 
                   ' kl ' in address or address.endswith(' kl') or 'selangor' in address or
                   'putrajaya' in address):
                # These are likely dummy or incomplete data
                is_dummy = True
            
            if is_dummy:
                outlets_to_remove.append(outlet)
                print(f"🗑️  Removing dummy outlet: {outlet.name}")
                print(f"    Address: {outlet.address}")
                print()
        
        # Remove dummy outlets
        for outlet in outlets_to_remove:
            db.delete(outlet)
        
        db.commit()
        
        # Get final count
        remaining_outlets = db.query(Outlet).all()
        print(f"✅ Cleanup complete!")
        print(f"📊 Removed: {len(outlets_to_remove)} dummy outlets")
        print(f"📊 Remaining: {len(remaining_outlets)} real outlets")
        
        # Show sample of remaining outlets
        print(f"\n📍 Sample of remaining outlets:")
        for i, outlet in enumerate(remaining_outlets[:5], 1):
            print(f"{i}. {outlet.name}")
            print(f"   📍 {outlet.address}")
            print()

if __name__ == "__main__":
    clean_dummy_outlets()
