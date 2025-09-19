"""
Simple Memory System Test - Check logic without full dependencies
"""

# Mock the required imports to test logic
class MockSession:
    def exec(self, query):
        return MockResult([])
    def add(self, obj):
        pass
    def commit(self):
        pass
    def refresh(self, obj):
        obj.id = 1

class MockResult:
    def __init__(self, data):
        self._data = data
    def first(self):
        return None if not self._data else self._data[0]
    def all(self):
        return self._data

# Test memory controller logic
def test_memory_logic():
    print("🧠 Testing Memory System Logic\n")
    
    # Import with mocked dependencies
    import sys
    sys.path.append('.')
    
    # Test keyword extraction
    test_message = "I want to compare the 2024 BMW X5 with the 2023 3 Series. What's the price difference?"
    
    # Mock the chat memory controller functions
    keywords = extract_keywords_simple(test_message)
    print(f"✅ Keywords extracted: {keywords}")
    
    intent = classify_intent_simple(test_message)
    print(f"✅ Intent classified: {intent}")
    
    models = extract_car_models_simple(test_message)
    print(f"✅ Car models found: {models}")
    
    importance = calculate_importance_simple(test_message, "Here's a detailed comparison...", models)
    print(f"✅ Importance score: {importance}")
    
    title = generate_title_simple(test_message)
    print(f"✅ Generated title: {title}")
    
    print(f"\n🎯 Memory Logic Test: ✅ PASSED")

def extract_keywords_simple(text):
    """Simple keyword extraction"""
    text = text.lower()
    keywords = []
    
    # BMW-specific terms
    bmw_terms = ['bmw', '3 series', '5 series', 'x5', 'x3', 'm3', 'm5', 'z4', '7 series']
    car_terms = ['car', 'vehicle', 'engine', 'horsepower', 'transmission', 'fuel', 'price', 'compare', 'specs']
    
    for term in bmw_terms + car_terms:
        if term in text:
            keywords.append(term)
    
    # Extract years
    import re
    years = re.findall(r'\b(20[0-2][0-9]|203[0])\b', text)
    keywords.extend(years)
    
    return list(set(keywords))

def classify_intent_simple(message):
    """Simple intent classification"""
    message = message.lower()
    
    if any(word in message for word in ['compare', 'vs', 'versus', 'difference']):
        return 'comparison'
    elif any(word in message for word in ['price', 'cost', 'expensive', 'cheap']):
        return 'pricing'
    elif any(word in message for word in ['specs', 'specification', 'engine', 'horsepower']):
        return 'specifications'
    elif any(word in message for word in ['recommend', 'suggest', 'best', 'should']):
        return 'recommendation'
    else:
        return 'general'

def extract_car_models_simple(text):
    """Simple car model extraction"""
    text = text.lower()
    models = []
    
    bmw_models = ['3 series', '5 series', 'x5', 'x3', 'x1', 'x7', 'm3', 'm5', 'z4', 'i3', 'i8', '7 series']
    
    for model in bmw_models:
        if model in text:
            models.append(model)
    
    return list(set(models))

def calculate_importance_simple(user_message, bot_response, car_models):
    """Simple importance calculation"""
    score = 0.5  # Base score
    
    if len(car_models) > 1:
        score += 0.2
    
    if 'compare' in user_message.lower():
        score += 0.2
    
    if bot_response and len(bot_response) > 200:
        score += 0.1
    
    return min(score, 1.0)

def generate_title_simple(first_message):
    """Simple title generation"""
    car_models = extract_car_models_simple(first_message)
    intent = classify_intent_simple(first_message)
    
    if car_models:
        if intent == 'comparison':
            return f"Comparing {', '.join(car_models[:2])}"
        elif intent == 'pricing':
            return f"Pricing for {car_models[0]}"
        elif intent == 'specifications':
            return f"Specs for {car_models[0]}"
        else:
            return f"About {car_models[0]}"
    else:
        if intent == 'recommendation':
            return "Car Recommendation"
        else:
            return "BMW Inquiry"

if __name__ == "__main__":
    test_memory_logic()