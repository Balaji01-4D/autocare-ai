"""
Detailed Memory Test - Check actual responses
"""
import requests
import json

def test_detailed_memory():
    print("🔍 Detailed Memory Test\n")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: Ask about 3 Series
        print("📝 Test 1: Asking about 2025 3 Series details")
        response1 = requests.post(
            f"{base_url}/api/chatbot",
            json={
                "message": "give me details about 2025 3 series",
                "selected_cars": [],
                "session_id": None
            }
        )
        
        data1 = response1.json()
        print(f"Response 1:\n{data1['response']}\n")
        print(f"Context used: {data1.get('context_used', 'None')}\n")
        
        session_id = data1.get('session_id')
        print(f"Session ID: {session_id}\n")
        
        # Test 2: Ask about mileage (should remember 3 Series context)
        print("📝 Test 2: Follow-up about mileage")
        response2 = requests.post(
            f"{base_url}/api/chatbot",
            json={
                "message": "what is the mileage",
                "selected_cars": [],
                "session_id": session_id
            }
        )
        
        data2 = response2.json()
        print(f"Response 2:\n{data2['response']}\n")
        print(f"Context used: {data2.get('context_used', 'None')}\n")
        
        # Check for memory indicators
        response2_text = data2['response'].lower()
        memory_indicators = ['3 series', 'm3', 'sedan', 'previous', 'mentioned', 'discussed']
        
        found_indicators = [indicator for indicator in memory_indicators if indicator in response2_text]
        
        if found_indicators:
            print(f"🧠 ✅ Memory Evidence Found: {', '.join(found_indicators)}")
        else:
            print("🧠 ❌ No clear memory evidence found")
            
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_detailed_memory()