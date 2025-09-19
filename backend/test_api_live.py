"""
Test Current API Memory Functionality
"""
import requests
import json

def test_memory_api():
    print("🧪 Testing Memory API Functionality\n")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test 1: First message about 3 Series
        print("📝 Test 1: Asking about 2025 3 Series")
        response1 = requests.post(
            f"{base_url}/api/chatbot",
            json={
                "message": "give the details about 2025 3 series",
                "selected_cars": [],
                "session_id": None
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"✅ Response received: {data1['response'][:100]}...")
            session_id = data1.get('session_id')
            print(f"📋 Session ID: {session_id}")
        else:
            print(f"❌ Request failed: {response1.status_code}")
            print(f"Response: {response1.text}")
            return False
        
        # Test 2: Follow-up question about mileage
        print("\n📝 Test 2: Follow-up question about mileage")
        response2 = requests.post(
            f"{base_url}/api/chatbot",
            json={
                "message": "what is the mileage",
                "selected_cars": [],
                "session_id": session_id
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Response received: {data2['response'][:100]}...")
            
            # Check if the response mentions 3 Series or shows memory
            response_text = data2['response'].lower()
            if "3 series" in response_text or "m3" in response_text:
                print("🧠 ✅ Memory working - Bot remembers previous context!")
            else:
                print("🧠 ❌ Memory not working - Bot doesn't remember previous context")
                print(f"🔍 Full response: {data2['response']}")
                
        else:
            print(f"❌ Request failed: {response2.status_code}")
            print(f"Response: {response2.text}")
            return False
        
        print(f"\n🎯 API Memory Test Complete")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    result = test_memory_api()
    if result:
        print("\n🚀 API tests completed!")
    else:
        print("\n⚠️  API tests failed - check server is running")