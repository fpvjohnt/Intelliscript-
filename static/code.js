document.getElementById('send-button').addEventListener('click', sendMessage);
document.getElementById('question-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    const codeInput = document.getElementById('code-input').value;
    const questionInput = document.getElementById('question-input').value;
    
    // Clear the question input box
    document.getElementById('question-input').value = '';

    // Prepare data to be sent to the Flask server
    const data = {
        code: codeInput,
        question: questionInput
    };

    fetch('/ask-code-question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Assuming the Flask response contains a field 'response'
        const responseContainer = document.getElementById('response-container');
        responseContainer.innerHTML = data.response;  // Display the AI's response
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
