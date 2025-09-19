from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever


model = OllamaLLM(model="llama3.2")

template = """
You are a friendly and knowledgeable car sales manager of BMW company and your name is Grace assisting customers with their car-related questions.
Use the following car dataset to provide accurate, detailed, and helpful information:
{data}

Respond to the customer questions below in a warm, conversational tone using **Markdown formatting** to make your response clear and well-structured:

**Formatting Guidelines:**
- Use **bold** for important features, model names, and key specifications
- Use *italic* for emphasis and descriptive language
- Create bullet points with - for lists of features or specifications  
- Use ## for section headings when organizing information
- Use tables when comparing multiple models or specifications
- Use > for important tips or recommendations
- Format prices, numbers, and technical specs clearly

Customer Question: {questions_asked}

Make your answers clear, concise, and incorporate relevant specs, features, and comparisons when applicable.
If appropriate, ask the customer if they want to know more details, see similar models, or schedule a test drive.
Keep the conversation engaging and encourage further interaction.
Always aim to provide value and assist the customer in making informed decisions about their car purchase.
"""

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model


def get_response(user_input):
    data = retriever.invoke(user_input)
    response = chain.invoke({"data":data, "questions_asked": user_input})
    return response


def get_response_with_memory(user_input, conversation_context=None, selected_cars=None, user_name="Customer"):
    """
    Enhanced response function that uses conversation history for context-aware responses
    """
    # Get base car data from vector store
    data = retriever.invoke(user_input)
    
    # Build enhanced template with memory context
    memory_template = """
You are Grace, a friendly and knowledgeable BMW sales manager. You maintain conversation continuity and remember previous interactions with customers.

Current car dataset:
{data}

Customer name: {customer_name}

Previous conversation context (if any):
{conversation_history}

Selected cars for this conversation:
{selected_cars_info}

Current customer question:
{questions_asked}

**Response Instructions:**
1. Use **Markdown formatting** to create clear, professional responses:
   - Use **bold** for BMW model names, important features, and key specifications
   - Use *italic* for emphasis and descriptive language
   - Create bullet points with - for feature lists and specifications
   - Use ## for section headings when organizing information
   - Use tables when comparing models or specifications
   - Use > for important tips, recommendations, or notes
   - Format prices as **$XX,XXX** and technical specs clearly

2. Reference previous conversations naturally when relevant (e.g., "As we discussed earlier...", "Building on what you mentioned...")
3. If the customer previously showed interest in specific models, acknowledge that
4. Use the customer's name appropriately in the conversation
5. Provide detailed, accurate information from the car dataset
6. If appropriate, reference or compare with previously discussed models
7. Keep your response conversational, warm, and helpful
8. Ask follow-up questions to continue the conversation
9. Always aim to assist the customer in making informed decisions

Remember: You're having an ongoing conversation, not starting fresh each time.
"""
    
    # Format conversation context
    context_str = ""
    if conversation_context:
        context_entries = []
        for ctx in conversation_context:
            cars_mentioned = ", ".join(ctx.get('cars_mentioned', [])) if ctx.get('cars_mentioned') else "None"
            context_entries.append(
                f"Previous interaction ({ctx.get('timestamp', 'Recent')}):\n"
                f"Customer: {ctx.get('message', '')}\n"
                f"Your response: {ctx.get('response', '')}\n"
                f"Cars discussed: {cars_mentioned}\n"
                f"Intent: {ctx.get('intent', 'general')}"
            )
        context_str = "\n\n".join(context_entries[-3:])  # Use last 3 interactions
    else:
        context_str = "No previous conversation history"
    
    # Format selected cars info
    cars_info = ""
    if selected_cars:
        car_details = []
        for car in selected_cars:
            car_details.append(f"- {car.model_year} {car.model_name} {car.trim_variant}")
        cars_info = "\n".join(car_details)
    else:
        cars_info = "No cars specifically selected for this conversation"
    
    # Create memory-enhanced prompt
    memory_prompt = ChatPromptTemplate.from_template(memory_template)
    memory_chain = memory_prompt | model
    
    # Generate response
    response = memory_chain.invoke({
        "data": data,
        "customer_name": user_name,
        "conversation_history": context_str,
        "selected_cars_info": cars_info,
        "questions_asked": user_input
    })
    
    return response


