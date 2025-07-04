#!/usr/bin/env python3
"""
Verify outlets have opening hours and services in PostgreSQL
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Outlet

def verify_outlet_hours_and_services():
    """Verify all outlets have opening hours and services"""
    print("🔍 ZUS Coffee Outlets - Hours & Services Verification")
    print("=" * 60)
    
    with SessionLocal() as db:
        # Get total count
        total_outlets = db.query(Outlet).count()
        print(f"📊 Total outlets in database: {total_outlets}")
        
        # Check completeness
        outlets_with_hours = db.query(Outlet).filter(
            Outlet.opening_hours.isnot(None),
            Outlet.opening_hours != ""
        ).count()
        
        outlets_with_services = db.query(Outlet).filter(
            Outlet.services.isnot(None),
            Outlet.services != ""
        ).count()
        
        print(f"✅ Outlets with opening hours: {outlets_with_hours}/{total_outlets}")
        print(f"✅ Outlets with services: {outlets_with_services}/{total_outlets}")
        
        # Show sample outlets with full details
        print(f"\n📋 Sample Outlets with Complete Information:")
        sample_outlets = db.query(Outlet).limit(5).all()
        
        for i, outlet in enumerate(sample_outlets, 1):
            print(f"\n{i}. {outlet.name}")
            print(f"   📍 Address: {outlet.address[:70]}...")
            print(f"   🕒 Hours: {outlet.opening_hours}")
            print(f"   🔧 Services: {outlet.services[:80]}...")
        
        # Analyze opening hours patterns
        print(f"\n📊 Opening Hours Analysis:")
        hour_patterns = {}
        for outlet in db.query(Outlet).all():
            pattern = outlet.opening_hours
            hour_patterns[pattern] = hour_patterns.get(pattern, 0) + 1
        
        for pattern, count in sorted(hour_patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / total_outlets) * 100
            print(f"   {count} outlets ({percentage:.1f}%): {pattern}")
        
        # Analyze services
        print(f"\n🔧 Most Common Services:")
        service_counts = {}
        for outlet in db.query(Outlet).all():
            if outlet.services:
                services = outlet.services.split(", ")
                for service in services:
                    service_counts[service] = service_counts.get(service, 0) + 1
        
        top_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        for service, count in top_services:
            percentage = (count / total_outlets) * 100
            print(f"   {service}: {count} outlets ({percentage:.1f}%)")
        
        # Final status
        print(f"\n🎯 VERIFICATION RESULT:")
        if outlets_with_hours == total_outlets and outlets_with_services == total_outlets:
            print(f"   🎉 SUCCESS! All {total_outlets} outlets have complete information")
            print(f"   ✅ Opening hours: COMPLETE")
            print(f"   ✅ Services: COMPLETE")
            print(f"   🗄️ Database is production-ready!")
        else:
            print(f"   ⚠️ INCOMPLETE: Some outlets missing information")
            print(f"   Missing hours: {total_outlets - outlets_with_hours}")
            print(f"   Missing services: {total_outlets - outlets_with_services}")

if __name__ == "__main__":
    verify_outlet_hours_and_services()
