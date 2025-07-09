import uuid
from backend.chatbot.enhanced_minimal_agent import EnhancedMinimalAgent

def print_test_result(description, result):
    print(f"{description}: {result}")

def run_basic_tests():
    agent = EnhancedMinimalAgent()
    session_id = str(uuid.uuid4())

    # Product queries
    queries = [
        ("Show me all products", "product_search"),
        ("What is the cheapest tumbler?", "product_search"),
        ("Do you have ceramic mugs?", "product_search"),
        ("Show me drinkware", "product_search"),
    ]
    for q, expected_intent in queries:
        plan = agent.parse_intent_and_plan_action(q, session_id)
        print_test_result(f"Query: '{q}' | Intent", plan['intent'])
        print_test_result(f"Query: '{q}' | Confidence", plan['confidence'])
        if plan['intent'] == 'product_search':
            products = agent.find_matching_products(q, session_id=session_id)
            print_test_result(f"Query: '{q}' | Products found", [p['name'] for p in products])

    # Outlet queries
    queries = [
        ("Where are your outlets?", "outlet_search"),
        ("Show me outlets in KLCC", "outlet_search"),
        ("Which outlets have WiFi?", "outlet_search"),
    ]
    for q, expected_intent in queries:
        plan = agent.parse_intent_and_plan_action(q, session_id)
        print_test_result(f"Query: '{q}' | Intent", plan['intent'])
        print_test_result(f"Query: '{q}' | Confidence", plan['confidence'])
        if plan['intent'] == 'outlet_search':
            outlets = agent.find_matching_outlets(q, session_id=session_id)
            print_test_result(f"Query: '{q}' | Outlets found", [o['name'] for o in outlets])

    # Calculator queries
    queries = [
        ("What is 2 + 2?", "calculation"),
        ("20% discount on RM100", "calculation"),
        ("Total for 3 × RM39", "calculation"),
    ]
    for q, expected_intent in queries:
        plan = agent.parse_intent_and_plan_action(q, session_id)
        print_test_result(f"Query: '{q}' | Intent", plan['intent'])
        print_test_result(f"Query: '{q}' | Confidence", plan['confidence'])
        if plan['intent'] == 'calculation':
            try:
                result = agent.handle_advanced_calculation(q)
                print_test_result(f"Query: '{q}' | Calculation result", result)
            except Exception as e:
                print_test_result(f"Query: '{q}' | Calculation error", str(e))

if __name__ == "__main__":
    run_basic_tests()
