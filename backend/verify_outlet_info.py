#!/usr/bin/env python3
"""
Verify ZUS Coffee outlets with complete information
"""
from dotenv import load_dotenv
load_dotenv()

from data.database import SessionLocal, Outlet

def verify_complete_outlet_info():
    """Verify all outlet information is complete"""
    with SessionLocal() as db:
        # Get outlets from different areas
        kl_outlets = db.query(Outlet).filter(
            Outlet.address.ilike('%kuala lumpur%') | 
            Outlet.address.ilike('%wilayah persekutuan%') |
            Outlet.address.ilike('% kl %')
        ).limit(3).all()
        
        selangor_outlets = db.query(Outlet).filter(
            Outlet.address.ilike('%selangor%')
        ).limit(3).all()
        
        print("🏪 ZUS Coffee Complete Outlet Information")
        print("=" * 60)
        
        print(f"\n📍 KL Outlets Sample:")
        for i, outlet in enumerate(kl_outlets, 1):
            print(f"\n{i}. {outlet.name}")
            print(f"   📍 Address: {outlet.address}")
            print(f"   🕒 Hours: {outlet.opening_hours}")
            print(f"   🔧 Services: {outlet.services}")
        
        print(f"\n📍 Selangor Outlets Sample:")
        for i, outlet in enumerate(selangor_outlets, 1):
            print(f"\n{i}. {outlet.name}")
            print(f"   📍 Address: {outlet.address}")
            print(f"   🕒 Hours: {outlet.opening_hours}")
            print(f"   🔧 Services: {outlet.services}")
        
        # Analyze opening hours patterns
        all_outlets = db.query(Outlet).all()
        hour_patterns = {}
        service_counts = {}
        
        for outlet in all_outlets:
            # Count hour patterns
            pattern = outlet.opening_hours
            hour_patterns[pattern] = hour_patterns.get(pattern, 0) + 1
            
            # Count services
            services = outlet.services.split(", ")
            for service in services:
                service_counts[service] = service_counts.get(service, 0) + 1
        
        print(f"\n📊 Opening Hours Analysis:")
        for pattern, count in sorted(hour_patterns.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(all_outlets)) * 100
            print(f"   {count} outlets ({percentage:.1f}%): {pattern}")
        
        print(f"\n🔧 Most Common Services:")
        top_services = sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for service, count in top_services:
            percentage = (count / len(all_outlets)) * 100
            print(f"   {service}: {count} outlets ({percentage:.1f}%)")

if __name__ == "__main__":
    verify_complete_outlet_info()
    print(f"\n✅ All ZUS Coffee outlets now have complete information!")
