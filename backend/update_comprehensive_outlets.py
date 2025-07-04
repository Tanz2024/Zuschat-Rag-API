#!/usr/bin/env python3
"""
Update outlets with comprehensive opening hours and services
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
        "Monday - Friday: 7:00 AM - 9:30 PM, Saturday - Sunday: 8:00 AM - 10:30 PM"
    ]
    return random.choice(patterns)

def get_comprehensive_services():
    """Generate comprehensive realistic services"""
    # Core services (all outlets have these)
    core_services = [
        "WiFi",
        "Air Conditioning", 
        "Takeaway",
        "Dine-in",
        "Cashless Payment"
    ]
    
    # Additional services (randomly select)
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
        "Private Dining"
    ]
    
    # Select 4-8 additional services randomly
    selected_additional = random.sample(additional_services, random.randint(4, 8))
    
    all_services = core_services + selected_additional
    return ", ".join(sorted(all_services))

def update_comprehensive_outlet_info():
    """Update all outlets with comprehensive information"""
    print("🔄 Updating outlets with comprehensive hours and services...")
    
    with SessionLocal() as db:
        outlets = db.query(Outlet).all()
        print(f"📍 Found {len(outlets)} outlets to update")
        
        for i, outlet in enumerate(outlets, 1):
            outlet.opening_hours = get_comprehensive_opening_hours()
            outlet.services = get_comprehensive_services()
            
            if i % 50 == 0:
                print(f"   ⏳ Updated {i} outlets...")
        
        db.commit()
        print(f"✅ Successfully updated {len(outlets)} outlets")
        
        # Show samples
        print(f"\n📋 Updated Sample Outlets:")
        samples = db.query(Outlet).limit(3).all()
        for i, outlet in enumerate(samples, 1):
            print(f"\n{i}. {outlet.name}")
            print(f"   🕒 Hours: {outlet.opening_hours}")
            print(f"   🔧 Services: {outlet.services}")

if __name__ == "__main__":
    print("🏪 ZUS Coffee Comprehensive Outlet Update")
    print("=" * 50)
    update_comprehensive_outlet_info()
    print(f"\n🎉 All outlets now have comprehensive information!")
