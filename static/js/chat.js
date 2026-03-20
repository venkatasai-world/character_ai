/**
 * AI Character Chat JS
 * Handles: messaging, stickers, emojis, voice input/output, language, animations
 */

// ===================== STATE =====================
let isRecording = false;
let recognition = null;
let voiceOutputEnabled = false;
let stickerPanelOpen = false;
let emojiPanelOpen = false;
let isSending = false;

// ===================== INIT =====================
document.addEventListener('DOMContentLoaded', function() {
    scrollToBottom(false);
    initSpeechRecognition();
    populateEmojis();
});

// ===================== STARS =====================
function generateStars() {
    const container = document.getElementById('chatStars');
    if (!container) return;
    for (let i = 0; i < 60; i++) {
        const star = document.createElement('div');
        star.style.cssText = `
            position:absolute;
            left:${Math.random()*100}%;
            top:${Math.random()*100}%;
            width:${Math.random()*2+1}px;
            height:${Math.random()*2+1}px;
            background:white;
            border-radius:50%;
            opacity:${Math.random()*0.4+0.05};
            animation:twinkle ${Math.random()*4+3}s ease-in-out infinite;
            animation-delay:${Math.random()*4}s;
        `;
        container.appendChild(star);
    }
}

// ===================== SEND MESSAGE =====================
async function sendMessage() {
    if (isSending) return;
    const input = document.getElementById('messageInput');
    const text = input.value.trim();
    if (!text) return;

    isSending = true;
    input.value = '';
    input.style.height = 'auto';
    document.getElementById('sendBtn').disabled = true;

    // Add user message to UI
    appendMessage({ role: 'user', type: 'text', content: text, timestamp: nowTime() });

    // Show typing indicator
    showTyping(true);
    scrollToBottom();

    try {
        const response = await fetch(SEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: text,
                type: 'text',
                language: currentLanguage
            })
        });

        const data = await response.json();

        if (data.success) {
            showTyping(false);
            appendMessage(data.ai_message);
            scrollToBottom();

            // Text-to-speech if enabled
            if (voiceOutputEnabled && data.ai_message.content) {
                speakText(data.ai_message.content);
            }
        } else {
            showTyping(false);
            appendMessage({ role: 'model', type: 'text', content: '⚠️ Something went wrong. Please try again.', timestamp: nowTime() });
        }
    } catch (err) {
        console.error('Send message error:', err);
        showTyping(false);
        appendMessage({ role: 'model', type: 'text', content: '⚠️ Connection error. Please check your internet.', timestamp: nowTime() });
    }

    isSending = false;
    document.getElementById('sendBtn').disabled = false;
}

// ===================== SEND STICKER =====================
async function sendSticker(filename) {
    if (isSending) return;
    isSending = true;

    // Close sticker panel
    toggleStickerPanel();

    // Add sticker to UI
    appendMessage({ role: 'user', type: 'sticker', content: filename, timestamp: nowTime() });
    showTyping(true);
    scrollToBottom();

    try {
        const response = await fetch(SEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: filename,
                type: 'sticker',
                language: currentLanguage
            })
        });

        const data = await response.json();
        showTyping(false);

        if (data.success) {
            appendMessage(data.ai_message);
            scrollToBottom();
        }
    } catch (err) {
        showTyping(false);
        console.error(err);
    }

    isSending = false;
}

// ===================== APPEND MESSAGE =====================
function appendMessage(msg) {
    const container = document.getElementById('chatMessages');
    
    // Remove welcome screen if exists
    const welcome = container.querySelector('.chat-welcome');
    if (welcome) welcome.remove();

    const isUser = msg.role === 'user';
    const row = document.createElement('div');
    row.className = `message-row ${isUser ? 'user-row' : 'ai-row'}`;
    row.style.animation = 'messageFadeIn 0.4s ease';

    let avatarHTML = '';
    if (isUser) {
        avatarHTML = USER_AVATAR
            ? `<img src="${USER_AVATAR}" alt="You">`
            : `<span>${USER_INITIAL}</span>`;
    } else {
        avatarHTML = CHARACTER_AVATAR
            ? `<img src="${CHARACTER_AVATAR}" alt="${CHARACTER_NAME}">`
            : `<span>${CHAR_INITIAL}</span>`;
    }

    const avatarClass = isUser ? 'user-msg-avatar' : 'ai-msg-avatar';

    let bubbleContent = '';
    if (msg.type === 'sticker') {
        bubbleContent = `<img src="/static/stickers/${msg.content}" alt="Sticker" class="sticker-message" onerror="this.style.display='none'">`;
    } else {
        bubbleContent = `<p>${escapeHTML(msg.content)}</p>`;
    }

    const bubbleClass = isUser ? 'user-bubble' : 'ai-bubble';
    const avatar = `<div class="message-avatar ${avatarClass}">${avatarHTML}</div>`;
    const bubble = `<div class="message-bubble ${bubbleClass}">${bubbleContent}<span class="msg-time">${msg.timestamp || ''}</span></div>`;

    row.innerHTML = isUser ? `${bubble}${avatar}` : `${avatar}${bubble}`;
    
    // Insert before typing indicator
    const typingIndicator = document.getElementById('typingIndicator');
    container.insertBefore(row, typingIndicator);
}

