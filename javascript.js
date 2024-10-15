document.addEventListener('DOMContentLoaded', () => {
    const chatDisplay = document.getElementById('chat-display');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const fileUpload = document.getElementById('file-upload');
    const uploadButton = document.getElementById('upload-button');
    const uploadStatus = document.getElementById('upload-status');

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    uploadButton.addEventListener('click', uploadFile);

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            displayMessage('You', message);
            userInput.value = '';

            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => response.json())
            .then(data => {
                displayMessage('Bot', data.response, true);
            })
            .catch(error => {
                console.error('Error:', error);
                displayMessage('Bot', 'Sorry, I encountered an error.');
            });
        }
    }

    function displayMessage(sender, message, isMarkdown = false) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        
        const senderElement = document.createElement('strong');
        senderElement.textContent = `${sender}: `;
        messageElement.appendChild(senderElement);

        const contentElement = document.createElement('span');
        if (isMarkdown && typeof marked !== 'undefined') {
            contentElement.innerHTML = marked.parse(message);
        } else {
            contentElement.textContent = message;
        }
        messageElement.appendChild(contentElement);

        chatDisplay.appendChild(messageElement);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }

    function uploadFile() {
        const file = fileUpload.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('file', file);

            uploadStatus.textContent = 'Uploading...';

            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                uploadStatus.textContent = data.message;
            })
            .catch(error => {
                console.error('Error:', error);
                uploadStatus.textContent = 'Error uploading file';
            });
        } else {
            uploadStatus.textContent = 'Please select a file';
        }
    }
});
