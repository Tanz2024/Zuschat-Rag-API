import re
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from models import (
    Intent, AgentAction, ConversationState, ChatMessage, MessageRole,
    ChatRequest, ChatResponse
)
from tools.calculator import get_calculator
# Try to import ML-based search, fallback to simple search
try:
    from services.product_search_service import get_vector_store
    USE_ML_SEARCH = True
except ImportError:
    from services.simple_product_search import get_vector_store
    USE_ML_SEARCH = False
    print("ML dependencies not available, using simple product search")
from services.real_data_outlet_filter import get_real_data_outlet_filter
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationMemory:
    """Manages conversation state and memory."""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationState] = {}
        self.session_timeout = timedelta(hours=2)
    
    def get_or_create_session(self, session_id: str = None) -> ConversationState:
        """Get existing session or create new one."""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationState(session_id=session_id)
        
        return self.sessions[session_id]
    
    def update_session(self, session: ConversationState):
        """Update session with new information."""
        session.updated_at = datetime.now()
        self.sessions[session.session_id] = session
    
    def _cleanup_expired_sessions(self):
        """Remove expired sessions to free memory."""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session.updated_at > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")

class IntentClassifier:
    """Classifies user intents from natural language."""
    
    def __init__(self):
        # Intent patterns and keywords
        self.intent_patterns = {
            Intent.GREETING: [
                r'\b(hi|hello|hey|good\s+(morning|afternoon|evening)|greetings)\b',
                r'\bhow\s+are\s+you\b',
                r'\bwhat\'?s\s+up\b'
            ],
            Intent.PRODUCT_SEARCH: [
                r'\b(product|drinkware|tumbler|mug|cup|bottle|flask|glass|travel|insulated|thermal|stainless|steel)\b',
                r'\b(show|find|search|look\s+for|tell\s+me\s+about|what|which|any)\s+.*\b(product|item|drinkware|tumbler|mug|cup|bottle|flask)\b',
                r'\b(what|which)\s+.*\b(products|items|drinkware|tumblers|mugs|cups|bottles)\b',
                r'\b(recommend|suggest)\s+.*\b(product|drinkware)\b',
                r'\b(price|cost|how\s+much)\b.*\b(product|drinkware|tumbler|mug)\b',
                r'\b(coffee|drink|beverage)\s+(mug|cup|tumbler|bottle)\b',
                r'\b(zus)\s+(product|item|drinkware|tumbler|mug|cup|bottle)\b',
                r'\bcoffee\s+related\s+(product|item)\b',
                r'\b(under|below|above|over)\s+rm\s*\d+\b',
                r'\b(cheap|affordable|expensive|budget)\s+.*(tumbler|mug|cup|bottle|product|item)\b',
                r'\bfind\s+.*(tumbler|mug|cup|bottle|product|item|drinkware)\b',
                # Enhanced patterns for material filtering
                r'\b(glass|acrylic|steel|stainless\s+steel|bamboo|plastic|ceramic|metal)\s+(tumbler|mug|cup|bottle|product|item|drinkware)\b',
                r'\b(tumbler|mug|cup|bottle|product|item|drinkware)\s+(made\s+of|in|with)\s+(glass|acrylic|steel|bamboo|plastic|ceramic)\b',
                # Enhanced patterns for feature filtering
                r'\b(eco-friendly|sustainable|thermal|insulated|leak-proof|spill-resistant|dishwasher\s+safe)\s+(tumbler|mug|cup|bottle|product|item|drinkware)\b',
                r'\b(tumbler|mug|cup|bottle|product|item|drinkware)\s+(that\s+is|with|having)\s+(eco-friendly|thermal|insulated|leak-proof)\b',
                # Enhanced patterns for price sorting
                r'\b(cheapest|most\s+affordable|lowest\s+price)\s+(tumbler|mug|cup|bottle|product|item|drinkware)\b',
                r'\b(most\s+expensive|highest\s+price|premium)\s+(tumbler|mug|cup|bottle|product|item|drinkware)\b',
                r'\b(best\s+value|budget\s+friendly)\s+(tumbler|mug|cup|bottle|product|item|drinkware)\b',
                # Enhanced patterns for type filtering
                r'\b(travel|thermal|coffee|tea|water|sports)\s+(mug|cup|tumbler|bottle)\b',
                r'\b(large|small|compact|portable)\s+(tumbler|mug|cup|bottle|product|item|drinkware)\b',
                # Complex combination patterns
                r'\b(glass|steel|bamboo|acrylic)\s+(thermal|insulated|eco-friendly)\s+(tumbler|mug|cup|bottle)\b',
                r'\b(cheapest|most\s+affordable)\s+(thermal|insulated|eco-friendly|glass|steel)\s+(tumbler|mug|cup|bottle)\b',
                r'\b(eco-friendly|sustainable)\s+(under|below)\s+rm\s*\d+\b',
                r'\b(thermal|insulated)\s+(under|below)\s+rm\s*\d+\b'
            ],
            Intent.OUTLET_SEARCH: [
                r'\b(outlet|store|shop|location|branch|cafe|coffee\s+shop)\b',
                r'\b(where|find|show|locate)\s+.*\b(outlet|store|shop|branch|cafe)\b',
                r'\b(opening|hours|time|when)\s+.*\b(open|close)\b',
                r'\b(address|location)\s+.*\b(outlet|store)\b',
                r'\bhow\s+many\s+.*\b(outlet|store|branch)\b',
                r'\b(nearest|closest|near)\s+.*\b(outlet|store|shop|branch)\b',
                r'\bzus\s+(outlet|store|shop|location|branch|cafe)\b',
                # Enhanced Malaysian location patterns
                r'\b(near|in|at)\s+(klcc|kl|kuala\s+lumpur|selangor|johor|penang)\b',
                r'\b(near|in|at)\s+(bukit\s+bintang|mid\s+valley|pavilion|bangsar|mont\s+kiara)\b',
                r'\b(near|in|at)\s+(damansara|sunway|ampang|cheras|kepong|setapak)\b',
                r'\bzus\s+(near|in|at)\s+\w+',
                r'\bcoffee\s+(near|in|at)\s+\w+',
                r'\bfind\s+zus\s+(near|in|at)\s+\w+',
                r'\bzus\s+coffee\s+(near|in|at|around)\s+\w+',
                # Enhanced patterns for city filtering
                r'\b(petaling\s+jaya|pj|shah\s+alam|klang|puchong|kajang|cyberjaya)\s+(outlet|store|branch)\b',
                r'\b(outlet|store|branch)\s+(in|at)\s+(petaling\s+jaya|pj|shah\s+alam|klang|cyberjaya)\b',
                r'\b(johor\s+bahru|jb|georgetown|ipoh|malacca|melaka)\s+(outlet|store|branch)\b',
                # Enhanced patterns for state filtering
                r'\b(selangor|kuala\s+lumpur|johor|penang|perak|malacca)\s+(outlet|store|branch)\b',
                r'\b(outlet|store|branch)\s+(in|at)\s+(selangor|kuala\s+lumpur|johor|penang)\b',
                # Enhanced patterns for service filtering
                r'\b(dine-?in|takeaway|delivery|drive-?thru|wifi)\s+(outlet|store|branch)\b',
                r'\b(outlet|store|branch)\s+(with|having|that\s+has)\s+(dine-?in|takeaway|delivery|drive-?thru|wifi)\b',
                # Enhanced patterns for time filtering
                r'\b(open\s+early|close\s+late|24\s+hours|24/7)\s+(outlet|store|branch)\b',
                r'\b(outlet|store|branch)\s+(open|close)\s+(early|late|after|before)\b',
                r'\bopen\s+(after|before)\s+\d{1,2}(am|pm)?\b',
                r'\bclose\s+(after|before)\s+\d{1,2}(am|pm)?\b',
                # Enhanced patterns for name filtering
                r'\b(ss2|ss15|klcc|pavilion|mid\s+valley|one\s+utama|curve)\s+(outlet|store|branch)\b',
                r'\bdo\s+you\s+have\s+(ss2|ss15|klcc|pavilion|mid\s+valley)\b',
                # Complex combination patterns
                r'\b(dine-?in|takeaway|drive-?thru)\s+(outlet|store)\s+(in|at)\s+(kl|selangor|pj)\b',
                r'\b(early|late)\s+(outlet|store)\s+(in|near)\s+\w+\b',
                r'\b24\s+hours?\s+(outlet|store)\s+(in|near)\s+\w+\b'
            ],
            Intent.CALCULATION: [
                r'\b(calculate|compute|solve)\s+.*\d+',  # More specific - must include numbers
                r'\bfind\s+.*\b(result|answer|solution)\b',  # Mathematical context
                r'\bfind\s+.*\b(square\s+root|factorial|percentage|total|sum|average)\b',  # Math functions
                r'\bwhat\s+is\s+\d+.*[+\-*/^%]',
                r'\bwhat\s+is\s+\d+.*\b(plus|minus|times|divided|multiplied)\b',
                r'\d+\s*[+\-*/^%]\s*\d+',
                r'\b(add|subtract|multiply|divide|plus|minus|times)\b.*\d+',
                r'\b(percentage|percent|%)\b.*\d+',
                r'\b(square\s+root|sqrt|sin|cos|tan|log)\b',
                r'\bwhat\s+is\s+.*\d+.*\d+',  # "what is 20 times 5"
                r'\b\d+\s+(times|multiplied\s+by|divided\s+by|plus|minus|added\s+to|subtracted\s+from)\s+\d+\b',
                r'\bhow\s+much\s+is\b.*\d+',  # Mathematical "how much"
                r'\bif\s+.*\b(hours?|minutes?|work|drink|wait)\b.*\d+',  # Time calculations
                r'\bif\s+.*\b(spend|cost|pay|price)\b.*rm\s*\d+',  # Money calculations
                r'\bif\s+.*rm\s*\d+.*\b(day|week|month|year)\b.*\d+',  # Spending over time
                r'\brm\s*\d+.*\b(day|week|month|year|time)\b.*\d+.*\bhow\s+much\b',  # RM spending calculations
                r'\bspend\s+rm\s*\d+.*\d+.*\b(days?|weeks?|months?)\b',  # Direct spending patterns
                # Purchase calculations
                r'\bif\s+i\s+buy\s+\d+.*rm\s*\d+.*each',
                r'\bbuy\s+\d+.*rm\s*\d+.*each',
                r'\d+.*(?:drinks?|items?|cups?).*rm\s*\d+.*each',
                # Reverse calculations
                r'\bhow\s+many.*buy.*with\s+rm\s*\d+',
                r'\bhow\s+many.*rm\s*\d+.*if\s+each\s+costs?',
                # Tax calculations
                r'\btotal\s+with\s+\d+%.*rm\s*\d+',
                r'\badd\s+\d+%.*to\s+rm\s*\d+',
                r'\d+%\s+(?:sst|tax|gst)',
                # Work/consumption calculations
                r'\bwork\s+\d+\s+hours?.*week',
                r'\bdrink\s+\d+.*day.*month',
                # Time calculations
                r'\boutlet\s+opens?\s+at.*arrive\s+at',
                r'\badd\s+\d+\s+minutes?\s+to',
                # Challenge calculations
                r'\baverage\s+price\s+of\s+\d+',
                r'\bsplit\s+rm\s*\d+.*\d+\s+people'
            ]
        }
        
        # Context keywords for follow-up detection
        self.context_keywords = {
            'product_follow_up': ['more', 'details', 'info', 'specifications', 'specs', 'features'],
            'outlet_follow_up': ['hours', 'address', 'phone', 'contact', 'direction'],
            'clarification': ['what', 'which', 'where', 'when', 'how', 'why']
        }
    
    def classify_intent(self, text: str, context: Dict[str, Any] = None) -> Tuple[Intent, float]:
        """Classify user intent with confidence score."""
        text_lower = text.lower().strip()
        
        # First check for non-dataset queries that should be immediately rejected
        non_dataset_indicators = [
            'convert', 'conversion', 'milliliter', 'ml', 'ounce', 'oz', 'cup size', 'cup sizes',
            'litre', 'liter', 'pint', 'gallon', 'fluid ounce',
            'customer service', 'customer support', 'help desk', 'helpline', 'support team',
            'complaint', 'feedback', 'how to contact', 'contact zus', 'phone number', 'email',
            'headquarters', 'head office', 'corporate office',
            'how to make coffee', 'coffee recipe', 'brewing method', 'coffee tips', 'barista tips',
            'health benefits', 'caffeine content', 'nutrition facts', 'calories',
            'thermal capacity', 'insulation rating', 'material properties', 'manufacturing process',
            'starbucks', 'coffee bean', 'old town white coffee', 'costa coffee'
        ]
        
        # If query contains non-dataset indicators, classify as general question with low confidence
        # This will trigger the rejection logic in _plan_general_question
        if any(indicator in text_lower for indicator in non_dataset_indicators):
            return Intent.GENERAL_CHAT, 0.1
        
        scores = {}
        
        # Calculate scores for each intent
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            pattern_matches = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1.0
                    pattern_matches += 1
            
            # Use a different scoring approach - give more weight to multiple matches
            # but don't penalize having many patterns
            if pattern_matches > 0:
                # Base score from matches, with bonus for multiple matches
                base_score = pattern_matches / len(patterns)
                bonus = min(pattern_matches * 0.2, 0.5)  # Up to 50% bonus for multiple matches
                scores[intent] = min(base_score + bonus, 1.0)
            else:
                scores[intent] = 0.0
        
        # Context-based adjustments
        if context:
            last_intent = context.get('current_intent')
            last_action = context.get('last_action')
            
            # Boost related intents based on context
            if last_intent == Intent.PRODUCT_SEARCH:
                if any(keyword in text_lower for keyword in self.context_keywords['product_follow_up']):
                    scores[Intent.PRODUCT_SEARCH] += 0.3
            
            elif last_intent == Intent.OUTLET_SEARCH:
                if any(keyword in text_lower for keyword in self.context_keywords['outlet_follow_up']):
                    scores[Intent.OUTLET_SEARCH] += 0.3
        
        # Find best intent
        if not scores or max(scores.values()) == 0:
            return Intent.GENERAL_CHAT, 0.1
        
        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent]
        
        # Lower minimum confidence threshold to be more inclusive
        if confidence < 0.1:
            return Intent.GENERAL_CHAT, confidence
        
        return best_intent, confidence

