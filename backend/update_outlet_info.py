#!/usr/bin/env python3
"""
Update ZUS Coffee outlets with realistic opening hours and services
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Outlet
import random

def get_realistic_opening_hours():
    """Generate realistic opening hours for ZUS Coffee outlets"""
    hour_patterns = [
        "Monday - Sunday: 7:00 AM - 10:00 PM",
        "Monday - Thursday: 7:00 AM - 9:30 PM, Friday - Sunday: 7:00 AM - 10:30 PM",
        "Monday - Friday: 7:30 AM - 9:00 PM, Saturday - Sunday: 8:00 AM - 10:00 PM",
        "Daily: 7:00 AM - 9:30 PM",
        "Monday - Sunday: 6:30 AM - 10:00 PM",
        "Monday - Thursday: 8:00 AM - 9:00 PM, Friday - Sunday: 7:30 AM - 10:00 PM",
        "Daily: 8:00 AM - 9:30 PM",
        "Monday - Friday: 7:00 AM - 9:30 PM, Saturday - Sunday: 8:00 AM - 10:30 PM"
    ]
    return random.choice(hour_patterns)

def get_realistic_services():
    """Generate realistic services for ZUS Coffee outlets"""
    all_services = [
        "WiFi",
        "Air Conditioning", 
        "Takeaway",
        "Dine-in",
        "Drive-thru",
        "Outdoor Seating",
        "Study Area",
        "Meeting Room",
        "Power Outlets",
        "Parking Available",
        "Wheelchair Accessible",
        "Cashless Payment",
        "Delivery Available",
        "Mobile Ordering",
        "Loyalty Program",
        "Group Bookings",
        "Event Space",
        "Private Dining"
    ]
    
    # Core services that most outlets have
    core_services = ["WiFi", "Air Conditioning", "Takeaway", "Dine-in", "Cashless Payment"]
    
    # Additional services (randomly select 3-7 more)
    additional_services = [s for s in all_services if s not in core_services]
    selected_additional = random.sample(additional_services, random.randint(3, 7))
    
    final_services = core_services + selected_additional
    return ", ".join(sorted(final_services))

def update_outlet_info():
    """Update all outlets with realistic opening hours and services"""
    print("🕒 Updating ZUS Coffee outlets with opening hours and services...")
    
    with SessionLocal() as db:
        outlets = db.query(Outlet).all()
        
        print(f"📍 Found {len(outlets)} outlets to update")
        
        updated_count = 0
        for outlet in outlets:
            # Generate realistic opening hours and services
            outlet.opening_hours = get_realistic_opening_hours()
            outlet.services = get_realistic_services()
            updated_count += 1
            
            if updated_count % 50 == 0:
                print(f"   ⏳ Updated {updated_count} outlets...")
        
        db.commit()
        print(f"✅ Successfully updated {updated_count} outlets with opening hours and services")
        
        # Show some examples
        sample_outlets = db.query(Outlet).limit(5).all()
        print(f"\n📋 Sample Updated Outlets:")
        for i, outlet in enumerate(sample_outlets, 1):
            print(f"\n{i}. {outlet.name}")
            print(f"   📍 {outlet.address[:60]}...")
            print(f"   🕒 Hours: {outlet.opening_hours}")
            print(f"   🔧 Services: {outlet.services[:80]}...")

def verify_outlet_updates():
    """Verify the outlet updates"""
    with SessionLocal() as db:
        total_outlets = db.query(Outlet).count()
        outlets_with_hours = db.query(Outlet).filter(Outlet.opening_hours.isnot(None)).count()
        outlets_with_services = db.query(Outlet).filter(Outlet.services.isnot(None)).count()
        
        print(f"\n📊 Update Verification:")
        print(f"   Total outlets: {total_outlets}")
        print(f"   Outlets with hours: {outlets_with_hours}")
        print(f"   Outlets with services: {outlets_with_services}")
        
        if outlets_with_hours == total_outlets and outlets_with_services == total_outlets:
            print(f"   ✅ All outlets successfully updated!")
        else:
            print(f"   ⚠️  Some outlets missing information")

def main():
    """Main function"""
    print("🏪 ZUS Coffee Outlet Information Update")
    print("=" * 50)
    
    update_outlet_info()
    verify_outlet_updates()
    
    print(f"\n🎉 Outlet information update complete!")
    print(f"All ZUS Coffee outlets now have realistic opening hours and services!")

if __name__ == "__main__":
    main()
