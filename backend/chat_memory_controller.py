from sqlmodel import Session, select, text
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import uuid
import re
from collections import Counter

from controllers import engine
from models import User, ChatConversation, ChatMessage, ChatMemoryEntry
from schemas import ConversationSummary, ChatHistoryResponse, MessageWithContext, ConversationDetailResponse


class ChatMemoryController:
    """
    Handles chat memory storage, retrieval, and RAG functionality
    """
    
    def __init__(self):
        self.session_timeout_hours = 24  # New session if inactive for 24 hours
    
    def get_or_create_conversation(self, user_id: int, session_id: Optional[str] = None) -> ChatConversation:
        """
        Get existing conversation or create new one
        """
        with Session(engine) as session:
            if session_id:
                # Try to find existing conversation
                statement = select(ChatConversation).where(
                    ChatConversation.user_id == user_id,
                    ChatConversation.session_id == session_id
                )
                conversation = session.exec(statement).first()
                if conversation:
                    return conversation
            
            # Check for recent active conversation (within timeout)
            cutoff_time = datetime.utcnow() - timedelta(hours=self.session_timeout_hours)
            statement = select(ChatConversation).where(
                ChatConversation.user_id == user_id,
                ChatConversation.updated_at > cutoff_time
            ).order_by(ChatConversation.updated_at.desc())
            
            recent_conversation = session.exec(statement).first()
            if recent_conversation:
                return recent_conversation
            
            # Create new conversation
            new_session_id = session_id or str(uuid.uuid4())
            conversation = ChatConversation(
                user_id=user_id,
                session_id=new_session_id,
                title=None  # Will be generated later
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation
    
    def store_message(
        self,
        user_id: int,
        user_message: str,
        bot_response: Optional[str] = None,
        selected_cars: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        context_used: Optional[str] = None
    ) -> ChatMessage:
        """
        Store a chat message and create memory entries
        """
        with Session(engine) as session:
            # Get or create conversation
            conversation = self.get_or_create_conversation(user_id, session_id)
            
            # Store user message
            message = ChatMessage(
                conversation_id=conversation.id,
                user_id=user_id,
                message=user_message,
                response=bot_response,
                sender="user",
                selected_cars=json.dumps(selected_cars) if selected_cars else None,
                context_used=context_used
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            
            # Update conversation timestamp and title if needed
            conversation.updated_at = datetime.utcnow()
            if not conversation.title:
                conversation.title = self.generate_conversation_title(user_message)
            session.add(conversation)
            session.commit()
            
            # Create memory entry for RAG
            self.create_memory_entry(session, message, user_message, bot_response)
            
            # Return conversation ID to avoid session issues
            return conversation.id
    
    def get_relevant_context(
        self,
        user_id: int,
        current_message: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context using simple keyword matching and recency
        """
        with Session(engine) as session:
            # Extract keywords from current message
            keywords = self.extract_keywords(current_message)
            
            # Get recent conversations for context
            recent_cutoff = datetime.utcnow() - timedelta(days=30)  # Last 30 days
            
            # Build query for relevant messages
            query = select(ChatMemoryEntry).where(
                ChatMemoryEntry.user_id == user_id,
                ChatMemoryEntry.created_at > recent_cutoff
            )
            
            memory_entries = session.exec(query).all()
            
            # Score entries based on keyword overlap and importance
            scored_entries = []
            for entry in memory_entries:
                score = self.calculate_relevance_score(entry, keywords, current_message)
                if score > 0.1:  # Minimum relevance threshold
                    scored_entries.append((entry, score))
            
            # Sort by score and return top results
            scored_entries.sort(key=lambda x: x[1], reverse=True)
            
            # Get full message details
            context = []
            for entry, score in scored_entries[:limit]:
                message_query = select(ChatMessage).where(ChatMessage.id == entry.message_id)
                message = session.exec(message_query).first()
                if message:
                    context.append({
                        "message": message.message,
                        "response": message.response,
                        "cars_mentioned": json.loads(entry.car_models_mentioned) if entry.car_models_mentioned else [],
                        "intent": entry.intent,
                        "relevance_score": score,
                        "timestamp": message.created_at
                    })
            
            return context
    
    def get_conversation_history(self, user_id: int, limit: int = 20) -> ChatHistoryResponse:
        """
        Get user's conversation history
        """
        with Session(engine) as session:
            # Get conversations with message count
            conversations_query = text("""
                SELECT c.id, c.session_id, c.title, c.updated_at, c.created_at,
                       COUNT(m.id) as message_count,
                       MAX(m.message) as last_message
                FROM chatconversation c
                LEFT JOIN chatmessage m ON c.id = m.conversation_id
                WHERE c.user_id = :user_id
                GROUP BY c.id, c.session_id, c.title, c.updated_at, c.created_at
                ORDER BY c.updated_at DESC
                LIMIT :limit
            """)
            
            result = session.execute(conversations_query, {"user_id": user_id, "limit": limit})
            rows = result.all()
            
            conversations = []
            for row in rows:
                conversations.append(ConversationSummary(
                    id=row.id,
                    session_id=row.session_id,
                    title=row.title or "Untitled Conversation",
                    message_count=row.message_count or 0,
                    last_activity=row.updated_at,
                    preview=row.last_message[:50] + "..." if row.last_message and len(row.last_message) > 50 else row.last_message
                ))
            
            total_count_query = select(ChatConversation).where(ChatConversation.user_id == user_id)
            total_count = len(session.exec(total_count_query).all())
            
            return ChatHistoryResponse(
                conversations=conversations,
                total_conversations=total_count
            )
    
    def get_conversation_detail(self, user_id: int, conversation_id: int) -> ConversationDetailResponse:
        """
        Get detailed conversation with all messages
        """
        with Session(engine) as session:
            # Get conversation
            conv_query = select(ChatConversation).where(
                ChatConversation.id == conversation_id,
                ChatConversation.user_id == user_id
            )
            conversation = session.exec(conv_query).first()
            if not conversation:
                raise ValueError("Conversation not found")
            
            # Get all messages
            messages_query = select(ChatMessage).where(
                ChatMessage.conversation_id == conversation_id
            ).order_by(ChatMessage.created_at)
            messages = session.exec(messages_query).all()
            
            # Convert to response format
            message_list = []
            for msg in messages:
                message_list.append(MessageWithContext(
                    id=msg.id,
                    message=msg.message,
                    response=msg.response,
                    sender=msg.sender,
                    selected_cars=json.loads(msg.selected_cars) if msg.selected_cars else None,
                    created_at=msg.created_at,
                    context_used=msg.context_used
                ))
            
            conversation_summary = ConversationSummary(
                id=conversation.id,
                session_id=conversation.session_id,
                title=conversation.title or "Untitled Conversation",
                message_count=len(message_list),
                last_activity=conversation.updated_at,
                preview=message_list[-1].message[:50] + "..." if message_list else None
            )
            
            return ConversationDetailResponse(
                conversation=conversation_summary,
                messages=message_list
            )
    
    def create_memory_entry(
        self,
        session: Session,
        message: ChatMessage,
        user_message: str,
        bot_response: Optional[str]
    ):
        """
        Create preprocessed memory entry for RAG
        """
        # Extract relevant information
        keywords = self.extract_keywords(user_message)
        intent = self.classify_intent(user_message)
        car_models = self.extract_car_models(user_message + " " + (bot_response or ""))
        
        # Create content for RAG
        content = f"{user_message}"
        if bot_response:
            content += f" | {bot_response}"
        
        # Calculate importance score
        importance = self.calculate_importance(user_message, bot_response, car_models)
        
        memory_entry = ChatMemoryEntry(
            user_id=message.user_id,
            conversation_id=message.conversation_id,
            message_id=message.id,
            content=content,
            keywords=json.dumps(keywords),
            intent=intent,
            car_models_mentioned=json.dumps(car_models),
            importance_score=importance
        )
        
        session.add(memory_entry)
        session.commit()
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text
        """
        # Simple keyword extraction
        text = text.lower()
        
        # BMW-specific terms
        bmw_terms = ['bmw', '3 series', '5 series', 'x5', 'x3', 'm3', 'm5', 'z4', '7 series']
        car_terms = ['car', 'vehicle', 'engine', 'horsepower', 'transmission', 'fuel', 'price', 'compare', 'specs']
        
        keywords = []
        for term in bmw_terms + car_terms:
            if term in text:
                keywords.append(term)
        
        # Extract years (2000-2030)
        years = re.findall(r'\b(20[0-2][0-9]|203[0])\b', text)
        keywords.extend(years)
        
        return list(set(keywords))
    
    def classify_intent(self, message: str) -> str:
        """
        Classify user intent
        """
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
    
    def extract_car_models(self, text: str) -> List[str]:
        """
        Extract BMW car models mentioned in text
        """
        text = text.lower()
        models = []
        
        # Common BMW models
        bmw_models = ['3 series', '5 series', 'x5', 'x3', 'x1', 'x7', 'm3', 'm5', 'z4', 'i3', 'i8', '7 series']
        
        for model in bmw_models:
            if model in text:
                models.append(model)
        
        return list(set(models))
    
    def calculate_importance(self, user_message: str, bot_response: Optional[str], car_models: List[str]) -> float:
        """
        Calculate importance score for memory entry
        """
        score = 0.5  # Base score
        
        # More important if multiple cars mentioned
        if len(car_models) > 1:
            score += 0.2
        
        # More important if it's a comparison
        if 'compare' in user_message.lower():
            score += 0.2
        
        # More important if response is long (detailed)
        if bot_response and len(bot_response) > 200:
            score += 0.1
        
        return min(score, 1.0)
    
    def calculate_relevance_score(self, entry: ChatMemoryEntry, current_keywords: List[str], current_message: str) -> float:
        """
        Calculate relevance score for memory entry
        """
        score = 0.0
        
        # Keyword overlap
        if entry.keywords:
            entry_keywords = json.loads(entry.keywords)
            common_keywords = set(current_keywords) & set(entry_keywords)
            if entry_keywords:
                keyword_score = len(common_keywords) / len(entry_keywords)
                score += keyword_score * 0.5
        
        # Intent matching
        current_intent = self.classify_intent(current_message)
        if entry.intent == current_intent:
            score += 0.3
        
        # Car model matching
        current_models = self.extract_car_models(current_message)
        if entry.car_models_mentioned and current_models:
            entry_models = json.loads(entry.car_models_mentioned)
            common_models = set(current_models) & set(entry_models)
            if entry_models:
                model_score = len(common_models) / len(entry_models)
                score += model_score * 0.4
        
        # Recency bonus (more recent = slightly higher score)
        days_old = (datetime.utcnow() - entry.created_at).days
        recency_score = max(0, (30 - days_old) / 30 * 0.2)
        score += recency_score
        
        # Apply importance multiplier
        score *= entry.importance_score
        
        return score
    
    def generate_conversation_title(self, first_message: str) -> str:
        """
        Generate a title for conversation based on first message
        """
        # Extract key terms
        car_models = self.extract_car_models(first_message)
        intent = self.classify_intent(first_message)
        
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


# Global instance
chat_memory = ChatMemoryController()