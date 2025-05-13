const ws = new WebSocket('ws://localhost:8000/ws');  // Connect to WebSocket server
const notificationsList = document.getElementById('notifications');

// Handle WebSocket messages
ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    const listItem = document.createElement('li');
    listItem.className = "list-group-item list-group-item-info";
    listItem.textContent = `🚨 ${notification.message} at 📍 ${notification.location}`;
    notificationsList.appendChild(listItem);
};

// Handle image upload
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('image', document.getElementById('image').files[0]);
    formData.append('location', document.getElementById('location').value);

    try {
        const response = await fetch('http://localhost:8000/upload', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        alert(result.message);  // Show upload result
    } catch (error) {
        console.error('Error:', error);
        alert('❌ Failed to upload image.');
    }
});
