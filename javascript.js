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
                displayMessage('Bot', data.response);
            })
            .catch(error => {
                console.error('Error:', error);
                displayMessage('Bot', 'Sorry, I encountered an error.');
            });
        }
    }

    function displayMessage(sender, message) {
        const messageElement = document.createElement('p');
        messageElement.textContent = `${sender}: ${message}`;
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
