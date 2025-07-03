import re
import math
import operator
from typing import Union, Dict, Any, Tuple
import sympy as sp
from sympy import sympify, SympifyError
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SafeCalculator:
    """Safe calculator tool for mathematical expressions and time calculations."""
    
    def __init__(self):
        self.time_calc = TimeCalculator()
        
        # Allowed operators and functions
        self.allowed_operators = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '//': operator.floordiv,
            '%': operator.mod,
            '**': operator.pow,
            '^': operator.pow,  # Alternative power operator
        }
        
        # Allowed mathematical functions
        self.allowed_functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max,
            'sum': sum,
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'exp': math.exp,
            'pi': math.pi,
            'e': math.e,
            'ceil': math.ceil,
            'floor': math.floor,
            'factorial': math.factorial,
        }
        
        # Dangerous patterns to reject
        self.dangerous_patterns = [
            r'__.*__',  # Dunder methods
            r'import\s+',
            r'exec\s*\(',
            r'eval\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
            r'compile\s*\(',
            r'globals\s*\(',
            r'locals\s*\(',
            r'vars\s*\(',
            r'dir\s*\(',
            r'getattr\s*\(',
            r'setattr\s*\(',
            r'delattr\s*\(',
            r'hasattr\s*\(',
        ]
    
    def is_safe_expression(self, expression: str) -> bool:
        """Check if the expression is safe to evaluate."""
        expression_lower = expression.lower()
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, expression_lower):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False
        
        # Check for only allowed characters
        allowed_chars = set('0123456789+-*/().,^% abcdefghijklmnopqrstuvwxyz')
        if not set(expression_lower).issubset(allowed_chars):
            # Remove common punctuation and check again
            cleaned = re.sub(r"['\"`]", '', expression_lower)
            if not set(cleaned).issubset(allowed_chars):
                logger.warning("Expression contains disallowed characters")
                return False
        
        return True
    
    def normalize_expression(self, expression: str) -> str:
        """Normalize the mathematical expression."""
        # Remove whitespace and common punctuation
        expression = expression.strip()
        expression = re.sub(r"['\"`]", '', expression)  # Remove quotes/apostrophes
        
        # Replace common text representations
        replacements = {
            'plus': '+',
            'minus': '-',
            'times': '*',
            'multiply': '*',
            'divided by': '/',
            'divide': '/',
            'power': '**',
            'squared': '**2',
            'cubed': '**3',
            'x': '*',  # Common multiplication symbol
            '×': '*',
            '÷': '/',
            '^': '**',  # Convert caret to power
        }
        
        for text, symbol in replacements.items():
            expression = expression.replace(text, symbol)
        
        # Handle implicit multiplication (e.g., "2(3+4)" -> "2*(3+4)")
        # First, protect function calls by temporarily replacing them
        function_pattern = r'\b(abs|round|min|max|sum|sqrt|sin|cos|tan|log|log10|exp|ceil|floor|factorial)\s*\('
        functions = re.findall(function_pattern, expression)
        temp_expression = re.sub(function_pattern, r'FUNC\1FUNC(', expression)
        
        # Now apply implicit multiplication
        temp_expression = re.sub(r'(\d)\s*\(', r'\1*(', temp_expression)
        temp_expression = re.sub(r'\)\s*(\d)', r')*\1', temp_expression)
        
        # Restore function calls
        expression = re.sub(r'FUNC(\w+)FUNC\(', r'\1(', temp_expression)
        
        # Handle percentage
        expression = re.sub(r'(\d+(?:\.\d+)?)\s*%', r'(\1/100)', expression)
        
        return expression
    
    def calculate_with_sympy(self, expression: str) -> Dict[str, Any]:
        """Calculate using SymPy for safer evaluation."""
        try:
            # Parse the expression with proper error handling
            expr = sympify(expression, strict=True)
            
            # Evaluate numerically
            result = float(expr.evalf())
            
            return {
                'result': result,
                'is_valid': True,
                'error_message': None,
                'method': 'sympy'
            }
            
        except (SympifyError, ValueError, TypeError, ZeroDivisionError, SyntaxError) as e:
            return {
                'result': None,
                'is_valid': False,
                'error_message': f"Invalid mathematical expression: {str(e)}. Please check your expression and try again.",
                'method': 'sympy'
            }
        except Exception as e:
            return {
                'result': None,
                'is_valid': False,
                'error_message': f"Unexpected error: {str(e)}",
                'method': 'sympy'
            }
    
    def calculate_basic(self, expression: str) -> Dict[str, Any]:
        """Calculate using basic eval with restricted namespace."""
        try:
            # Create safe namespace
            safe_dict = {
                "__builtins__": {},
                **self.allowed_functions
            }
            
            # Evaluate the expression
            result = eval(expression, safe_dict, {})
            
            # Ensure result is a number
            if isinstance(result, (int, float, complex)):
                if isinstance(result, complex):
                    if result.imag == 0:
                        result = result.real
                    else:
                        return {
                            'result': None,
                            'is_valid': False,
                            'error_message': "Complex numbers are not supported",
                            'method': 'basic'
                        }
                
                return {
                    'result': float(result),
                    'is_valid': True,
                    'error_message': None,
                    'method': 'basic'
                }
            else:
                return {
                    'result': None,
                    'is_valid': False,
                    'error_message': "Result is not a number",
                    'method': 'basic'
                }
                
        except ZeroDivisionError:
            return {
                'result': None,
                'is_valid': False,
                'error_message': "Division by zero is not allowed",
                'method': 'basic'
            }
        except (NameError, SyntaxError, TypeError, ValueError) as e:
            return {
                'result': None,
                'is_valid': False,
                'error_message': f"Invalid expression: {str(e)}",
                'method': 'basic'
            }
        except Exception as e:
            return {
                'result': None,
                'is_valid': False,
                'error_message': f"Calculation error: {str(e)}",
                'method': 'basic'
            }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """Main calculation method with safety checks."""
        original_expression = expression
        
        try:
            # Check if this is a time calculation
            if expression.startswith("TIME_CALC:"):
                return self._handle_time_calculation(expression, original_expression)
            
            # Normalize the expression
            expression = self.normalize_expression(expression)
            
            # Safety check
            if not self.is_safe_expression(expression):
                return {
                    'result': None,
                    'is_valid': False,
                    'error_message': "Expression contains unsafe elements",
                    'original_expression': original_expression,
                    'normalized_expression': expression
                }
            
            # Try SymPy first (safer)
            result = self.calculate_with_sympy(expression)
            
            # If SymPy fails, try basic eval as fallback
            if not result['is_valid']:
                result = self.calculate_basic(expression)
            
            # Add expression information
            result['original_expression'] = original_expression
            result['normalized_expression'] = expression
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error in calculate: {e}")
            return {
                'result': None,
                'is_valid': False,
                'error_message': f"Unexpected error: {str(e)}",
                'original_expression': original_expression,
                'normalized_expression': expression if 'expression' in locals() else original_expression
            }
    
    def parse_calculation_intent(self, text: str) -> Union[str, None]:
        """Extract mathematical expression from natural language."""
        # Remove common words
        original_text = text
        text = text.lower().strip()
        
        # Handle time-based calculations first
        time_result = self._parse_time_calculations(text, original_text)
        if time_result:
            return time_result
        
        # Handle specific calculation patterns
        
        # 1. Unit cost calculations: "3 mugs at RM25 each"
        unit_cost_pattern = r'(\d+(?:\.\d+)?)\s+(?:mugs?|cups?|items?|things?)\s+at\s+rm\s*(\d+(?:\.\d+)?)\s*(?:each)?'
        unit_match = re.search(unit_cost_pattern, text)
        if unit_match:
            quantity, unit_price = unit_match.groups()
            return f"{quantity} * {unit_price}"
        
        # 2. Split money: "Split RM120 among 4 people" OR "Divide RM80 between 5 friends"
        split_patterns = [
            r'split\s+rm\s*(\d+(?:\.\d+)?)\s+(?:among|between)\s+(\d+)\s+people?',
            r'divide\s+rm\s*(\d+(?:\.\d+)?)\s+(?:among|between)\s+(\d+)\s+(?:people|friends?)',
        ]
        for pattern in split_patterns:
            split_match = re.search(pattern, text)
            if split_match:
                amount, people = split_match.groups()
                return f"{amount} / {people}"
        
        # 3. Average calculations: "What's the average of 8, 10, 12, 9, 11?"
        if 'average' in text:
            # Try to extract comma-separated numbers after "average of"
            numbers_pattern = r'average\s+of\s+([\d\s,.\-+]+)'
            avg_match = re.search(numbers_pattern, text)
            if avg_match:
                numbers_text = avg_match.group(1)
                # Extract all numbers from the matched text only
                numbers = re.findall(r'\d+(?:\.\d+)?', numbers_text)
                if len(numbers) >= 2:
                    numbers_str = ' + '.join(numbers)
                    return f"({numbers_str}) / {len(numbers)}"
            
            # Alternative pattern: "average price of X drinks: RM8, RM10..." 
            alt_pattern = r'average\s+price\s+of\s+\d+\s+\w+:\s*((?:rm\s*\d+(?:\.\d+)?,?\s*)+)'
            alt_match = re.search(alt_pattern, text)
            if alt_match:
                prices_text = alt_match.group(1)
                numbers = re.findall(r'\d+(?:\.\d+)?', prices_text)
                if len(numbers) >= 2:
                    numbers_str = ' + '.join(numbers)
                    return f"({numbers_str}) / {len(numbers)}"
        
        # 4. Percentage calculations
        percent_patterns = [
            r'(\d+(?:\.\d+)?)\s*percent\s+of\s+(?:rm\s*)?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)%\s+of\s+(?:rm\s*)?(\d+(?:\.\d+)?)',
            r'whats?\s+(\d+(?:\.\d+)?)%\s+of\s+(?:rm\s*)?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*%\s*(?:tip|tax)\s+on\s+(?:rm\s*)?(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*percent\s+(?:tip|tax)\s+on\s+(?:rm\s*)?(\d+(?:\.\d+)?)',
            r'add\s+(\d+(?:\.\d+)?)%\s+(?:tax\s+)?to\s+rm\s*(\d+(?:\.\d+)?)',
        ]
        
        for pattern in percent_patterns:
            match = re.search(pattern, text)
            if match:
                percent, amount = match.groups()
                if 'add' in text and 'tax' in text:
                    # Add tax: amount + (amount * percent/100)
                    return f"{amount} + ({amount} * {percent}/100)"
                else:
                    # Regular percentage calculation
                    return f"({percent}/100) * {amount}"
        
        
        # 5. Tax calculations: "What's the total with 6% SST on RM43?" - MOVED UP to prevent conflict with simple %
        tax_patterns = [
            r'total\s+with\s+(\d+(?:\.\d+)?)%\s+(?:sst|tax|gst)\s+on\s+rm\s*(\d+(?:\.\d+)?)',
            r'whats?\s+the\s+total\s+with\s+(\d+(?:\.\d+)?)%\s+(?:sst|tax|gst)\s+on\s+rm\s*(\d+(?:\.\d+)?)',
            r'add\s+(\d+(?:\.\d+)?)%\s+(?:sst|tax|gst)\s+to\s+rm\s*(\d+(?:\.\d+)?)',
            r'rm\s*(\d+(?:\.\d+)?)\s+(?:plus|with)\s+(\d+(?:\.\d+)?)%\s+(?:sst|tax|gst)',
            r'(\d+(?:\.\d+)?)%\s+(?:sst|tax|gst)\s+on\s+rm\s*(\d+(?:\.\d+)?)',
        ]
        for pattern in tax_patterns:
            tax_match = re.search(pattern, text)
            if tax_match:
                if 'rm' in pattern and pattern.index('rm') < pattern.index('%'):
                    # Pattern where amount comes before percentage
                    amount, tax_rate = tax_match.groups()
                else:
                    # Pattern where percentage comes before amount
                    tax_rate, amount = tax_match.groups()
                return f"{amount} + ({amount} * {tax_rate}/100)"
        
        # 6. Simple percentage like "15%" or "20% of RM100"
        simple_percent = re.search(r'(\d+(?:\.\d+)?)%', text)
        if simple_percent and 'of' not in text and 'sst' not in text and 'tax' not in text and 'gst' not in text:
            percent = simple_percent.group(1)
            return f"{percent}/100"
        
        # 7. Purchase/Shopping calculations: "If I buy 3 drinks for RM6.90 each"
        purchase_patterns = [
            r'if\s+i\s+buy\s+(\d+(?:\.\d+)?)\s+(?:drinks?|items?|cups?|things?)\s+for\s+rm\s*(\d+(?:\.\d+)?)\s+each',
            r'buy\s+(\d+(?:\.\d+)?)\s+(?:drinks?|items?|cups?|things?)\s+(?:for|at)\s+rm\s*(\d+(?:\.\d+)?)\s+each',
            r'(\d+(?:\.\d+)?)\s+(?:drinks?|items?|cups?|things?)\s+(?:for|at)\s+rm\s*(\d+(?:\.\d+)?)\s+each',
            r'(\d+(?:\.\d+)?)\s+(?:drinks?|items?|cups?|mugs?|tumblers?)\s+(?:cost|price|costing)\s+rm\s*(\d+(?:\.\d+)?)\s+each',
        ]
        for pattern in purchase_patterns:
            purchase_match = re.search(pattern, text)
            if purchase_match:
                quantity, unit_price = purchase_match.groups()
                return f"{quantity} * {unit_price}"
        
        # 8. Reverse calculations: "How many drinks can I buy with RM50 if each costs RM7.50?"
        reverse_calc_patterns = [
            r'how\s+many\s+(?:drinks?|items?|cups?|things?)\s+.*buy.*with\s+rm\s*(\d+(?:\.\d+)?).*each\s+costs?\s+rm\s*(\d+(?:\.\d+)?)',
            r'how\s+many\s+(?:drinks?|items?|cups?|things?)\s+.*rm\s*(\d+(?:\.\d+)?).*if\s+each\s+costs?\s+rm\s*(\d+(?:\.\d+)?)',
            r'how\s+many\s+(?:cups?|drinks?|items?)\s+for\s+rm\s*(\d+(?:\.\d+)?).*rm\s*(\d+(?:\.\d+)?)\s+each',
        ]
        for pattern in reverse_calc_patterns:
            reverse_match = re.search(pattern, text)
            if reverse_match:
                total_money, unit_price = reverse_match.groups()
                return f"{total_money} / {unit_price}"
        
        # 9. Spending calculations: "If I spend RM30 a day for 7 days"
        spending_patterns = [
            r'if\s+i\s+spend\s+rm\s*(\d+(?:\.\d+)?)\s+(?:a\s+)?day\s+for\s+(\d+)\s+days?',
            r'spend\s+rm\s*(\d+(?:\.\d+)?)\s+(?:a\s+|per\s+)?day\s+for\s+(\d+)\s+days?',
            r'rm\s*(\d+(?:\.\d+)?)\s+(?:a\s+|per\s+)?day\s+for\s+(\d+)\s+days?',
            r'if\s+.*spend\s+rm\s*(\d+(?:\.\d+)?)\s+.*\s+(\d+)\s+days?',
        ]
        for pattern in spending_patterns:
            spending_match = re.search(pattern, text)
            if spending_match:
                daily_amount, days = spending_match.groups()
                return f"{daily_amount} * {days}"
        
        # 10. Work/Time calculations: "If I work 8 hours a day, how many hours in a week?"
        work_patterns = [
            r'if\s+i\s+work\s+(\d+(?:\.\d+)?)\s+hours?\s+(?:a\s+|per\s+)?day.*how\s+many\s+hours?.*week',
            r'work\s+(\d+(?:\.\d+)?)\s+hours?\s+(?:a\s+|per\s+)?day.*hours?.*week',
            r'(\d+(?:\.\d+)?)\s+hours?\s+(?:a\s+|per\s+)?day.*how\s+many.*week',
        ]
        for pattern in work_patterns:
            work_match = re.search(pattern, text)
            if work_match:
                daily_hours = work_match.group(1)
                return f"{daily_hours} * 7"  # 7 days in a week
        
        # 11. Monthly/daily consumption: "If I drink 2 cups a day, how many cups in a month?"
        consumption_patterns = [
            r'if\s+i\s+drink\s+(\d+(?:\.\d+)?)\s+(?:cups?|drinks?)\s+(?:a\s+|per\s+)?day.*(?:how\s+many|total).*month',
            r'drink\s+(\d+(?:\.\d+)?)\s+(?:cups?|drinks?)\s+(?:a\s+|per\s+)?day.*(?:how\s+many|total).*month',
            r'(\d+(?:\.\d+)?)\s+(?:cups?|drinks?)\s+(?:a\s+|per\s+)?day.*(?:how\s+many|total).*month',
        ]
        for pattern in consumption_patterns:
            consumption_match = re.search(pattern, text)
            if consumption_match:
                daily_amount = consumption_match.group(1)
                return f"{daily_amount} * 30"  # Assuming 30 days in a month
        monthly_pattern = r'(\d+(?:\.\d+)?)\s+(?:cups?|drinks?)\s+(?:a\s+|per\s+)?day.*(?:how\s+many|total).*month'
        monthly_match = re.search(monthly_pattern, text)
        if monthly_match:
            daily_amount = monthly_match.group(1)
            return f"{daily_amount} * 30"  # Assuming 30 days in a month
        
        # 12. Convert natural language to mathematical operators
        replacements = [
            (r'\btimes\b', '*'),
            (r'\bmultiplied\s+by\b', '*'),
            (r'\bdivided\s+by\b', '/'),
            (r'\bplus\b', '+'),
            (r'\bminus\b', '-'),
            (r'\bto\s+the\s+power\s+of\b', '**'),
            (r'\bsquare\s+root\s+of\s+(\d+(?:\.\d+)?)', r'sqrt(\1)'),
            (r'\bsqrt\s+of\s+(\d+(?:\.\d+)?)', r'sqrt(\1)'),
            (r'\broot\s+of\s+(\d+(?:\.\d+)?)', r'sqrt(\1)'),
            (r'\bsquare\s+root\s+(\d+(?:\.\d+)?)', r'sqrt(\1)'),
            (r'\bsqrt\s+(\d+(?:\.\d+)?)', r'sqrt(\1)'),
            (r'\broot\s+(\d+(?:\.\d+)?)', r'sqrt(\1)'),
            (r'√(\d+(?:\.\d+)?)', r'sqrt(\1)'),  # Unicode square root symbol
            (r'\b(\d+)\s+factorial\b', r'factorial(\1)'),
            (r'\bfactorial\s+of\s+(\d+)', r'factorial(\1)'),
            (r'×', '*'),
            (r'÷', '/'),
            (r'\bx\b', '*'),  # Common multiplication symbol
        ]
        
        for pattern, replacement in replacements:
            text = re.sub(pattern, replacement, text)
        
        # 8. Remove currency symbols and common words
        text = re.sub(r'\b(?:rm|dollar|dollars|\$)\s*', '', text)
        text = re.sub(r'\b(?:calculate|compute|solve|find|what\s+is|equals?|the\s+result\s+of|the|what|whats)\b', '', text)
        
        # Remove possessive forms and contractions
        text = re.sub(r"'s\b", '', text)
        text = re.sub(r"'re\b", '', text)
        text = re.sub(r"'ll\b", '', text)
        
        # Clean up extra whitespace after word removal
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 9. Clean up and extract expressions
        calc_patterns = [
            r'(.+?)\s*[=?]\s*$',  # Expression ending with = or ?
            r'(.+)',  # Fallback: treat entire cleaned text as expression
        ]
        
        for pattern in calc_patterns:
            match = re.search(pattern, text.strip())
            if match:
                potential_expr = match.group(1).strip()
                
                # Clean up extra whitespace
                potential_expr = re.sub(r'\s+', ' ', potential_expr).strip()
                
                # Check if it looks like a mathematical expression
                if self._looks_like_math(potential_expr):
                    return potential_expr
        
        return None
    
    def _looks_like_math(self, text: str) -> bool:
        """Check if text looks like a mathematical expression."""
        # Must contain at least one number
        has_number = bool(re.search(r'\d', text))
        if not has_number:
            return False
        
        # Check for mathematical operators or functions
        has_operator = bool(re.search(r'[+\-*/^%=()]', text))
        has_function = any(func in text.lower() for func in self.allowed_functions.keys())
        
        # Check for word-based operators
        has_word_math = bool(re.search(r'\b(times|plus|minus|divided|multiplied|power|percent|sqrt|root)\b', text.lower()))
        
        # Must have some mathematical element
        if not (has_operator or has_function or has_word_math):
            return False
        
        # Should not contain too many non-math words
        words = re.findall(r'\b\w+\b', text)
        math_words = {
            'plus', 'minus', 'times', 'divide', 'divided', 'multiplied', 'power', 'sqrt', 'root',
            'sin', 'cos', 'tan', 'log', 'exp', 'abs', 'round', 'min', 'max', 'sum',
            'by', 'of', 'the', 'and', 'or', 'percent', 'pi', 'e'
        }
        
        # Count non-mathematical words
        non_math_words = []
        for word in words:
            word_lower = word.lower()
            # Skip if it's a math word, number, or very short
            if (word_lower not in math_words and 
                not re.match(r'^\d+$', word) and 
                len(word) > 2):
                non_math_words.append(word)
        
        # Allow up to 2 non-math words for natural language
        return len(non_math_words) <= 2

    def _parse_time_calculations(self, text: str, original_text: str) -> Union[str, None]:
        """Parse time-based calculations and return a special result format."""
        
        # 1. Enhanced wait time calculation: "If the outlet opens at 9 and I arrive at 8:30, how long must I wait?"
        wait_patterns = [
            r'(?:if\s+)?(?:the\s+)?(?:outlet\s+)?opens?\s+at\s+(\d{1,2}(?::\d{2})?(?:\s*(?:am|pm))?)\s+and\s+.*arrive\s+at\s+(\d{1,2}:\d{2}(?:\s*(?:am|pm))?)',
            r'arrive\s+at\s+(\d{1,2}:\d{2}(?:\s*(?:am|pm))?)\s+.*opens?\s+at\s+(\d{1,2}(?::\d{2})?(?:\s*(?:am|pm))?)',
            r'outlet\s+opens?\s+(\d{1,2}(?::\d{2})?(?:\s*(?:am|pm))?)\s+.*i\s+arrive\s+(\d{1,2}:\d{2}(?:\s*(?:am|pm))?)',
        ]
        
        for pattern in wait_patterns:
            wait_match = re.search(pattern, text)
            if wait_match:
                if 'arrive' in pattern and pattern.index('arrive') < pattern.index('opens'):
                    # Arrive time comes first
                    arrive_time_str, open_time_str = wait_match.groups()
                else:
                    # Open time comes first
                    open_time_str, arrive_time_str = wait_match.groups()
                
                open_time = self.time_calc.parse_time(open_time_str)
                arrive_time = self.time_calc.parse_time(arrive_time_str)
                
                if open_time and arrive_time:
                    open_minutes = self.time_calc.time_to_minutes(*open_time)
                    arrive_minutes = self.time_calc.time_to_minutes(*arrive_time)
                    
                    if open_minutes > arrive_minutes:
                        wait_minutes = open_minutes - arrive_minutes
                        return f"TIME_CALC:WAIT:{wait_minutes}"
                    else:
                        return f"TIME_CALC:WAIT:0"  # Already open or past opening
        
        # 2. Weekly calculation: "If I work 8 hours a day, how many hours is that in a week?"
        weekly_pattern = r'(?:if\s+)?.*work\s+(\d+(?:\.\d+)?)\s+hours?\s+(?:a\s+|per\s+)?day.*(?:how\s+many\s+hours?\s+.*week|week)'
        weekly_match = re.search(weekly_pattern, text)
        if weekly_match:
            daily_hours = float(weekly_match.group(1))
            return f"{daily_hours} * 7"
        
        # 3. Add time: "Add 45 minutes to 2:15PM"
        add_time_pattern = r'add\s+(\d+)\s+minutes?\s+to\s+(\d{1,2}:\d{2}\s*(?:am|pm)?)'
        add_match = re.search(add_time_pattern, text)
        if add_match:
            minutes_to_add = int(add_match.group(1))
            base_time_str = add_match.group(2)
            
            base_time = self.time_calc.parse_time(base_time_str)
            if base_time:
                base_minutes = self.time_calc.time_to_minutes(*base_time)
                new_minutes = base_minutes + minutes_to_add
                return f"TIME_CALC:ADD_TIME:{new_minutes}"
        
        # 4. Unit conversions: "How many minutes in 2.5 hours?"
        unit_conversion_patterns = [
            (r'how\s+many\s+minutes?\s+in\s+(\d+(?:\.\d+)?)\s+hours?', 'HOURS_TO_MINUTES'),
            (r'convert\s+(\d+)\s+minutes?\s+to\s+hours?', 'MINUTES_TO_HOURS'),
            (r'(\d+)\s+minutes?\s+in\s+hours?', 'MINUTES_TO_HOURS'),
        ]
        
        for pattern, conversion_type in unit_conversion_patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                if conversion_type == 'HOURS_TO_MINUTES':
                    return f"{value} * 60"
                elif conversion_type == 'MINUTES_TO_HOURS':
                    return f"{value} / 60"
        
        # 5. Time addition with current time: "If I wait 30 minutes and the current time is 2:15, what time will it be?"
        current_time_pattern = r'(?:if\s+)?.*wait\s+(\d+)\s+minutes?.*current\s+time\s+is\s+(\d{1,2}:\d{2}(?:\s*(?:am|pm))?)'
        current_match = re.search(current_time_pattern, text)
        if current_match:
            wait_minutes = int(current_match.group(1))
            current_time_str = current_match.group(2)
            
            current_time = self.time_calc.parse_time(current_time_str)
            if current_time:
                current_minutes = self.time_calc.time_to_minutes(*current_time)
                new_minutes = current_minutes + wait_minutes
                return f"TIME_CALC:ADD_TIME:{new_minutes}"
        
        return None

    def _handle_time_calculation(self, expression: str, original_expression: str) -> Dict[str, Any]:
        """Handle time-based calculations."""
        try:
            parts = expression.split(":")
            calc_type = parts[1]
            
            if calc_type == "WAIT":
                wait_minutes = int(parts[2])
                if wait_minutes == 0:
                    result_text = "The outlet is already open! No need to wait."
                else:
                    duration = self.time_calc.minutes_to_duration(wait_minutes)
                    result_text = f"You need to wait {duration}."
                
                return {
                    'result': result_text,
                    'is_valid': True,
                    'error_message': None,
                    'original_expression': original_expression,
                    'normalized_expression': expression,
                    'is_time_calculation': True
                }
            
            elif calc_type == "ADD_TIME":
                total_minutes = int(parts[2])
                new_time = self.time_calc.minutes_to_time(total_minutes)
                result_text = f"The time will be {new_time}."
                
                return {
                    'result': result_text,
                    'is_valid': True,
                    'error_message': None,
                    'original_expression': original_expression,
                    'normalized_expression': expression,
                    'is_time_calculation': True
                }
            
            else:
                return {
                    'result': None,
                    'is_valid': False,
                    'error_message': "Unknown time calculation type",
                    'original_expression': original_expression,
                    'normalized_expression': expression
                }
                
        except (IndexError, ValueError) as e:
            return {
                'result': None,
                'is_valid': False,
                'error_message': f"Error processing time calculation: {str(e)}",
                'original_expression': original_expression,
                'normalized_expression': expression
            }
        
