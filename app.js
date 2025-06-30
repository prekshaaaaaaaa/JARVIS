const chat = document.getElementById('chatBox');
const input = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const voiceBtn = document.getElementById('voiceBtn');
const typing = document.querySelector('.typing-indicator');

function addBubble(text, who) {
  const div = document.createElement('div');
  div.className = `bubble ${who}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function sendMessage(msg) {
  typing.hidden = false;
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });
    const { reply } = await res.json();
    if (!reply) return;

    addBubble(reply, 'jarvis');

    window.speechSynthesis.cancel(); // Stop any ongoing speech
    const utter = new SpeechSynthesisUtterance(reply);
    utter.lang = 'en-US';
    window.speechSynthesis.speak(utter);
    // ⚠ No utter.onend here!

  } catch (err) {
    console.error(err);
    addBubble("⚠️ Can't reach Jarvis", 'jarvis');
  } finally {
    typing.hidden = true;
  }
}

let sending = false;
sendBtn.onclick = () => {
  if (sending) return;
  const msg = input.value.trim();
  if (!msg) return;
  sending = true;

  addBubble(msg, 'user');
  input.value = '';
  sendMessage(msg).finally(() => sending = false);
};

input.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    e.preventDefault();
    sendBtn.click();
  }
});