class AgentPlanner:
    """Plans and executes agent actions based on intent and context."""
    
    def __init__(self):
        self.calculator = get_calculator()
        self.vector_store = get_vector_store()
        self.real_data_outlet_filter = get_real_data_outlet_filter()
        
        # Action planning rules
        self.action_rules = {
            Intent.GREETING: self._plan_greeting,
            Intent.PRODUCT_SEARCH: self._plan_product_inquiry,
            Intent.OUTLET_SEARCH: self._plan_outlet_inquiry,
            Intent.CALCULATION: self._plan_calculation,
            Intent.GENERAL_CHAT: self._plan_general_question
        }
    
    def plan_action(self, intent: Intent, text: str, context: Dict[str, Any]) -> Tuple[AgentAction, Dict[str, Any]]:
        """Plan the next action based on intent and context."""
        if intent in self.action_rules:
            return self.action_rules[intent](text, context)
        else:
            return AgentAction.REQUEST_CLARIFICATION, {
                'message': "I'm not sure how to help with that. Could you please rephrase your question?"
            }
    
    def _plan_greeting(self, text: str, context: Dict[str, Any]) -> Tuple[AgentAction, Dict[str, Any]]:
        """Plan response for greeting."""
        return AgentAction.PROVIDE_ANSWER, {
            'message': "Hello! I'm your ZUS Coffee assistant. I can help you with product information, outlet locations, and simple calculations. How can I assist you today?"
        }
    
    def _plan_product_inquiry(self, text: str, context: Dict[str, Any]) -> Tuple[AgentAction, Dict[str, Any]]:
        """Plan response for product inquiries."""
        # Always try to search for products when product intent is detected
        return AgentAction.CALL_PRODUCT_SEARCH, {
            'query': text,
            'top_k': 15
        }
    
    def _plan_outlet_inquiry(self, text: str, context: Dict[str, Any]) -> Tuple[AgentAction, Dict[str, Any]]:
        """Plan response for outlet inquiries."""
        return AgentAction.CALL_OUTLET_SEARCH, {
            'query': text
        }
    
    def _plan_calculation(self, text: str, context: Dict[str, Any]) -> Tuple[AgentAction, Dict[str, Any]]:
        """Plan response for calculations."""
        # Try to extract mathematical expression
        expression = self.calculator.parse_calculation_intent(text)
        
        if expression and self._is_valid_calculation_query(text):
            return AgentAction.CALL_CALCULATOR, {
                'expression': expression,
                'original_query': text
            }
        else:
            return AgentAction.ASK_FOLLOWUP, {
                'message': """I can help with calculations! Please try:

**Examples:**
• `2 + 3 * 4`
• `15% of 120`
• `Calculate 15% tip on RM 45`
• `What's the square root of 64?`
• `Find 2 to the power of 3`

What calculation would you like me to help with?"""
            }
    
    def _plan_general_question(self, text: str, context: Dict[str, Any]) -> Tuple[AgentAction, Dict[str, Any]]:
        """Plan response for general questions with improved routing."""
        text_lower = text.lower()
        
        # Check for non-dataset queries that should not be answered
        non_dataset_queries = [
            # Unit conversions
            'convert', 'conversion', 'milliliter', 'ml', 'ounce', 'oz', 'cup size', 'cup sizes',
            'litre', 'liter', 'pint', 'gallon', 'fluid ounce',
            # Customer service/contact information
            'customer service', 'customer support', 'help desk', 'helpline', 'support team',
            'complaint', 'feedback', 'how to contact', 'contact zus', 'phone number', 'email',
            'headquarters', 'head office', 'corporate office',
            # General advice not related to ZUS data
            'how to make coffee', 'coffee recipe', 'brewing method', 'coffee tips', 'barista tips',
            'how do i brew', 'how to brew', 'brew the perfect', 'perfect coffee', 'make cappuccino',
            'make latte', 'make espresso', 'coffee at home', 'home brewing', 'brewing guide',
            'health benefits', 'caffeine content', 'nutrition facts', 'calories',
            # Technical specifications not in product data
            'thermal capacity', 'insulation rating', 'material properties', 'manufacturing process',
            # Competitor information
            'starbucks', 'coffee bean', 'old town white coffee', 'costa coffee'
        ]
        
        # Check if query is about non-dataset information
        if any(phrase in text_lower for phrase in non_dataset_queries):
            # Extract the main topic for a more specific response
            main_topic = None
            if any(word in text_lower for word in ['convert', 'conversion', 'ml', 'milliliter', 'cup size']):
                main_topic = "cup size conversion"
            elif any(word in text_lower for word in ['customer service', 'contact', 'support', 'phone', 'email']):
                main_topic = "customer service contact information"
            elif any(word in text_lower for word in ['recipe', 'brewing', 'how to make']):
                main_topic = "coffee brewing instructions"
            elif any(word in text_lower for word in ['health', 'nutrition', 'calories', 'caffeine']):
                main_topic = "nutritional information"
            else:
                main_topic = "that information"
            
            return AgentAction.PROVIDE_ANSWER, {
                'message': f"Sorry, I don't have information about {main_topic}, please search for something else.\n\nI can help you with:\n• ZUS Coffee products and merchandise\n• ZUS Coffee outlet locations and hours\n• Simple calculations for pricing\n\nWhat would you like to know about ZUS Coffee?"
            }
        
        # Check for ZUS Coffee general information (only basic info that we know)
        zus_general = ['zus coffee', 'about zus', 'what is zus', 'zus brand', 'company', 'zus story']
        if any(phrase in text_lower for phrase in zus_general):
            return AgentAction.PROVIDE_ANSWER, {
                'message': """ZUS Coffee is Malaysia's specialty coffee chain. I can help you find information about our products and outlet locations.

What I can assist you with:
• **Product Information**: Search for specific coffee drinks, food items, or merchandise
• **Outlet Locations**: Find ZUS Coffee outlets near you or get their details
• **Calculations**: Help with mathematical calculations for pricing or quantities

What would you like to know about ZUS Coffee products or outlets?"""
            }
        
        # Check for product-related keywords that might have been missed
        product_indicators = ['coffee', 'drink', 'beverage', 'latte', 'cappuccino', 'americano', 
                            'tea', 'matcha', 'container', 'cup', 'mug', 'tumbler', 'bottle',
                            'hot', 'cold', 'iced', 'thermal', 'buy', 'purchase', 'price', 'cost', 
                            'menu', 'merchandise', 'item', 'gift', 'souvenir', 'collection']
        
        # Check for location/outlet indicators
        outlet_indicators = ['where', 'location', 'address', 'near', 'nearby', 'closest', 'find', 
                           'hours', 'open', 'close', 'opening', 'closing', 'visit', 'go to', 
                           'direction', 'outlet', 'store', 'branch']
        
        # Check for calculation indicators
        calc_indicators = ['how much', 'total', 'sum', 'calculate', 'calculation', 'math', 
                         'add', 'plus', 'minus', 'subtract', 'times', 'multiply', 'divide', 
                         'percentage', 'percent', '=', '+', '-', '*', '/', 'x']
        
        # Smart routing based on content analysis
        if any(indicator in text_lower for indicator in product_indicators):
            return AgentAction.CALL_PRODUCT_SEARCH, {
                'query': text,
                'top_k': 15
            }
        elif any(indicator in text_lower for indicator in outlet_indicators):
            return AgentAction.CALL_OUTLET_SEARCH, {
                'query': text
            }
        elif any(indicator in text_lower for indicator in calc_indicators) or any(char.isdigit() for char in text):
            # Try to extract mathematical expression
            expression = self.calculator.parse_calculation_intent(text)
            if expression and self._is_valid_calculation_query(text):
                return AgentAction.CALL_CALCULATOR, {
                    'expression': expression,
                    'original_query': text
                }
        
        # Check if it's a follow-up to previous context
        last_intent = context.get('current_intent')
        
        if last_intent == Intent.PRODUCT_SEARCH:
            return AgentAction.CALL_PRODUCT_SEARCH, {
                'query': text,
                'top_k': 15
            }
        elif last_intent == Intent.OUTLET_SEARCH:
            return AgentAction.CALL_OUTLET_SEARCH, {
                'query': text
            }
        
        # Default fallback with helpful suggestions
        return AgentAction.PROVIDE_ANSWER, {
            'message': """Sorry, I don't have information about that topic, please search for something else.

I can help you with:
• **Product Information**: Ask about our coffee drinks, food items, or merchandise
• **Outlet Locations**: Find ZUS Coffee outlets near you or get contact details
• **Calculations**: Help with mathematical calculations for pricing or quantities

What would you like to know about ZUS Coffee products or outlets?"""
        }
    
    def _is_valid_calculation_query(self, text: str) -> bool:
        """Check if the text is actually a calculation query and not just containing numbers"""
        text_lower = text.lower()
        
        # Strong calculation indicators
        strong_calc_words = ['calculate', 'compute', 'solve', 'what is', 'find', 'tip', 'percent', '%', 
                           'plus', 'minus', 'times', 'divide', 'multiply', 'square', 'sqrt', 'power',
                           'root', 'average', 'mean', 'sum', 'total', 'add', 'subtract', 'split',
                           'each', 'per', 'at rm', 'cost', 'price per', 'how much', 'how many']
        
        # Math operators
        has_operators = any(op in text for op in ['+', '-', '*', '/', '^', '=', '%', 'x'])
        
        # Mathematical expressions pattern
        import re
        math_patterns = [
            r'\d+\s*[\+\-\*/\^%]\s*\d+',  # Basic math operations
            r'\d+\s+(plus|minus|times|divided\s+by|multiplied\s+by)\s+\d+',  # Word operations
            r'\d+%\s+of\s+\d+',  # Percentage calculations
            r'square\s+root\s+of\s+\d+',  # Square root
            r'sqrt\s*\(\s*\d+\s*\)',  # sqrt function
            r'\d+\s+at\s+rm\s*\d+',  # Unit pricing (e.g., "3 mugs at RM25 each")
            r'split\s+rm\s*\d+',  # Split money
            r'average\s+.*\d+.*\d+',  # Average calculations
        ]
        
        # Check for mathematical patterns
        for pattern in math_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Strong calculation intent
        if any(word in text_lower for word in strong_calc_words) or has_operators:
            return True
        
        # Check if it's just product names with numbers (not calculations)
        # Only reject if it's clearly a product search and has no calculation indicators
        product_words = ['coffee', 'cup', 'mug', 'bottle', 'tumbler', 'zus', 'ml', 'oz', 'collection']
        has_product_words = any(word in text_lower for word in product_words)
        has_calc_indicators = any(word in text_lower for word in strong_calc_words) or has_operators
        
        # If it has product words but NO calculation indicators, it's probably a product search
        if has_product_words and not has_calc_indicators:
            return False
        
        # If it contains numbers and some mathematical context, treat as calculation
        has_numbers = bool(re.search(r'\d+', text))
        math_context = any(word in text_lower for word in ['total', 'sum', 'average', 'each', 'per'])
        
        return has_numbers and math_context