// ===================== TYPING INDICATOR =====================
function showTyping(show) {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.style.display = show ? 'flex' : 'none';
        const statusEl = document.getElementById('headerStatus');
        if (statusEl) {
            if (show) {
                statusEl.innerHTML = '<span class="status-dot online-anim"></span> AI is typing...';
            } else {
                statusEl.innerHTML = `<span class="status-dot online-anim"></span> Online`;
            }
        }
    }
}

// ===================== SCROLL =====================
function scrollToBottom(smooth = true) {
    const container = document.getElementById('chatMessages');
    if (container) {
        container.scrollTo({
            top: container.scrollHeight,
            behavior: smooth ? 'smooth' : 'auto'
        });
    }
}

// ===================== KEYBOARD =====================
function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 100) + 'px';
}

// ===================== SIDEBAR TOGGLE =====================
function toggleSidebar() {
    const sidebar = document.getElementById('chatSidebar');
    sidebar.classList.toggle('open');
}

// ===================== STICKER PANEL =====================
function toggleStickerPanel() {
    const panel = document.getElementById('stickerPanel');
    const emojiPanel = document.getElementById('emojiPanel');
    
    stickerPanelOpen = !stickerPanelOpen;
    panel.classList.toggle('open', stickerPanelOpen);
    
    // Close emoji if open
    if (emojiPanelOpen) {
        emojiPanelOpen = false;
        emojiPanel.classList.remove('open');
    }

    document.getElementById('stickerBtn').classList.toggle('active', stickerPanelOpen);
}

// ===================== EMOJI PANEL =====================
const EMOJIS = ['😀','😂','🥰','😎','🤔','😮','😢','😡','🥳','😴',
                '👍','👎','❤️','🔥','⭐','✨','🎉','🎭','🤖','👾',
                '🌟','💫','🚀','🌙','⚡','💎','🎵','🎮','📱','💡',
                '🙏','💪','👀','🤝','✌️','🫶','💯','🔮','🌈','🦄',
                '🐶','🐱','🐼','🦊','🐸','🦁','🦋','🌸','🍕','🍦'];

function populateEmojis() {
    const grid = document.getElementById('emojiGrid');
    if (!grid) return;
    EMOJIS.forEach(emoji => {
        const item = document.createElement('div');
        item.className = 'emoji-item';
        item.textContent = emoji;
        item.onclick = () => insertEmoji(emoji);
        grid.appendChild(item);
    });
}

function toggleEmojiPanel() {
    const panel = document.getElementById('emojiPanel');
    const stickerPanel = document.getElementById('stickerPanel');

    emojiPanelOpen = !emojiPanelOpen;
    panel.classList.toggle('open', emojiPanelOpen);

    if (stickerPanelOpen) {
        stickerPanelOpen = false;
        stickerPanel.classList.remove('open');
    }

    document.getElementById('emojiBtn').classList.toggle('active', emojiPanelOpen);
}

function insertEmoji(emoji) {
    const input = document.getElementById('messageInput');
    const start = input.selectionStart;
    const end = input.selectionEnd;
    input.value = input.value.substring(0, start) + emoji + input.value.substring(end);
    input.selectionStart = input.selectionEnd = start + emoji.length;
    input.focus();
    autoResize(input);
}

// Close panels on outside click
document.addEventListener('click', function(e) {
    if (!e.target.closest('#emojiPanel') && !e.target.closest('#emojiBtn')) {
        if (emojiPanelOpen) {
            emojiPanelOpen = false;
            document.getElementById('emojiPanel').classList.remove('open');
            document.getElementById('emojiBtn').classList.remove('active');
        }
    }
    if (!e.target.closest('#stickerPanel') && !e.target.closest('#stickerBtn')) {
        if (stickerPanelOpen) {
            stickerPanelOpen = false;
            document.getElementById('stickerPanel').classList.remove('open');
            document.getElementById('stickerBtn').classList.remove('active');
        }
    }
});