class TimeCalculator:
    """Helper class for time-based calculations."""
    
    @staticmethod
    def parse_time(time_str: str) -> Union[Tuple[int, int], None]:
        """Parse time string into (hours, minutes). Returns None if invalid."""
        time_str = time_str.strip().lower()
        
        # Handle various time formats
        patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',  # 2:15PM, 8:30, etc.
            r'(\d{1,2})\s*(am|pm)',           # 9am, 2pm, etc.
            r'(\d{1,2})\.(\d{2})',            # 8.30 format
            r'^(\d{1,2})$',                   # Just a number like "9"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, time_str)
            if match:
                if len(match.groups()) == 3:  # HH:MM AM/PM format
                    hours, minutes, period = match.groups()
                    hours, minutes = int(hours), int(minutes)
                    
                    if period:
                        if period == 'pm' and hours != 12:
                            hours += 12
                        elif period == 'am' and hours == 12:
                            hours = 0
                    
                    return (hours, minutes)
                elif len(match.groups()) == 2:
                    if ':' in time_str or '.' in time_str:  # HH:MM or HH.MM
                        hours, minutes = int(match.group(1)), int(match.group(2))
                        return (hours, minutes)
                    else:  # H AM/PM format
                        hours, period = int(match.group(1)), match.group(2)
                        if period == 'pm' and hours != 12:
                            hours += 12
                        elif period == 'am' and hours == 12:
                            hours = 0
                        return (hours, 0)
                elif len(match.groups()) == 1:  # Just a number
                    hours = int(match.group(1))
                    # Assume business hours context - if single digit or small number, likely AM
                    if hours <= 12:
                        return (hours, 0)
                    else:
                        return None  # Invalid hour
        
        return None
    
    @staticmethod
    def time_to_minutes(hours: int, minutes: int) -> int:
        """Convert time to total minutes."""
        return hours * 60 + minutes
    
    @staticmethod
    def minutes_to_time(total_minutes: int) -> str:
        """Convert total minutes back to time format."""
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        # Handle 24-hour rollover
        hours = hours % 24
        
        # Format with AM/PM
        if hours == 0:
            return f"12:{minutes:02d} AM"
        elif hours < 12:
            return f"{hours}:{minutes:02d} AM"
        elif hours == 12:
            return f"12:{minutes:02d} PM"
        else:
            return f"{hours-12}:{minutes:02d} PM"
    
    @staticmethod
    def minutes_to_duration(minutes: int) -> str:
        """Convert minutes to human-readable duration."""
        if minutes < 60:
            return f"{minutes} minutes"
        else:
            hours = minutes // 60
            remaining_minutes = minutes % 60
            if remaining_minutes == 0:
                return f"{hours} hour{'s' if hours != 1 else ''}"
            else:
                return f"{hours} hour{'s' if hours != 1 else ''} and {remaining_minutes} minutes"

# Initialize calculator
calculator = SafeCalculator()

def get_calculator() -> SafeCalculator:
    """Get the calculator instance."""
    return calculator
