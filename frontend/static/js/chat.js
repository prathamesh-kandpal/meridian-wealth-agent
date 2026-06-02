document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const clientIdInput = document.getElementById('clientIdInput');
    const chatWindow = document.getElementById('chatWindow');
    const inspectorPanel = document.getElementById('inspectorPanel');
    const emptyInspectorMessage = document.getElementById('emptyInspectorMessage');

    // Auto-populate Client ID if passed from the dashboard URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('client_id') && clientIdInput) {
        clientIdInput.value = urlParams.get('client_id');
    }

    if (!chatForm) return; // Exit gracefully if not on the chat page view

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const messageText = userInput.value.trim();
        if (!messageText) return;

        const clientId = clientIdInput.value.trim() ? parseInt(clientIdInput.value.trim()) : null;

        // Render user message bubble
        appendMessage('user', messageText);
        userInput.value = '';

        if(emptyInspectorMessage) emptyInspectorMessage.style.display = 'none';
        appendInspectorLog('SYSTEM', `Initiating ReAct graph execution loop for prompt: "${messageText}"`);

        // Insert visual loader bubble
        const typingBubble = appendTypingIndicator();

        try {
            // Leverage external unified API client object from api.js
            const data = await API.sendChatMessage(messageText, clientId);

            typingBubble.remove();

            // Process intermediate runtime agent execution traces
            if (data.intermediate_steps && data.intermediate_steps.length > 0) {
                data.intermediate_steps.forEach((step, index) => {
                    const logHeader = `STEP ${index + 1}: Tool Usage [${step.tool}]`;
                    const details = `Thought Log:\n${step.log}\n\nArguments Applied:\n${step.tool_input}`;
                    appendInspectorLog('TOOL_CALL', details, logHeader);
                });
            } else {
                appendInspectorLog('INFO', 'Agent addressed query directly without external tool intervention.');
            }

            // Append final structured output
            appendMessage('agent', data.output);
            appendInspectorLog('SUCCESS', 'Execution sequence complete. Agent returned final answer block.');

        } catch (error) {
            if(typingBubble) typingBubble.remove();
            appendMessage('agent', `⚠️ Technical Error processing query: ${error.message}`);
            appendInspectorLog('ERROR', error.message, 'Agent Execution Interrupted');
        }
    });

    function appendMessage(sender, text) {
        const wrapper = document.createElement('div');
        wrapper.className = 'flex space-x-3 max-w-2xl' + (sender === 'user' ? ' ml-auto justify-end' : '');
        const isUser = sender === 'user';
        
        const avatarHtml = isUser 
            ? `<div class="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-bold text-slate-200 shrink-0 shadow order-2 ml-3">UX</div>`
            : `<div class="h-8 w-8 rounded-full bg-emerald-600 flex items-center justify-center text-xs font-bold text-white shrink-0 shadow mr-3">MW</div>`;

        const contentHtml = `
            <div class="${isUser ? 'bg-emerald-700 text-white rounded-br-none' : 'bg-slate-800 text-slate-200 rounded-tl-none'} rounded-2xl px-4 py-3 shadow-sm border border-slate-700/40 text-sm leading-relaxed whitespace-pre-wrap ${isUser ? 'order-1' : ''}">
                ${escapeHtml(text)}
            </div>
        `;
        
        wrapper.innerHTML = avatarHtml + contentHtml;
        chatWindow.appendChild(wrapper);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    function appendTypingIndicator() {
        const wrapper = document.createElement('div');
        wrapper.className = 'flex space-x-3 max-w-2xl';
        wrapper.innerHTML = `
            <div class="h-8 w-8 rounded-full bg-emerald-600 flex items-center justify-center text-xs font-bold text-white shrink-0 shadow mr-3">MW</div>
            <div class="bg-slate-800 text-slate-400 rounded-2xl rounded-tl-none px-4 py-3 border border-slate-700/40 text-sm flex items-center space-x-1">
                <span class="animate-bounce inline-block h-1.5 w-1.5 bg-slate-400 rounded-full"></span>
                <span class="animate-bounce inline-block h-1.5 w-1.5 bg-slate-400 rounded-full [animation-delay:0.2s]"></span>
                <span class="animate-bounce inline-block h-1.5 w-1.5 bg-slate-400 rounded-full [animation-delay:0.4s]"></span>
            </div>
        `;
        chatWindow.appendChild(wrapper);
        chatWindow.scrollTop = chatWindow.scrollHeight;
        return wrapper;
    }

    function appendInspectorLog(type, content, title = '') {
        if(emptyInspectorMessage) emptyInspectorMessage.style.display = 'none';
        const block = document.createElement('div');
        block.className = `p-3 rounded-lg border text-xs font-mono transition-all duration-200 shadow-sm mb-3 `;

        let badgeColor = 'bg-slate-800 text-slate-300 border-slate-700';
        if (type === 'SYSTEM') badgeColor = 'bg-blue-950 text-blue-400 border-blue-900/60';
        if (type === 'TOOL_CALL') badgeColor = 'bg-amber-950 text-amber-400 border-amber-900/60';
        if (type === 'SUCCESS') badgeColor = 'bg-emerald-950 text-emerald-400 border-emerald-900/60';
        if (type === 'ERROR') badgeColor = 'bg-rose-950 text-rose-400 border-rose-900/60';

        block.className += badgeColor;
        const headerHtml = title ? `<div class="font-bold border-b border-current/10 pb-1 mb-1.5 uppercase tracking-wide text-[11px]">${title}</div>` : '';
        block.innerHTML = `${headerHtml}<div class="whitespace-pre-wrap">${escapeHtml(content)}</div>`;
        
        inspectorPanel.appendChild(block);
        inspectorPanel.scrollTop = inspectorPanel.scrollHeight;
    }

    function escapeHtml(str) {
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }
});