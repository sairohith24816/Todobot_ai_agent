// TodoBot Application JavaScript
class TodoBot {
    constructor() {
        this.currentUser = null;
        this.users = [];
        this.initializeElements();
        this.attachEventListeners();
        this.loadUsers();
    }

    initializeElements() {
        this.userSelect = document.getElementById('userSelect');
        this.addUserBtn = document.getElementById('addUserBtn');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.addUserModal = document.getElementById('addUserModal');
        this.userNameInput = document.getElementById('userNameInput');
        this.createUserBtn = document.getElementById('createUserBtn');
        this.cancelBtn = document.getElementById('cancelBtn');
        this.closeModalBtn = document.getElementById('closeModalBtn');
        this.notification = document.getElementById('notification');
        this.notificationText = document.getElementById('notificationText');
    }

    attachEventListeners() {
        // User selection
        this.userSelect.addEventListener('change', (e) => this.onUserChange(e));
        
        // Add user modal
        this.addUserBtn.addEventListener('click', () => this.showAddUserModal());
        this.closeModalBtn.addEventListener('click', () => this.hideAddUserModal());
        this.cancelBtn.addEventListener('click', () => this.hideAddUserModal());
        this.createUserBtn.addEventListener('click', () => this.createUser());
        
        // Message input
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Modal backdrop click
        this.addUserModal.addEventListener('click', (e) => {
            if (e.target === this.addUserModal) {
                this.hideAddUserModal();
            }
        });
        
        // Enter key in user name input
        this.userNameInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.createUser();
            }
        });
    }

    async loadUsers() {
        try {
            const response = await fetch('/api/users');
            if (response.ok) {
                this.users = await response.json();
                this.updateUserSelect();
            }
        } catch (error) {
            this.showNotification('Error loading users', 'error');
        }
    }

    updateUserSelect() {
        this.userSelect.innerHTML = '<option value="">Select User</option>';
        this.users.forEach(user => {
            const option = document.createElement('option');
            option.value = user.id;
            option.textContent = user.name;
            this.userSelect.appendChild(option);
        });
    }

    async onUserChange(e) {
        const userId = e.target.value;
        if (userId) {
            const user = this.users.find(u => u.id == userId);
            if (user) {
                this.currentUser = user;
                this.enableChat();
                await this.loadConversationHistory();
                this.showNotification(`Selected user: ${user.name}`);
            }
        } else {
            this.currentUser = null;
            this.disableChat();
            this.clearMessages();
            this.addWelcomeMessage();
        }
    }

    enableChat() {
        this.messageInput.disabled = false;
        this.sendBtn.disabled = false;
        this.messageInput.placeholder = 'Type your message...';
    }

    disableChat() {
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
        this.messageInput.placeholder = 'Select a user to start chatting';
    }

    showAddUserModal() {
        this.addUserModal.classList.remove('hidden');
        this.addUserModal.classList.add('flex');
        this.addUserModal.firstElementChild.classList.add('modal-fade-in');
        this.userNameInput.focus();
    }

    hideAddUserModal() {
        this.addUserModal.classList.add('hidden');
        this.addUserModal.classList.remove('flex');
        this.userNameInput.value = '';
    }

    async createUser() {
        const name = this.userNameInput.value.trim();
        if (!name) {
            this.showNotification('Please enter a user name', 'warning');
            return;
        }

        try {
            const response = await fetch('/api/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name: name })
            });

            if (response.ok) {
                this.showNotification(`User '${name}' added successfully`);
                this.hideAddUserModal();
                await this.loadUsers();
            } else {
                const error = await response.json();
                this.showNotification(error.detail || 'Error creating user', 'error');
            }
        } catch (error) {
            this.showNotification('Error creating user', 'error');
        }
    }

    async loadConversationHistory() {
        if (!this.currentUser) return;

        try {
            const response = await fetch(`/api/users/${this.currentUser.id}/conversations`);
            if (response.ok) {
                const conversations = await response.json();
                this.clearMessages();
                conversations.forEach(conv => {
                    const isBot = conv.role === 'assistant';
                    this.addMessage(isBot ? 'TodoBot' : this.currentUser.name, conv.content, isBot);
                });
                this.scrollToBottom();
            }
        } catch (error) {
            this.showNotification('Error loading conversation history', 'error');
        }
    }

    clearMessages() {
        this.messagesContainer.innerHTML = '';
    }

    addWelcomeMessage() {
        this.addMessage('TodoBot', 'Welcome! Please select a user to start chatting.', true);
    }

    addMessage(sender, content, isBot = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'flex items-start space-x-3 message-fade-in';
        
        const avatar = document.createElement('div');
        avatar.className = 'flex-shrink-0';
        
        const avatarIcon = document.createElement('div');
        avatarIcon.className = `w-8 h-8 rounded-full flex items-center justify-center text-white text-sm ${
            isBot ? 'bg-blue-500' : 'bg-gray-500'
        }`;
        avatarIcon.innerHTML = isBot ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        avatar.appendChild(avatarIcon);
        
        const messageContent = document.createElement('div');
        messageContent.className = 'flex-1';
        
        const messageBubble = document.createElement('div');
        messageBubble.className = `rounded-lg p-3 max-w-md ${
            isBot ? 'bg-gray-100 text-gray-800' : 'bg-blue-500 text-white ml-auto'
        }`;
        
        // Format message content (preserve line breaks)
        const formattedContent = content.replace(/\n/g, '<br>');
        messageBubble.innerHTML = `<p>${formattedContent}</p>`;
        
        const senderName = document.createElement('p');
        senderName.className = 'text-xs text-gray-500 mt-1';
        senderName.textContent = sender;
        
        messageContent.appendChild(messageBubble);
        messageContent.appendChild(senderName);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }

    addTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'flex items-start space-x-3 message-fade-in';
        typingDiv.id = 'typing-indicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'flex-shrink-0';
        
        const avatarIcon = document.createElement('div');
        avatarIcon.className = 'w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm';
        avatarIcon.innerHTML = '<i class="fas fa-robot"></i>';
        
        avatar.appendChild(avatarIcon);
        
        const messageContent = document.createElement('div');
        messageContent.className = 'flex-1';
        
        const messageBubble = document.createElement('div');
        messageBubble.className = 'bg-gray-100 rounded-lg p-3 max-w-md';
        messageBubble.innerHTML = '<p class="text-gray-600">Thinking<span class="typing-indicator"></span></p>';
        
        const senderName = document.createElement('p');
        senderName.className = 'text-xs text-gray-500 mt-1';
        senderName.textContent = 'TodoBot';
        
        messageContent.appendChild(messageBubble);
        messageContent.appendChild(senderName);
        
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(messageContent);
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async sendMessage() {
        if (!this.currentUser) {
            this.showNotification('Please select a user first', 'warning');
            return;
        }

        const message = this.messageInput.value.trim();
        if (!message) return;

        // Add user message
        this.addMessage(this.currentUser.name, message, false);
        
        // Clear input
        this.messageInput.value = '';
        
        // Show typing indicator
        this.addTypingIndicator();
        
        try {
            const response = await fetch(`/api/users/${this.currentUser.id}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.currentUser.id,
                    message: message
                })
            });

            this.removeTypingIndicator();

            if (response.ok) {
                const data = await response.json();
                this.addMessage('TodoBot', data.response, true);
            } else {
                this.addMessage('TodoBot', 'Sorry, I encountered an error processing your request.', true);
            }
        } catch (error) {
            this.removeTypingIndicator();
            this.addMessage('TodoBot', 'Connection error. Please try again.', true);
            this.showNotification('Connection error', 'error');
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    showNotification(message, type = 'info') {
        this.notificationText.textContent = message;
        
        // Set notification style based on type
        const notificationClasses = {
            info: 'bg-blue-500',
            success: 'bg-green-500',
            warning: 'bg-yellow-500',
            error: 'bg-red-500'
        };
        
        this.notification.className = `fixed top-4 right-4 text-white px-6 py-3 rounded-lg shadow-lg transform transition-transform duration-300 z-50 ${notificationClasses[type] || notificationClasses.info}`;
        
        // Show notification
        this.notification.classList.add('notification-slide-in');
        
        // Hide after 3 seconds
        setTimeout(() => {
            this.notification.classList.remove('notification-slide-in');
            this.notification.classList.add('notification-slide-out');
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TodoBot();
});