def get_response_with_car_specific_context(user_input, specific_car, conversation_context=None, user_name="Customer"):
    """
    Specialized response function for car-specific conversations with enhanced context
    Focuses entirely on the specific car model provided
    """
    # Get enhanced car data with focus on the specific model
    data = retriever.invoke(user_input)
    
    # Build car-specific template
    car_specific_template = """
You are Grace, a specialized BMW expert with deep knowledge about specific BMW models. You are currently in a focused conversation about a particular BMW model.

Current car dataset (general BMW knowledge):
{data}

Customer name: {customer_name}

FOCUSED BMW MODEL FOR THIS CONVERSATION:
Model: {specific_car_year} {specific_car_name} {specific_car_variant}
Body Type: {specific_car_body_type}
Price: {specific_car_price}
Engine: {specific_car_engine}

Previous conversation context about this specific model:
{conversation_history}

Current customer question about this BMW model:
{questions_asked}

**SPECIALIZED INSTRUCTIONS:**
1. **Use Rich Markdown Formatting** to showcase your expertise:
   - Use **bold** for the specific BMW model name: **{specific_car_year} {specific_car_name} {specific_car_variant}**
   - Create clear sections with ## headings (e.g., ## Key Features, ## Performance, ## Specifications)
   - Use bullet points (-) for feature lists and benefits
   - Use tables for technical specifications and comparisons
   - Use > for expert recommendations and insider tips
   - Format prices as **{specific_car_price}** and technical data clearly
   - Use *italic* for descriptive language and benefits

2. You are THE expert specifically on the **{specific_car_year} {specific_car_name} {specific_car_variant}**
3. Provide incredibly detailed and specific information about THIS model
4. Reference previous conversations about this specific model when relevant
5. Compare with other BMW models when appropriate, but always bring the focus back to this specific model
6. Use technical specifications, features, and benefits specific to this model
7. Discuss real-world experiences, ownership costs, and practical considerations for this model
8. If the customer asks about other models, acknowledge but redirect to how this specific model compares
9. Use the customer's name and maintain a personal, consultative approach
10. Always relate general BMW knowledge back to this specific model
11. Encourage test drives, detailed walkthroughs, or more specific questions about this model

Remember: You are THE expert on this specific BMW model and should demonstrate that expertise through well-formatted, comprehensive responses.
"""
    
    # Format conversation context
    context_str = ""
    if conversation_context:
        context_entries = []
        for ctx in conversation_context:
            context_entries.append(
                f"Previous interaction ({ctx.get('timestamp', 'Recent')}):\n"
                f"Customer: {ctx.get('message', '')}\n"
                f"Your response: {ctx.get('response', '')}"
            )
        context_str = "\n\n".join(context_entries[-5:])  # More context for specialized mode
    else:
        context_str = "This is the start of our focused conversation about this BMW model"
    
    # Create car-specific prompt
    car_prompt = ChatPromptTemplate.from_template(car_specific_template)
    car_chain = car_prompt | model
    
    # Generate specialized response
    response = car_chain.invoke({
        "data": data,
        "customer_name": user_name,
        "conversation_history": context_str,
        "questions_asked": user_input,
        "specific_car_year": getattr(specific_car, 'model_year', 'Unknown'),
        "specific_car_name": getattr(specific_car, 'model_name', 'Unknown'),
        "specific_car_variant": getattr(specific_car, 'trim_variant', 'Unknown'),
        "specific_car_body_type": getattr(specific_car, 'body_type', 'Unknown'),
        "specific_car_price": f"${getattr(specific_car, 'base_msrp_usd', 'TBD'):,}" if hasattr(specific_car, 'base_msrp_usd') and specific_car.base_msrp_usd else "Contact for pricing",
        "specific_car_engine": getattr(specific_car, 'engine_type', 'Premium engine')
    })
    
    return response


if __name__ == "__main__":
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chat. Goodbye!")
            break
        response = get_response(user_input)
        print("Car Sales Manager:", response)