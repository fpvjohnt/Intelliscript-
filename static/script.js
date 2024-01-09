document.getElementById('send-button').addEventListener('click', function() {
    var input = document.getElementById('message-input');
    var message = input.value;
    input.value = '';

    // Append the message to the sidebar as a query
    var sidebarQueries = document.querySelector('.sidebar .queries');
    var queryDiv = document.createElement('div');
    queryDiv.classList.add('query');
    queryDiv.innerHTML = `<p>${message}</p>`;
    sidebarQueries.appendChild(queryDiv);

    // Send the message to Flask server
    fetch('/send_message', {
        method: 'POST',
        body: new URLSearchParams('message=' + message),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(response => response.json())
    .then(data => {
        // Display the response and query in chat area
        var messagesArea = document.querySelector('.messages');
        var messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'output');
        messageDiv.innerHTML = `<p><strong>${data.query}</strong>: ${data.response}</p>`;
        messagesArea.appendChild(messageDiv);

        // Scroll to the latest message
        messagesArea.scrollTop = messagesArea.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
        displayInPageNotification('Error sending message. Please try again.');
    });
});

// Event listener for the file input change
document.getElementById('file-input').addEventListener('change', function(event) {
    var file = event.target.files[0];
    if (file) {
        var formData = new FormData();
        formData.append('file', file);

        // Send the file to the Flask server
        fetch('/upload_file', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            // Display a confirmation message or the response from the server
            displayInPageNotification(data.message);

            // Display the AI-generated summary if available
            if (data.summary) {
                var messagesArea = document.querySelector('.messages');
                var summaryMessageDiv = document.createElement('div');
                summaryMessageDiv.classList.add('message', 'output');
                summaryMessageDiv.innerHTML = `<p>AI Summary of <strong>${data.filename}</strong>:</p><p>${data.summary}</p>`;
                messagesArea.appendChild(summaryMessageDiv);
                messagesArea.scrollTop = messagesArea.scrollHeight;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayInPageNotification('Error uploading file. Please try again.');
        });
    }
});

// Helper function to display in-page notifications
function displayInPageNotification(message) {
    const notificationArea = document.getElementById('notification-area');
    if (!notificationArea) return;

    notificationArea.textContent = message;
    notificationArea.style.display = 'block';

    setTimeout(() => {
        notificationArea.style.display = 'none';
        notificationArea.textContent = '';
    }, 5000);
}
