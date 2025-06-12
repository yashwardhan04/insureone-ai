function toggleChat() {
    const chatPopup = document.getElementById("chat-popup");
    chatPopup.style.display = chatPopup.style.display === "none" ? "block" : "none";
}

function handleChatInput(event) {
    if (event.key === "Enter") {
        const input = document.getElementById("chat-input");
        const message = input.value.trim();
        if (message === "") return;

        appendMessage("You", message);
        input.value = "";

        fetch("/chatbot", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: message })
        })
        .then(response => response.json())
        .then(data => {
            appendMessage("Bot", data.answer);
        })
        .catch(error => {
            appendMessage("Bot", "Error: " + error.message);
        });
    }
}

function appendMessage(sender, message) {
    const chatBox = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");
    messageDiv.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}
