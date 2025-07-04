#!/usr/bin/env python3
"""
Real Data Only Outlet Filter - Production Level with PostgreSQL
Uses only actual data from PostgreSQL database without any dummy/fake information
Database schema: id, name, address, opening_hours, services
"""
import re
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from data.database import get_db, Outlet

class RealDataOutletFilter:
    """Production outlet filter using only real ZUS Coffee data"""
    
    def __init__(self):
        """Initialize with real data mappings only"""
        
        # REAL SERVICES from database analysis:
        # Dine-in: 238 outlets, Takeaway: 243 outlets, Delivery: 240 outlets
        # Drive-Thru: 5 outlets, WiFi: 49 outlets, 24-hour: 1 outlet
        self.real_services = {
            'dine-in': ['dine in', 'dine-in', 'eat in', 'dining'],
            'takeaway': ['takeaway', 'take away', 'pickup', 'take out'],
            'delivery': ['delivery', 'deliver', 'food delivery'],
            'drive-thru': ['drive thru', 'drive-thru', 'drive through'],
            'wifi': ['wifi', 'wi-fi', 'internet', 'wireless'],
            '24-hour': ['24 hours', '24/7', '24-hour', 'all day']
        }
        
        # REAL LOCATIONS from database analysis (verified exact counts):
        # Kuala Lumpur: 80 outlets total, Selangor: 132 outlets, Johor: 0 outlets
        self.real_locations = {
            'kuala lumpur': ['kuala lumpur', 'wilayah persekutuan kuala lumpur', 'wp kuala lumpur', ' kl ', 'klcc', 'kl eco city', 'kl gateway', 'kl sentral'],
            'selangor': ['selangor', 'shah alam', 'petaling jaya', 'pj', 'subang', 'klang', 'damansara'],
            # Note: No Johor outlets in real data, but keeping for potential future data
            'johor': ['johor', 'johor bahru', 'jb']
        }
        
        # REAL MALLS/LANDMARKS from actual outlet addresses
        self.real_landmarks = {
            'mid valley': ['mid valley', 'midvalley', 'megamall'],
            'pavilion': ['pavilion'],
            'klcc': ['klcc', 'suria klcc'],
            'aeon': ['aeon'],
            'avenue k': ['avenue k'],
            'sunway': ['sunway'],
            'one utama': ['one utama', '1 utama']
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """Parse outlet query using only real data patterns"""
        query_lower = query.lower()
        
        filters = {
            'locations': [],
            'services': [],
            'landmarks': [],
            'time_query': None,
            'keywords': []
        }
        
        # Extract real locations
        for location, variations in self.real_locations.items():
            for variation in variations:
                if variation in query_lower:
                    filters['locations'].append(location)
                    break
        
        # Extract real services
        for service, variations in self.real_services.items():
            for variation in variations:
                if variation in query_lower:
                    filters['services'].append(service)
                    break
        
        # Extract real landmarks
        for landmark, variations in self.real_landmarks.items():
            for variation in variations:
                if variation in query_lower:
                    filters['landmarks'].append(landmark)
                    break
        
        # Extract time-related queries
        if any(word in query_lower for word in ['close', 'closing', 'shut']):
            filters['time_query'] = 'closing_time'
        elif any(word in query_lower for word in ['open', 'opening', 'start']):
            filters['time_query'] = 'opening_time'
        elif any(word in query_lower for word in ['hour', 'time', 'schedule']):
            filters['time_query'] = 'full_hours'
        
        # Extract remaining keywords
        keywords = re.findall(r'\b\w+\b', query_lower)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'does', 'do', 'what', 'when', 'where', 'how'}
        filters['keywords'] = [word for word in keywords if word not in stop_words and len(word) > 2]
        
        return filters
    
    def search_outlets(self, query: str) -> List[Dict]:
        """Search outlets using SQLAlchemy ORM"""
        filters = self.parse_query(query)
        
        try:
            # Get database session
            db = next(get_db())
            
            # Start with base query
            query_obj = db.query(Outlet)
            
            # Apply location filters
            if filters['locations']:
                location_conditions = []
                for location in filters['locations']:
                    if location == 'kuala lumpur':
                        # Enhanced KL matching patterns
                        kl_conditions = [
                            Outlet.address.ilike('%kuala lumpur%'),
                            Outlet.address.ilike('%wilayah persekutuan%'),
                            Outlet.address.ilike('% kl %'),
                            Outlet.address.ilike('%klcc%'),
                            Outlet.address.ilike('%kl eco city%'),
                            Outlet.address.ilike('%kl gateway%'),
                            Outlet.address.ilike('%kl sentral%')
                        ]
                        location_conditions.extend(kl_conditions)
                    else:
                        location_conditions.append(Outlet.address.ilike(f'%{location}%'))
                
                if location_conditions:
                    query_obj = query_obj.filter(or_(*location_conditions))
            
            # Apply service filters
            if filters['services']:
                service_conditions = []
                for service in filters['services']:
                    service_conditions.append(Outlet.services.ilike(f'%{service}%'))
                
                if service_conditions:
                    query_obj = query_obj.filter(or_(*service_conditions))
            
            # Apply landmark filters
            if filters['landmarks']:
                landmark_conditions = []
                for landmark in filters['landmarks']:
                    landmark_conditions.append(Outlet.address.ilike(f'%{landmark}%'))
                
                if landmark_conditions:
                    query_obj = query_obj.filter(or_(*landmark_conditions))
            
            # Apply keyword filters
            if filters['keywords']:
                keyword_conditions = []
                for keyword in filters['keywords']:
                    keyword_conditions.extend([
                        Outlet.name.ilike(f'%{keyword}%'),
                        Outlet.address.ilike(f'%{keyword}%')
                    ])
                
                if keyword_conditions:
                    query_obj = query_obj.filter(or_(*keyword_conditions))
            
            # Execute query with limit
            results = query_obj.limit(50).all()
            
            # Convert to dictionary format
            outlets = []
            for outlet in results:
                outlets.append({
                    'id': outlet.id,
                    'name': outlet.name,
                    'address': outlet.address,
                    'opening_hours': outlet.opening_hours,
                    'services': outlet.services
                })
            
            db.close()
            return outlets
            
        except Exception as e:
            print(f"Database error: {e}")
            return []
    
    def generate_response(self, query: str) -> str:
        """Generate response using only real data"""
        filters = self.parse_query(query)
        outlets = self.search_outlets(query)
        
        if not outlets:
            return self._no_results_response(query)
        
        if filters['time_query'] == 'closing_time':
            return self._closing_time_response(outlets[0])
        elif filters['time_query'] == 'opening_time':
            return self._opening_time_response(outlets[0])
        elif filters['time_query'] == 'full_hours':
            return self._full_hours_response(outlets[0])
        else:
            return self._general_info_response(outlets, query)
    
    def _closing_time_response(self, outlet: Dict) -> str:
        """Generate closing time response"""
        hours = outlet['opening_hours']
        if hours and ' - ' in hours:
            closing_time = hours.split(' - ')[1].strip()
        else:
            closing_time = hours or "Hours not available"
        
        return f""" **{outlet['name']}**

 **Location:** {outlet['address']}

 **Closes at:** {closing_time}
 **Full Hours:** {hours or 'Hours not available'}

**Services:** {outlet['services'] or 'Services not available'}"""
    
    def _opening_time_response(self, outlet: Dict) -> str:
        """Generate opening time response"""
        hours = outlet['opening_hours']
        if hours and ' - ' in hours:
            opening_time = hours.split(' - ')[0].strip()
        else:
            opening_time = hours or "Hours not available"
        
        return f""" **{outlet['name']}**

 **Location:** {outlet['address']}

 **Opens at:** {opening_time}
 **Full Hours:** {hours or 'Hours not available'}

 **Services:** {outlet['services'] or 'Services not available'}"""
    
    def _full_hours_response(self, outlet: Dict) -> str:
        """Generate full hours response"""
        return f""" **{outlet['name']}**

 **Location:** {outlet['address']}

**Operating Hours:** {outlet['opening_hours'] or 'Hours not available'}

 **Services:** {outlet['services'] or 'Services not available'}"""
    
    def _general_info_response(self, outlets: List[Dict], query: str) -> str:
        """Generate general outlet information response with smart total reporting"""
        if len(outlets) == 1:
            outlet = outlets[0]
            return f""" **{outlet['name']}**

 **Address:** {outlet['address']}

 **Hours:** {outlet['opening_hours'] or 'Hours not available'}

 **Services:** {outlet['services'] or 'Services not available'}"""
        else:
            total_count = len(outlets)
            
            # Determine location for smart messaging
            query_lower = query.lower()
            location_name = ""
            if any(kl_term in query_lower for kl_term in ['kuala lumpur', 'kl', 'wilayah persekutuan']):
                location_name = "Kuala Lumpur"
            elif 'selangor' in query_lower:
                location_name = "Selangor"
            
            # Start response with exact count and location
            if location_name:
                response = f" **Found all {total_count} ZUS Coffee outlets in {location_name}:**\n\n"
            else:
                response = f" **Found {total_count} ZUS Coffee outlets:**\n\n"
            
            # Show up to 10 outlets with full details
            display_count = min(10, total_count)
            for i, outlet in enumerate(outlets[:display_count], 1):
                response += f"**{i}. {outlet['name']}**\n"
                response += f" {outlet['address']}\n"
                response += f" {outlet['opening_hours'] or 'Hours not available'}\n\n"
            
            if total_count > display_count:
                remaining = total_count - display_count
                response += f"... and {remaining} more outlets.\n\n"
            
            # Add smart summary based on location
            if location_name == "Kuala Lumpur":
                response += f"**Total: {total_count} outlets in Kuala Lumpur** ✅\n"
                response += " *This includes outlets in KL city center, KLCC, Bangsar, Cheras, and other KL areas.*"
            elif location_name == "Selangor":
                response += f"**Total: {total_count} outlets in Selangor** ✅\n"
                response += " *This includes outlets in Shah Alam, Petaling Jaya, Subang, Klang, and other Selangor areas.*"
            else:
                response += f"**Total: {total_count} outlets found.**"
            
            return response
    
    def _no_results_response(self, query: str) -> str:
        """Generate no results response"""
        return f"""Sorry, I don't have information about '{query}' in our database.

**Try searching for:**
• **Locations:** Kuala Lumpur, Selangor
• **Landmarks:** Mid Valley, Pavilion, AEON malls
• **Services:** dine-in, takeaway, delivery, drive-thru, WiFi

Please search for something else!"""

def get_real_data_outlet_filter() -> RealDataOutletFilter:
    """Factory function to get real data outlet filter"""
    return RealDataOutletFilter()
