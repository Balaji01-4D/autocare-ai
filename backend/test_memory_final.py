"""
Simple Memory System Test - Verify functionality works
"""
from datetime import datetime
from models import *
from controllers import engine
from sqlmodel import Session, select
from chat_memory_controller import ChatMemoryController

def test_memory_basic():
    print("🧠 Testing Basic Memory System Functionality\n")
    
    try:
        # Create tables
        SQLModel.metadata.create_all(engine)
        print("✅ Database tables created")
        
        # Initialize memory controller
        memory_controller = ChatMemoryController()
        print("✅ Memory controller initialized")
        
        # Get any existing user
        with Session(engine) as session:
            user = session.exec(select(User)).first()
            if not user:
                print("❌ No users found. Please create a user first.")
                return False
            user_id = user.id
            print(f"✅ Using user ID: {user_id}")
        
        # Test message storage
        conv_id = memory_controller.store_message(
            user_id=user_id,
            user_message="I want to compare the 2024 BMW X5 with the 2023 3 Series",
            bot_response="The 2024 BMW X5 is a luxury SUV starting at $60,600, while the 2023 BMW 3 Series is a luxury sedan starting at $35,300."
        )
        print("✅ First message stored successfully")
        print(f"✅ Conversation ID: {conv_id}")
        
        # Add follow-up message
        conv_id2 = memory_controller.store_message(
            user_id=user_id,
            user_message="Which one has better fuel economy?",
            bot_response="The 3 Series has better fuel economy at 26/36 MPG vs X5's 21/26 MPG.",
            session_id=str(conv_id)
        )
        print("✅ Follow-up message stored successfully")
        
        # Test context retrieval
        context = memory_controller.get_relevant_context(user_id, "BMW X5 safety features")
        print(f"✅ Retrieved {len(context)} relevant context entries")
        
        # Test conversation retrieval
        conversations = memory_controller.get_conversation_history(user_id, limit=5)
        print(f"✅ Retrieved {len(conversations.conversations)} conversations")
        
        # Test conversation detail
        conv_detail = memory_controller.get_conversation_detail(user_id, conv_id)
        print(f"✅ Retrieved conversation with {len(conv_detail.messages)} messages")
        
        print(f"\n🎯 Memory System Test: ✅ PASSED")
        return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_memory_basic()
    if result:
        print("\n🚀 Memory system is working!")
    else:
        print("\n⚠️  Memory system has issues")