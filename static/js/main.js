document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Handle chat functionality
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');

    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const message = chatInput.value.trim();
            if (!message) return;
            
            const sessionId = this.getAttribute('data-session-id');
            
            // Disable input and show loading
            chatInput.disabled = true;
            chatInput.value = '';
            
            // Send message to server
            fetch('/user/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    'session_id': sessionId,
                    'message': message
                })
            })
            .then(response => response.json())
            .then(data => {
                // Add user message
                appendMessage(data.user_message.content, true);
                
                // Add AI message
                appendMessage(data.ai_message.content, false);
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Re-enable input
                chatInput.disabled = false;
                chatInput.focus();
            })
            .catch(error => {
                console.error('Error:', error);
                appendMessage('Error sending message. Please try again.', false);
                chatInput.disabled = false;
            });
        });
    }

    // Function to append a message to the chat
    function appendMessage(content, isUser) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${isUser ? 'user-message' : 'ai-message'}`;
        messageDiv.textContent = content;
        chatMessages.appendChild(messageDiv);
    }

    // Initialize file upload preview
    const fileInput = document.getElementById('file-input');
    const fileLabel = document.getElementById('file-label');
    
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                fileLabel.textContent = this.files[0].name;
            } else {
                fileLabel.textContent = 'Choose file';
            }
        });
    }

    // Handle assessment timer if exists
    const assessmentTimer = document.getElementById('assessment-timer');
    if (assessmentTimer) {
        let timeLeft = 300; // 5 minutes
        
        const timerInterval = setInterval(function() {
            timeLeft--;
            
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            
            assessmentTimer.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                document.getElementById('assessment-form').submit();
            }
        }, 1000);
    }
});