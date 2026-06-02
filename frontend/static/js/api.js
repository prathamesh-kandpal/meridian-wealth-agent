/**
 * Global API Client Utility Layer for Meridian Agent Node
 */
const API = {
    // Authenticate Agent Sessions
    async login(username, password) {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);

        const response = await fetch('/api/login', {
            method: 'POST',
            body: formData
        });
        return response;
    },

    // Query the Agent Executor Engine
    async sendChatMessage(message, clientId = null) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                client_id: clientId,
                message: message
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned error status: ${response.status}`);
        }
        return await response.json();
    }
};