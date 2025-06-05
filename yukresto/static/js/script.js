let currentPort = "5000";
let lastStock = [];
let lastOrders = {};
let lastMessages = [];
let selectedUser = null;

function toggleChat() {
    const chatBox = document.getElementById('chatBox');
    chatBox.style.display = chatBox.style.display === 'none' ? 'block' : 'none';
}

function showNotification(message) {
    const popup = document.getElementById('notificationPopup');
    popup.textContent = message;
    popup.style.display = 'block';
    setTimeout(() => popup.style.display = 'none', 5000);
}

function checkServerStatus() {
    console.log(`Checking server status on port ${currentPort}`);
    fetch(`http://localhost:${currentPort}/health`, { timeout: 2000 })
    .then(response => response.json())
    .then(data => {
        console.log(`Server on port ${currentPort} is alive:`, data);
        if (data.status !== "alive") {
            throw new Error("Server not alive");
        }
    })
    .catch(() => {
        const newPort = currentPort === "5000" ? "5003" : "5000";
        console.log(`Failed to reach port ${currentPort}, trying port ${newPort}`);
        fetch(`http://localhost:${newPort}/health`, { timeout: 2000 })
        .then(response => response.json())
        .then(data => {
            console.log(`Server on port ${newPort} is alive:`, data);
            if (data.status === "alive") {
                currentPort = newPort;
                showNotification(`Beralih ke server port ${currentPort}`);
            }
        })
        .catch(error => console.error('Both servers down:', error));
    });
}

function updateStock() {
    console.log(`Fetching stock from port ${currentPort}`);
    fetch(`http://localhost:${currentPort}/stock`)
    .then(response => response.json())
    .then(data => {
        console.log("Stock data received:", data);
        if (JSON.stringify(data) !== JSON.stringify(lastStock)) {
            const grid = document.querySelector('.grid');
            const menuSelect = document.getElementById('menuSelect');
            if (grid) {
                grid.innerHTML = '';
                let cabang = document.querySelector('nav span').textContent.includes('Cabang A') ? 'cabang_a' : 'cabang_b';
                let filteredData = data.filter(item => {
                    return cabang === 'cabang_a' ? 
                        (item.name === 'Pizza' && data.indexOf(item) < 2) || item.name === 'Burger' :
                        (item.name === 'Pizza' && data.indexOf(item) >= 2) || item.name === 'Soda';
                });
                filteredData.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'stock-card';
                    div.innerHTML = `
                        <img src="/static/images/${item.image}" alt="${item.name}">
                        <h3>${item.name}</h3>
                        <p>Stok: ${item.stock}</p>
                        <p>Harga: Rp ${item.price}</p>
                    `;
                    grid.appendChild(div);
                });
            }
            if (menuSelect) {
                const currentValue = menuSelect.value;
                menuSelect.innerHTML = '<option value="">Pilih Menu</option>';
                data.forEach(item => {
                    const option = document.createElement('option');
                    option.value = item.name;
                    option.textContent = `${item.name} - ${item.stock} tersedia`;
                    menuSelect.appendChild(option);
                });
                menuSelect.value = currentValue;
            }
            lastStock = data;
        }
    })
    .catch(error => console.error('Error updating stock:', error));
}

function calculateEstimation(minutes) {
    const now = new Date();
    now.setMinutes(now.getMinutes() + minutes);
    const date = now.getDate();
    const monthNames = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"];
    const month = monthNames[now.getMonth()];
    const year = now.getFullYear();
    const hours = String(now.getHours()).padStart(2, '0');
    const mins = String(now.getMinutes()).padStart(2, '0');
    return `${date} ${month} ${year}, ${hours}:${mins}`;
}

