#!/usr/bin/env python3
"""
Verify outlet opening hours and services in PostgreSQL database
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Outlet

def verify_outlet_hours_and_services():
    """Verify that all outlets have opening hours and services"""
    print("🔍 Verifying ZUS Coffee Outlet Hours & Services")
    print("=" * 60)
    
    with SessionLocal() as db:
        # Get total outlet count
        total_outlets = db.query(Outlet).count()
        print(f"📊 Total outlets in database: {total_outlets}")
        
        # Check outlets with opening hours
        outlets_with_hours = db.query(Outlet).filter(
            Outlet.opening_hours.isnot(None),
            Outlet.opening_hours != ''
        ).count()
        
        # Check outlets with services
        outlets_with_services = db.query(Outlet).filter(
            Outlet.services.isnot(None),
            Outlet.services != ''
        ).count()
        
        print(f"🕒 Outlets with opening hours: {outlets_with_hours}/{total_outlets}")
        print(f"🔧 Outlets with services: {outlets_with_services}/{total_outlets}")
        
        # Show detailed sample of outlets
        print(f"\n📋 Sample Outlets with Details:")
        sample_outlets = db.query(Outlet).limit(5).all()
        
        for i, outlet in enumerate(sample_outlets, 1):
            print(f"\n{i}. {outlet.name}")
            print(f"   📍 Location: {outlet.address[:60]}...")
            print(f"   🕒 Hours: {outlet.opening_hours or 'NOT SET'}")
            print(f"   🔧 Services: {outlet.services or 'NOT SET'}")
        
        # Check for missing data
        outlets_missing_hours = db.query(Outlet).filter(
            (Outlet.opening_hours.is_(None)) | (Outlet.opening_hours == '')
        ).count()
        
        outlets_missing_services = db.query(Outlet).filter(
            (Outlet.services.is_(None)) | (Outlet.services == '')
        ).count()
        
        print(f"\n⚠️  Missing Data:")
        print(f"   Outlets missing hours: {outlets_missing_hours}")
        print(f"   Outlets missing services: {outlets_missing_services}")
        
        # Verify status
        if outlets_missing_hours == 0 and outlets_missing_services == 0:
            print(f"\n✅ VERIFICATION PASSED!")
            print(f"   All {total_outlets} outlets have complete information")
            print(f"   Opening hours: ✅ Complete")
            print(f"   Services: ✅ Complete")
        else:
            print(f"\n❌ VERIFICATION FAILED!")
            print(f"   Some outlets are missing hours or services data")
            
            if outlets_missing_hours > 0:
                print(f"\n🔍 Sample outlets missing hours:")
                missing_hours = db.query(Outlet).filter(
                    (Outlet.opening_hours.is_(None)) | (Outlet.opening_hours == '')
                ).limit(3).all()
                for outlet in missing_hours:
                    print(f"   • {outlet.name}")
            
            if outlets_missing_services > 0:
                print(f"\n🔍 Sample outlets missing services:")
                missing_services = db.query(Outlet).filter(
                    (Outlet.services.is_(None)) | (Outlet.services == '')
                ).limit(3).all()
                for outlet in missing_services:
                    print(f"   • {outlet.name}")

if __name__ == "__main__":
    verify_outlet_hours_and_services()
