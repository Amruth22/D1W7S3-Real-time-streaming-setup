class DocumentQAClient {
    constructor() {
        this.ws = null;
        this.currentServer = null;
        this.servers = [
            { host: 'localhost', port: 8080, priority: 1 },
            { host: 'localhost', port: 8081, priority: 2 }
        ];
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;
        
        this.initializeElements();
        this.setupEventListeners();
        this.connect();
    }
    
    initializeElements() {
        this.elements = {
            connectionStatus: document.getElementById('connectionStatus'),
            fileInput: document.getElementById('fileInput'),
            uploadBtn: document.getElementById('uploadBtn'),
            uploadProgress: document.getElementById('uploadProgress'),
            progressFill: document.getElementById('progressFill'),
            uploadStatus: document.getElementById('uploadStatus'),
            searchInput: document.getElementById('searchInput'),
            searchResults: document.getElementById('searchResults'),
            questionInput: document.getElementById('questionInput'),
            askBtn: document.getElementById('askBtn'),
            aiResponse: document.getElementById('aiResponse'),
            log: document.getElementById('log'),
            totalDocs: document.getElementById('totalDocs'),
            serverPort: document.getElementById('serverPort'),
            activeClients: document.getElementById('activeClients'),
            uploadSection: document.getElementById('uploadSection')
        };
    }
    
    setupEventListeners() {
        // File upload
        this.elements.fileInput.addEventListener('change', () => {
            this.elements.uploadBtn.disabled = !this.elements.fileInput.files.length;
        });
        
        this.elements.uploadBtn.addEventListener('click', () => {
            this.uploadFile();
        });
        
        // Drag and drop
        this.elements.uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.elements.uploadSection.classList.add('dragover');
        });
        
        this.elements.uploadSection.addEventListener('dragleave', () => {
            this.elements.uploadSection.classList.remove('dragover');
        });
        
        this.elements.uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            this.elements.uploadSection.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.elements.fileInput.files = files;
                this.elements.uploadBtn.disabled = false;
            }
        });
        
        // Real-time search
        this.elements.searchInput.addEventListener('input', () => {
            const query = this.elements.searchInput.value.trim();
            if (query.length > 2) {
                this.searchDocuments(query);
            } else {
                this.elements.searchResults.innerHTML = '';
            }
        });
        
        // Question asking
        this.elements.questionInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.askQuestion();
            }
        });
        
        this.elements.askBtn.addEventListener('click', () => {
            this.askQuestion();
        });
    }
    
    connect() {
        // Try servers in priority order
        const server = this.getNextServer();
        if (!server) {
            this.log('No available servers', 'error');
            return;
        }
        
        this.currentServer = server;
        const wsUrl = `ws://${server.host}:${server.port}`;
        
        this.log(`Connecting to ${wsUrl}...`, 'info');
        this.updateConnectionStatus('Connecting...', false);
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                this.onConnect();
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };
            
            this.ws.onclose = () => {
                this.onDisconnect();
            };
            
            this.ws.onerror = (error) => {
                this.log(`WebSocket error: ${error}`, 'error');
                this.tryNextServer();
            };
            
        } catch (error) {
            this.log(`Connection error: ${error}`, 'error');
            this.tryNextServer();
        }
    }
    
    getNextServer() {
        // Simple round-robin with priority
        return this.servers.find(server => server.priority === 1) || this.servers[0];
    }
    
    tryNextServer() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            this.log(`Trying next server (attempt ${this.reconnectAttempts})...`, 'info');
            
            setTimeout(() => {
                // Switch server priority for load balancing
                this.servers.forEach(server => {
                    server.priority = server.priority === 1 ? 2 : 1;
                });
                this.connect();
            }, this.reconnectDelay);
        } else {
            this.log('All connection attempts failed', 'error');
            this.updateConnectionStatus('Connection failed', false);
        }
    }
    
    onConnect() {
        this.reconnectAttempts = 0;
        this.log(`Connected to server on port ${this.currentServer.port}`, 'success');
        this.updateConnectionStatus(`Connected to port ${this.currentServer.port}`, true);
        this.enableControls(true);
        this.getStats();
    }
    
    onDisconnect() {
        this.log('Disconnected from server', 'error');
        this.updateConnectionStatus('Disconnected', false);
        this.enableControls(false);
        
        // Try to reconnect
        setTimeout(() => {
            this.connect();
        }, this.reconnectDelay);
    }
    
    updateConnectionStatus(message, connected) {
        this.elements.connectionStatus.textContent = message;
        this.elements.connectionStatus.className = `status ${connected ? 'connected' : 'disconnected'}`;
    }
    
    enableControls(enabled) {
        this.elements.uploadBtn.disabled = !enabled || !this.elements.fileInput.files.length;
        this.elements.searchInput.disabled = !enabled;
        this.elements.questionInput.disabled = !enabled;
        this.elements.askBtn.disabled = !enabled;
    }
    
    sendMessage(message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            this.log('WebSocket not connected', 'error');
        }
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'connection_status':
                this.elements.serverPort.textContent = data.server_port;
                break;
                
            case 'upload_complete':
                this.log(`File uploaded: ${data.filename}`, 'success');
                break;
                
            case 'processing_status':
                this.updateProgress(data.progress, data.status);
                break;
                
            case 'processing_complete':
                this.log('Document processing completed', 'success');
                this.hideProgress();
                break;
                
            case 'embedding_status':
                this.updateProgress(data.progress, data.status);
                break;
                
            case 'embedding_complete':
                this.log(`Document indexed: ${data.chunks_added} chunks`, 'success');
                this.hideProgress();
                this.getStats();
                break;
                
            case 'search_results':
                this.displaySearchResults(data.results);
                break;
                
            case 'ai_status':
                this.log(`AI processing: ${data.question}`, 'info');
                break;
                
            case 'ai_chunk':
                this.appendAIResponse(data.content);
                break;
                
            case 'ai_complete':
                this.log('AI response completed', 'success');
                break;
                
            case 'stats':
                this.updateStats(data.data);
                break;
                
            case 'error':
                this.log(`Error: ${data.message}`, 'error');
                break;
                
            default:
                this.log(`Unknown message type: ${data.type}`, 'info');
        }
    }
    
    uploadFile() {
        const file = this.elements.fileInput.files[0];
        if (!file) return;
        
        this.log(`Uploading file: ${file.name}`, 'info');
        this.showProgress();
        
        const reader = new FileReader();
        reader.onload = (e) => {
            const fileData = btoa(String.fromCharCode(...new Uint8Array(e.target.result)));
            
            this.sendMessage({
                type: 'file_upload',
                filename: file.name,
                file_data: fileData
            });
        };
        
        reader.readAsArrayBuffer(file);
    }
    
    searchDocuments(query) {
        this.sendMessage({
            type: 'search_query',
            query: query
        });
    }
    
    askQuestion() {
        const question = this.elements.questionInput.value.trim();
        if (!question) return;
        
        this.log(`Asking question: ${question}`, 'info');
        this.elements.aiResponse.innerHTML = '<div class="ai-response">Getting AI response...</div>';
        
        this.sendMessage({
            type: 'ask_question',
            question: question
        });
        
        this.elements.questionInput.value = '';
    }
    
    displaySearchResults(results) {
        if (!results || results.length === 0) {
            this.elements.searchResults.innerHTML = '<p>No results found</p>';
            return;
        }
        
        let html = '<h4>Search Results:</h4>';
        results.forEach((result, index) => {
            html += `
                <div class="result-item">
                    <div class="result-header">
                        ${result.metadata.filename} (Score: ${(result.score * 100).toFixed(1)}%)
                    </div>
                    <div class="result-content">
                        ${result.text.substring(0, 200)}...
                    </div>
                </div>
            `;
        });
        
        this.elements.searchResults.innerHTML = html;
    }
    
    appendAIResponse(content) {
        let responseDiv = this.elements.aiResponse.querySelector('.ai-response');
        if (!responseDiv) {
            responseDiv = document.createElement('div');
            responseDiv.className = 'ai-response';
            this.elements.aiResponse.innerHTML = '';
            this.elements.aiResponse.appendChild(responseDiv);
        }
        
        responseDiv.textContent += content;
    }
    
    updateProgress(progress, status) {
        this.elements.progressFill.style.width = `${progress}%`;
        this.elements.uploadStatus.textContent = status;
    }
    
    showProgress() {
        this.elements.uploadProgress.style.display = 'block';
        this.updateProgress(0, 'Starting...');
    }
    
    hideProgress() {
        setTimeout(() => {
            this.elements.uploadProgress.style.display = 'none';
            this.elements.uploadStatus.textContent = '';
        }, 2000);
    }
    
    getStats() {
        this.sendMessage({ type: 'get_stats' });
    }
    
    updateStats(stats) {
        this.elements.totalDocs.textContent = stats.total_documents || 0;
        this.elements.serverPort.textContent = stats.server_port || '-';
        this.elements.activeClients.textContent = stats.active_clients || 0;
    }
    
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${type}`;
        logEntry.textContent = `[${timestamp}] ${message}`;
        
        this.elements.log.appendChild(logEntry);
        this.elements.log.scrollTop = this.elements.log.scrollHeight;
        
        // Keep only last 100 log entries
        while (this.elements.log.children.length > 100) {
            this.elements.log.removeChild(this.elements.log.firstChild);
        }
    }
}

// Initialize client when page loads
document.addEventListener('DOMContentLoaded', () => {
    new DocumentQAClient();
});