function updateOrders() {
    console.log(`Fetching orders from port ${currentPort}`);
    fetch(`http://localhost:${currentPort}/orders/user1`)
    .then(response => response.json())
    .then(data => {
        console.log("Orders data received:", data);
        if (JSON.stringify(data) !== JSON.stringify(lastOrders)) {
            const logMessages = document.getElementById('logMessages');
            const orderList = document.getElementById('orderList');
            if (logMessages) {
                logMessages.innerHTML = '';
                for (const order_id in data) {
                    const order = data[order_id];
                    const div = document.createElement('div');
                    div.className = 'order-card';
                    if (logMessages.closest('main').querySelector('h1').textContent.includes('Daftar Pesanan')) {
                        div.innerHTML = `
                            <p>${order_id}: ${order.menu} x${order.quantity} - ${order.status}</p>
                            <div class="estimation-buttons">
                                <button onclick="setEstimation('${order_id}', 10)">10 Menit</button>
                                <button onclick="setEstimation('${order_id}', 20)">20 Menit</button>
                                <button onclick="setEstimation('${order_id}', 30)">30 Menit</button>
                                <button onclick="setEstimation('${order_id}', 45)">45 Menit</button>
                                <button onclick="setEstimation('${order_id}', 60)">1 Jam</button>
                                <button onclick="promptCustomEstimation('${order_id}')">Kustom</button>
                            </div>
                        `;
                    } else {
                        div.innerHTML = `
                            <p>${order_id}: ${order.menu} x${order.quantity} - ${order.status}</p>
                        `;
                    }
                    logMessages.appendChild(div);
                }
            }
            if (orderList) {
                orderList.innerHTML = '';
                for (const order_id in data) {
                    const order = data[order_id];
                    const div = document.createElement('div');
                    div.className = 'order-list-item';
                    div.innerHTML = `
                        <p>${order_id}: ${order.menu} x${order.quantity} - ${order.status}</p>
                    `;
                    div.onclick = () => {
                        selectedUser = 'user1'; // Sementara hardcode, bisa diperluas untuk banyak user
                        document.getElementById('chatArea').style.display = 'block';
                        updateMessages();
                    };
                    orderList.appendChild(div);
                }
            }
            lastOrders = data;
        }
    })
    .catch(error => console.error('Error updating orders:', error));
}

function updateMessages() {
    if (!selectedUser && !document.getElementById('chatMessages')) return;
    const username = selectedUser || 'user1';
    console.log(`Fetching messages for ${username} from port ${currentPort}`);
    fetch(`http://localhost:${currentPort}/messages/${username}`)
    .then(response => response.json())
    .then(data => {
        console.log(`Messages data received for ${username}:`, data);
        if (JSON.stringify(data) !== JSON.stringify(lastMessages)) {
            const chatMessages = document.getElementById('chatMessages');
            if (chatMessages) {
                chatMessages.innerHTML = '';
                data.forEach(msg => {
                    const div = document.createElement('div');
                    div.className = 'message ' + (msg.sender === 'You' ? 'you' : 'cs');
                    div.textContent = `${msg.sender}: ${msg.text} (${msg.time})`;
                    chatMessages.appendChild(div);
                });
                chatMessages.scrollTop = chatMessages.scrollHeight;
                const lastMessage = data[data.length - 1];
                if (lastMessage && lastMessage.sender !== 'You' && !selectedUser) {
                    showNotification(`Pesan baru: ${lastMessage.text}`);
                }
            }
            lastMessages = data;
        }
    })
    .catch(error => console.error('Error updating messages:', error));
}

function setEstimation(orderId, minutes) {
    const estimation = calculateEstimation(minutes);
    fetch('/set_estimation', {
        method: 'POST',
        body: new URLSearchParams({
            'order_id': orderId,
            'estimation': estimation,
            'port': currentPort
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateOrders();
        }
    })
    .catch(error => console.error('Error setting estimation:', error));
}

function promptCustomEstimation(orderId) {
    const input = prompt("Masukkan waktu estimasi dalam menit (misalnya, 90 untuk 1 jam 30 menit):");
    if (input && !isNaN(input)) {
        const minutes = parseInt(input);
        setEstimation(orderId, minutes);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const orderForm = document.getElementById('orderForm');
    if (orderForm) {
        orderForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            formData.append('port', currentPort);
            fetch('/place_order', {
                method: 'POST',
                body: new URLSearchParams(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateOrders();
                }
            });
        });
    }

    const chatForm = document.getElementById('chatForm');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const message = document.getElementById('chatInput').value;
            const username = selectedUser || 'user1';
            const sender = selectedUser ? 'CS' : 'You';
            fetch('/send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({
                    'message': message,
                    'port': currentPort,
                    'username': username,
                    'sender': sender
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.getElementById('chatInput').value = '';
                    updateMessages();
                }
            })
            .catch(error => console.error('Error sending message:', error));
        });
    }

    setInterval(() => {
        checkServerStatus();
        updateStock();
        updateOrders();
        updateMessages();
    }, 3000); // Polling setiap 3 detik
});