document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = window.API_BASE_URL || '';

    // UI Elements - Upload
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('pdfFile');
    const dropZone = document.getElementById('dropZone');
    const dropMsg = document.querySelector('.drop-msg');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadBtn = document.getElementById('uploadBtn');
    
    // UI Elements - Context
    const activeDocSection = document.getElementById('activeDocSection');
    const activeDocTitle = document.getElementById('activeDocTitle');
    const activeDocMeta = document.getElementById('activeDocMeta');
    const viewAnalysisBtn = document.getElementById('viewAnalysisBtn');
    const sessionBadge = document.getElementById('sessionBadge');
    
    // UI Elements - Chat
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const chatMessages = document.getElementById('chatMessages');
    
    // UI Elements - Modal
    const modal = document.getElementById('analysisModal');
    const closeBtn = document.querySelector('.close-btn');
    const analysisContent = document.getElementById('analysisContent');

    // State
    let currentDocumentId = null;
    let currentSessionId = null;
    let currentAnalysis = null;

    // --- Drag and Drop File Handlers ---
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.add('dragover'), false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => dropZone.classList.remove('dragover'), false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length) {
            fileInput.files = files;
            updateFileName(files);
        }
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length) {
            updateFileName(this.files);
        }
    });

    function updateFileName(files) {
        if (files.length === 1) {
            dropMsg.textContent = files[0].name;
        } else {
            dropMsg.textContent = `${files.length} files selected`;
        }
        dropMsg.style.color = 'var(--primary)';
    }

    // --- Upload PDF Logic ---

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!fileInput.files.length) return;
        
        const formData = new FormData(uploadForm);
        
        // UI Loading State
        uploadBtn.disabled = true;
        uploadBtn.textContent = 'Uploading...';
        uploadStatus.className = 'status-msg';
        uploadStatus.textContent = '';

        try {
            // 1. Upload the PDF
            const response = await fetch(`${API_BASE_URL}/api/v1/upload_pdf`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (!response.ok) throw new Error(result.error || 'Upload failed');
            
            uploadStatus.textContent = 'Upload successful! Analyzing paper...';
            uploadStatus.className = 'status-msg success';
            uploadBtn.textContent = 'Analyzing...';
            
            currentDocumentId = result.document_id;
            
            // 2. Trigger Analysis
            await fetchAnalysis(currentDocumentId, result.filename, formData.get('subject'), formData.get('year'));

        } catch (error) {
            console.error('Error:', error);
            uploadStatus.textContent = `Error: ${error.message}`;
            uploadStatus.className = 'status-msg error';
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload & Analyze';
        }
    });

    async function fetchAnalysis(docId, filename, subject, year) {
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/analyze/${docId}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            if (!response.ok) throw new Error(result.error || 'Analysis failed');
            
            currentAnalysis = result.analysis;
            
            // Update UI
            uploadBtn.textContent = 'Upload & Analyze';
            uploadBtn.disabled = false;
            
            // Show new Context Document Side panel
            activeDocSection.style.display = 'block';
            activeDocTitle.textContent = `${subject} (${year})`;
            activeDocMeta.textContent = filename;
            
            // Enable Chat
            chatInput.disabled = false;
            sendBtn.disabled = false;
            sessionBadge.textContent = `Context: ${subject}`;
            sessionBadge.style.color = 'var(--primary)';
            sessionBadge.style.borderColor = 'var(--primary)';
            
            // Add system message
            appendSystemMessage(`Analysis complete for **${subject}**. You can view the insights or ask me questions about it!`);
            
        } catch (error) {
            console.error('Analysis Error:', error);
            uploadStatus.textContent = `Analysis failed: ${error.message}`;
            uploadStatus.className = 'status-msg error';
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload & Analyze';
        }
    }

    // --- Chat Logic ---

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = chatInput.value.trim();
        if (!text || !currentDocumentId) return;
        
        // Push user message to UI
        appendMessage('User', text);
        chatInput.value = '';
        chatInput.disabled = true;
        sendBtn.disabled = true;
        
        // Show typing indicator
        const typingId = appendTypingIndicator();

        try {
            const payload = {
                document_id: currentDocumentId,
                query: text
            };
            if (currentSessionId) {
                payload.session_id = currentSessionId;
            }

            const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await response.json();
            
            // Remove typing indicator
            document.getElementById(typingId).remove();
            
            if (!response.ok) throw new Error(result.error || 'Failed to get response');
            
            currentSessionId = result.session_id; // save session for history
            
            // Push AI message to UI
            appendMessage('AI', result.response);

        } catch (error) {
            console.error('Chat Error:', error);
            document.getElementById(typingId).remove();
            appendSystemMessage(`Error: ${error.message}. Please try again.`);
        } finally {
            chatInput.disabled = false;
            sendBtn.disabled = false;
            chatInput.focus();
        }
    });

    // --- UI Helpers ---

    function appendMessage(senderType, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${senderType === 'User' ? 'user' : 'ai'}`;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'avatar';
        avatarDiv.textContent = senderType === 'User' ? '👤' : '🤖';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Use marked to parse markdown if it's the AI responding
        if (senderType === 'AI') {
            contentDiv.innerHTML = marked.parse(text);
        } else {
            contentDiv.textContent = text;
        }
        
        msgDiv.appendChild(avatarDiv);
        msgDiv.appendChild(contentDiv);
        
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendSystemMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ai`;
        msgDiv.innerHTML = `
            <div class="avatar">⚡</div>
            <div class="message-content">${marked.parse(text)}</div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function appendTypingIndicator() {
        const id = 'typing-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message ai';
        msgDiv.id = id;
        msgDiv.innerHTML = `
            <div class="avatar">🤖</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    // --- Modal Logic ---

    viewAnalysisBtn.addEventListener('click', () => {
        if (!currentAnalysis) return;
        
        modal.classList.add('show');
        
        // Format the structured JSON to HTML
        let html = '';
        
        if (currentAnalysis.exam_pattern) {
            html += `
            <div class="analysis-section">
                <h3>📋 Exam Pattern</h3>
                <p style="color:var(--text-muted); line-height:1.5">${currentAnalysis.exam_pattern}</p>
            </div>`;
        }
        
        if (currentAnalysis.frequent_topics && currentAnalysis.frequent_topics.length > 0) {
            html += `
            <div class="analysis-section">
                <h3>🎯 Frequent Topics</h3>
                <ul>
                    ${currentAnalysis.frequent_topics.map(t => `<li>${t}</li>`).join('')}
                </ul>
            </div>`;
        }
        
        if (currentAnalysis.repeated_questions && currentAnalysis.repeated_questions.length > 0) {
            html += `
            <div class="analysis-section">
                <h3>🔄 Repeated Core Concepts</h3>
                <ul>
                    ${currentAnalysis.repeated_questions.map(q => `<li>${q}</li>`).join('')}
                </ul>
            </div>`;
        }

        analysisContent.innerHTML = html;
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('show');
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('show');
        }
    });

});
