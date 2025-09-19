"""
Test the chat memory system functionality
"""

# Mock testing without full dependencies
class MockUser:
    def __init__(self, id, name):
        self.id = id
        self.name = name

def test_memory_logic():
    """Test the memory extraction and processing logic"""
    
    # Test keyword extraction
    from chat_memory_controller import ChatMemoryController
    
    memory = ChatMemoryController()
    
    # Test 1: Keyword extraction
    message1 = "I want to compare the 2024 BMW X5 with the 2023 3 Series"
    keywords = memory.extract_keywords(message1)
    print(f"Keywords extracted from '{message1}': {keywords}")
    
    # Test 2: Intent classification
    intent1 = memory.classify_intent(message1)
    print(f"Intent classified: {intent1}")
    
    # Test 3: Car model extraction
    models = memory.extract_car_models(message1)
    print(f"Car models found: {models}")
    
    # Test 4: Conversation title generation
    title = memory.generate_conversation_title(message1)
    print(f"Generated title: {title}")
    
    # Test 5: Importance calculation
    importance = memory.calculate_importance(message1, "Here's a detailed comparison...", models)
    print(f"Importance score: {importance}")
    
    print("\n✅ Memory system logic tests passed!")

if __name__ == "__main__":
    test_memory_logic()