class AgentController:
    """Main controller that orchestrates the conversation flow."""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.intent_classifier = IntentClassifier()
        self.planner = AgentPlanner()
        self.calculator = get_calculator()
        self.vector_store = get_vector_store()
        self.real_data_outlet_filter = get_real_data_outlet_filter()
    
    async def process_message(self, request: ChatRequest, db: Session) -> ChatResponse:
        """Process user message and generate response."""
        try:
            # Get or create conversation session
            session = self.memory.get_or_create_session(request.session_id)
            
            # Add user message to history
            user_message = ChatMessage(
                role=MessageRole.USER,
                content=request.message
            )
            session.messages.append(user_message)
            
            # Classify intent
            intent, confidence = self.intent_classifier.classify_intent(
                request.message, 
                session.context
            )
            
            # Update session context
            session.current_intent = intent
            session.context.update({
                'last_user_message': request.message,
                'intent_confidence': confidence
            })
            
            logger.info(f"Intent: {intent} (confidence: {confidence:.2f})")
            
            # Standard intent-based processing
            # Plan action
            action, action_params = self.planner.plan_action(
                intent, 
                request.message, 
                session.context
            )
            
            session.last_action = action
            logger.info(f"Planned action: {action}")
            
            # Execute action
            response_text, tool_used = await self._execute_action(action, action_params, db)
            
            # Add assistant response to history
            assistant_message = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=response_text
            )
            session.messages.append(assistant_message)
            
            # Update session
            self.memory.update_session(session)
            
            return ChatResponse(
                message=response_text,
                session_id=session.session_id,
                action=action,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return ChatResponse(
                message="I apologize, but I encountered an error while processing your request. Please try again.",
                session_id=request.session_id or str(uuid.uuid4()),
                action=AgentAction.PROVIDE_ANSWER,
                confidence=0.0
            )
    
    async def _execute_action(self, action: AgentAction, params: Dict[str, Any], db: Session) -> Tuple[str, Optional[str]]:
        """Execute the planned action and return response."""
        try:
            if action == AgentAction.PROVIDE_ANSWER:
                return params['message'], None
            
            elif action == AgentAction.ASK_FOLLOWUP:
                return params['message'], None
            
            elif action == AgentAction.CALL_PRODUCT_SEARCH:
                return await self._execute_product_search(params), "product_search"
            
            elif action == AgentAction.CALL_OUTLET_SEARCH:
                return await self._execute_outlet_search(params, db), "outlet_search"
            
            elif action == AgentAction.CALL_CALCULATOR:
                return await self._execute_calculation(params), "calculator"
            
            elif action == AgentAction.REQUEST_CLARIFICATION:
                return params.get('message', "Could you please clarify your request?"), None
            
            else:
                return "I'm not sure how to handle that request.", None
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return f"I encountered an error while {action.value.replace('_', ' ')}. Please try again.", None
    
    async def _execute_product_search(self, params: Dict[str, Any]) -> str:
        """Execute product search using enhanced vector store."""
        try:
            query = params['query']
            top_k = params.get('top_k', 5)
            
            results = self.vector_store.search(query, top_k)
            summary = self.vector_store.generate_summary(query, results)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in product search: {e}")
            return "I'm having trouble searching for products right now. Please try again later."
    
    async def _execute_outlet_search(self, params: Dict[str, Any], db: Session) -> str:
        """Execute outlet search using real data filter."""
        try:
            query = params['query']
            
            result = self.real_data_outlet_filter.generate_response(query)
            
            # Real data filter returns formatted response string
            return result
            
        except Exception as e:
            logger.error(f"Error executing outlet search: {e}")
            return "I'm having trouble searching for outlets right now. Please try again later."
    
    async def _execute_calculation(self, params: Dict[str, Any]) -> str:
        """Execute calculation using calculator tool."""
        try:
            expression = params['expression']
            original_query = params.get('original_query', expression)
            
            # Validate the expression before calculation
            if not expression or not expression.strip():
                return "Please provide a valid mathematical expression to calculate."
            
            # First try to parse natural language into math expression if needed
            if original_query != expression:
                # Expression was already parsed, use it directly
                pass
            else:
                # Try to parse again if original query wasn't processed
                parsed_expression = self.calculator.parse_calculation_intent(original_query)
                if parsed_expression and parsed_expression != expression:
                    expression = parsed_expression
            
            # Clean up common issues
            expression = self._clean_calculation_expression(expression)
            
            # Validate again after cleaning
            if not expression or not expression.strip():
                return self._get_calculation_help(original_query, "Empty expression after processing")
            
            result = self.calculator.calculate(expression)
            
            if result['is_valid']:
                # Format the result nicely
                result_value = result['result']
                if result_value == int(result_value):
                    result_value = int(result_value)
                
                return f"**Result: {result_value}**\n\nCalculation: `{result['normalized_expression']}`"
            else:
                # Provide helpful suggestions for common errors
                error_msg = result['error_message']
                
                # Try to give more specific help based on the error
                specific_help = self._get_calculation_help(original_query, error_msg)
                
                return f"I couldn't calculate that: {error_msg}\n\n{specific_help}"
                
        except Exception as e:
            logger.error(f"Error in calculation: {e}")
            return f"""I'm having trouble with that calculation. The error was: {str(e)}

Please try a simpler format like:
• `2 + 3`
• `15 * 0.20`
• `sqrt(25)`

What calculation would you like me to help with?"""
    
    def _clean_calculation_expression(self, expression: str) -> str:
        """Clean up common issues in calculation expressions"""
        # Remove common words that might interfere
        expression = re.sub(r'\b(calculate|compute|solve|find|what\s+is|equals?)\b', '', expression, flags=re.IGNORECASE)
        
        # Remove currency symbols but keep numbers
        expression = re.sub(r'RM\s*', '', expression)
        expression = re.sub(r'\$\s*', '', expression)
        
        # Handle common phrases
        expression = re.sub(r'\b(\d+)\s*percent\s+of\s+(\d+)', r'(\1/100) * \2', expression)
        expression = re.sub(r'\b(\d+)%\s+of\s+(\d+)', r'(\1/100) * \2', expression)
        expression = re.sub(r'\btip\s+on\b', '', expression, flags=re.IGNORECASE)
        
        # Clean up extra spaces and punctuation
        expression = re.sub(r'[?!.]', '', expression)
        expression = re.sub(r'\s+', ' ', expression).strip()
        
        return expression
    
    def _get_calculation_help(self, original_query: str, error_msg: str) -> str:
        """Get specific help based on the query and error"""
        original_lower = original_query.lower()
        
        # Specific help for different types of queries
        if 'percent' in original_lower or '%' in original_query:
            return """**For percentage calculations, try:**
• `15% of 120` → Use: `15 * 120 / 100` or `0.15 * 120`
• `15% tip on 45` → Use: `45 * 0.15` or `45 * 15 / 100`
• `What's 20% of 250?` → Use: `20 * 250 / 100`"""
        
        elif 'tip' in original_lower:
            return """**For tip calculations, try:**
• `15% tip on RM 45` → Use: `45 * 0.15`
• `20% tip on 120` → Use: `120 * 0.20`
• `Tip amount for RM 85 at 18%` → Use: `85 * 0.18`"""
        
        elif 'square' in original_lower or 'sqrt' in original_lower:
            return """**For square root calculations, try:**
• `sqrt(16)` 
• `square root of 25` → Use: `sqrt(25)`
• `√64` → Use: `sqrt(64)`"""
        
        elif 'power' in original_lower or '^' in original_query:
            return """**For power calculations, try:**
• `2^3` or `2**3` (both work for 2 to the power of 3)
• `5 to the power of 2` → Use: `5**2` or `5^2`
• `pow(2, 8)` → Use: `pow(2, 8)` or `2**8`"""
        
        else:
            return """**Common calculation formats:**
• Basic math: `2 + 3 * 4`
• Percentages: `15 * 120 / 100` or `0.15 * 120`
• Square root: `sqrt(16)`
• Powers: `2**3` or `2^3`

**Examples:**
• "Calculate 15% tip on RM 45" → Try: `45 * 0.15`
• "What's 2.5 * 8?" → Try: `2.5 * 8`
• "Square root of 64" → Try: `sqrt(64)`

Please check your expression and try again."""
    
# Initialize the controller
agent_controller = AgentController()

def get_agent_controller() -> AgentController:
    """Get the agent controller instance."""
    return agent_controller
