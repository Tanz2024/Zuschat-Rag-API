#!/usr/bin/env python3
"""
Update outlets with comprehensive realistic hours and services
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Outlet
import random

def get_comprehensive_opening_hours():
    """Generate comprehensive realistic opening hours"""
    patterns = [
        "Monday - Sunday: 7:00 AM - 10:00 PM",
        "Monday - Thursday: 7:00 AM - 9:30 PM, Friday - Sunday: 7:00 AM - 10:30 PM", 
        "Monday - Friday: 7:30 AM - 9:00 PM, Saturday - Sunday: 8:00 AM - 10:00 PM",
        "Daily: 7:00 AM - 9:30 PM",
        "Monday - Sunday: 6:30 AM - 10:00 PM",
        "Monday - Thursday: 8:00 AM - 9:00 PM, Friday - Sunday: 7:30 AM - 10:00 PM",
        "Daily: 8:00 AM - 9:30 PM",
        "Monday - Friday: 7:00 AM - 9:30 PM, Saturday - Sunday: 8:00 AM - 10:30 PM",
        "Monday - Sunday: 7:30 AM - 9:30 PM",
        "Daily: 6:30 AM - 9:30 PM"
    ]
    return random.choice(patterns)

def get_comprehensive_services():
    """Generate comprehensive realistic services"""
    # Core services (always included)
    core_services = [
        "WiFi", 
        "Air Conditioning", 
        "Takeaway", 
        "Dine-in", 
        "Cashless Payment"
    ]
    
    # Additional services pool
    additional_services = [
        "Drive-thru",
        "Outdoor Seating", 
        "Study Area",
        "Meeting Room",
        "Power Outlets",
        "Parking Available",
        "Wheelchair Accessible",
        "Delivery Available",
        "Mobile Ordering",
        "Loyalty Program",
        "Group Bookings",
        "Event Space",
        "Private Dining",
        "Free Parking",
        "24/7 Access",
        "Conference Room",
        "Kids Area",
        "Pet Friendly"
    ]
    
    # Randomly select 4-8 additional services
    selected_additional = random.sample(additional_services, random.randint(4, 8))
    
    # Combine core + additional services
    all_services = core_services + selected_additional
    return ", ".join(sorted(all_services))

def update_comprehensive_outlet_info():
    """Update all outlets with comprehensive information"""
    print("🔄 Updating ZUS Coffee outlets with comprehensive information...")
    
    with SessionLocal() as db:
        outlets = db.query(Outlet).all()
        print(f"📍 Updating {len(outlets)} outlets...")
        
        updated_count = 0
        for outlet in outlets:
            # Update with comprehensive data
            outlet.opening_hours = get_comprehensive_opening_hours()
            outlet.services = get_comprehensive_services()
            updated_count += 1
            
            if updated_count % 50 == 0:
                print(f"   ⏳ Updated {updated_count} outlets...")
        
        db.commit()
        print(f"✅ Successfully updated {updated_count} outlets")
        
        # Show samples
        print(f"\n📋 Sample Updated Outlets:")
        samples = db.query(Outlet).limit(3).all()
        for i, outlet in enumerate(samples, 1):
            print(f"\n{i}. {outlet.name}")
            print(f"   📍 {outlet.address[:50]}...")
            print(f"   🕒 Hours: {outlet.opening_hours}")
            print(f"   🔧 Services: {outlet.services}")

def verify_update():
    """Verify the comprehensive update"""
    with SessionLocal() as db:
        total = db.query(Outlet).count()
        with_hours = db.query(Outlet).filter(Outlet.opening_hours.isnot(None)).count()
        with_services = db.query(Outlet).filter(Outlet.services.isnot(None)).count()
        
        print(f"\n📊 Update Verification:")
        print(f"   Total outlets: {total}")
        print(f"   With comprehensive hours: {with_hours}")
        print(f"   With comprehensive services: {with_services}")
        
        if with_hours == total and with_services == total:
            print(f"   ✅ All outlets updated successfully!")
        else:
            print(f"   ❌ Some outlets missing data")

def main():
    """Main update function"""
    print("🏪 ZUS Coffee Comprehensive Outlet Information Update")
    print("=" * 60)
    
    update_comprehensive_outlet_info()
    verify_update()
    
    print(f"\n🎉 Comprehensive outlet information update complete!")

if __name__ == "__main__":
    main()
