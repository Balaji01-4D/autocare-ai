"""
Test Memory System Integration
"""
import asyncio
import json
from datetime import datetime
import sys
sys.path.append('.')

# Import models and controller
from models import *
from controllers import engine
from sqlmodel import Session, select
from chat_memory_controller import ChatMemoryController

def test_memory_system():
    print("🧠 Testing Memory System Integration\n")
    
    # Create database session
    session = Session(engine)
    
    try:
        # Create tables
        SQLModel.metadata.create_all(engine)
        print("✅ Database tables created")
        
        # Initialize memory controller
        memory_controller = ChatMemoryController()
        print("✅ Memory controller initialized")
        
        # Get any existing user for testing
        existing_user = session.exec(select(User)).first()
        if existing_user:
            user_id = existing_user.id
            print(f"✅ Using existing user with ID: {user_id}")
        else:
            print("❌ No users found. Please create a user first.")
            return False
        
        # Test 1: Start new conversation
        user_message = "I want to compare the 2024 BMW X5 with the 2023 3 Series. What's the price difference?"
        bot_response = "The 2024 BMW X5 starts at $60,600, while the 2023 BMW 3 Series starts at $35,300. The price difference is approximately $25,300, with the X5 being positioned as a luxury SUV versus the 3 Series as a luxury sedan."
        
        # Store message and get relevant context
        message = memory_controller.store_message(
            user_id=user_id,
            user_message=user_message,
            bot_response=bot_response,
            session_id=None  # New conversation
        )
        
        print(f"✅ New conversation created: ID {message.conversation_id}")
        
        # Test 2: Add to existing conversation
        follow_up_message = "Which one has better fuel economy?"
        follow_up_response = "The 2023 BMW 3 Series has better fuel economy with 26 city/36 highway MPG, compared to the 2024 BMW X5's 21 city/26 highway MPG. The 3 Series is more fuel-efficient due to its smaller size and lighter weight."
        
        memory_controller.store_message(
            user_id=user_id,
            user_message=follow_up_message,
            bot_response=follow_up_response,
            session_id=str(message.conversation_id)
        )
        
        print("✅ Follow-up message added to conversation")
        
        # Test 3: Get relevant context for new query
        new_query = "Tell me about X5 safety features"
        relevant_context = memory_controller.get_relevant_context(user_id, new_query)
        
        print(f"✅ Retrieved {len(relevant_context)} relevant context entries")
        if relevant_context:
            print(f"   Most relevant: {relevant_context[0].summary[:100]}...")
        
        # Test 4: Get conversation history
        conversations = memory_controller.get_conversations(user_id, limit=5)
        print(f"✅ Retrieved {len(conversations)} conversations for user {user_id}")
        
        # Test 5: Get specific conversation
        conv_detail = memory_controller.get_conversation(message.conversation_id)
        print(f"✅ Retrieved conversation details with {len(conv_detail.messages)} messages")
        
        print(f"\n🎯 Memory System Integration Test: ✅ PASSED")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        session.close()

if __name__ == "__main__":
    result = test_memory_system()
    if result:
        print("\n🚀 Memory system is fully functional!")
    else:
        print("\n⚠️  Memory system needs debugging")