// ===================== VOICE INPUT =====================
function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = currentLanguage || 'en-US';

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('messageInput').value = transcript;
            autoResize(document.getElementById('messageInput'));
            stopRecording();
            sendMessage();
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            stopRecording();
        };

        recognition.onend = function() {
            stopRecording();
        };
    }
}

function toggleVoiceInput() {
    if (!recognition) {
        alert('Speech recognition is not supported in your browser. Try Chrome.');
        return;
    }

    if (isRecording) {
        recognition.stop();
        stopRecording();
    } else {
        recognition.lang = getLangCode(currentLanguage);
        recognition.start();
        startRecording();
    }
}

function startRecording() {
    isRecording = true;
    const micBtn = document.getElementById('micBtn');
    micBtn.classList.add('recording');
    micBtn.title = 'Stop recording';
}

function stopRecording() {
    isRecording = false;
    const micBtn = document.getElementById('micBtn');
    micBtn.classList.remove('recording');
    micBtn.title = 'Voice input';
}

// ===================== VOICE OUTPUT =====================
function toggleVoiceOutput() {
    voiceOutputEnabled = !voiceOutputEnabled;
    const btn = document.getElementById('voiceOutputBtn');
    btn.classList.toggle('active', voiceOutputEnabled);
    btn.title = voiceOutputEnabled ? 'Voice output: ON' : 'Voice output: OFF';
    
    if (!voiceOutputEnabled) {
        window.speechSynthesis.cancel();
    }
}

function speakText(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = getLangCode(currentLanguage);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    
    // Try to get a good voice
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => v.lang.startsWith(currentLanguage));
    if (preferredVoice) utterance.voice = preferredVoice;
    
    window.speechSynthesis.speak(utterance);
}

// ===================== LANGUAGE =====================
function changeLanguage(lang) {
    currentLanguage = lang;
    if (recognition) recognition.lang = getLangCode(lang);

    // Save preference
    fetch('/profile/update-language', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: lang })
    }).catch(err => console.error('Language update failed:', err));
}

function getLangCode(lang) {
    const codes = {
        'en': 'en-US', 'hi': 'hi-IN', 'es': 'es-ES', 'fr': 'fr-FR',
        'de': 'de-DE', 'ja': 'ja-JP', 'ko': 'ko-KR', 'zh': 'zh-CN',
        'ar': 'ar-SA', 'pt': 'pt-BR', 'ru': 'ru-RU', 'te': 'te-IN', 'ta': 'ta-IN'
    };
    return codes[lang] || 'en-US';
}

// ===================== CLEAR CHAT =====================
async function clearChat() {
    if (!confirm(`Clear all messages with ${CHARACTER_NAME}?`)) return;
    
    try {
        await fetch(CLEAR_URL, { method: 'POST' });
        const container = document.getElementById('chatMessages');
        // Remove all message rows
        container.querySelectorAll('.message-row').forEach(el => el.remove());
        // Add welcome back
        const welcome = document.createElement('div');
        welcome.className = 'chat-welcome';
        welcome.innerHTML = `
            <div class="welcome-char-avatar">${CHARACTER_AVATAR ? `<img src="${CHARACTER_AVATAR}" alt="${CHARACTER_NAME}">` : `<span>${CHAR_INITIAL}</span>`}</div>
            <h3>Chat cleared! Say hi to ${CHARACTER_NAME} 👋</h3>
        `;
        container.insertBefore(welcome, document.getElementById('typingIndicator'));
    } catch (err) {
        console.error('Clear chat error:', err);
    }
}

// ===================== UTILS =====================
function nowTime() {
    const now = new Date();
    return now.getHours().toString().padStart(2,'0') + ':' + now.getMinutes().toString().padStart(2,'0');
}

function escapeHTML(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML.replace(/\n/g, '<br>');
}

// Add CSS animation for twinkle (used by star generator)
const style = document.createElement('style');
style.textContent = `
@keyframes twinkle {
    0%, 100% { opacity: 0.05; transform: scale(1); }
    50% { opacity: 0.6; transform: scale(1.4); }
}
`;
document.head.appendChild(style);
