import OpenAI from "openai";

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

const response = await openai.chat.completions.create({
    model: "gpt-4o",
    messages: [],
    temperature: 1,
    max_tokens: 2048,
    top_p: 1,
    frequency_penalty: 0,
    presence_penalty: 0,
    response_format: {
    "type": "text"},
});

function addMessage(message, isUser = false) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Example usage:
document.getElementById('send-button').addEventListener('click', function() {
    const userInput = document.getElementById('user-input');
    const userMessage = userInput.value.trim();
    
    if (userMessage) {
        addMessage(userMessage, true);
        userInput.value = '';
        
        // Here you would typically send the user's message to your chatbot backend
        // and get a response. For this example, we'll just echo the user's message.
        setTimeout(() => {
            const botResponse = `You said: "${userMessage}". How can I help you with your exercise routine?`;
            addMessage(botResponse);
        }, 1000);
    }
});
