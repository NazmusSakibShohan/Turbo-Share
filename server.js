const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: { origin: "*" }
});

// index.html ফাইলটি দেখানোর জন্য
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

io.on('connection', (socket) => {
    socket.on('join', (room) => {
        socket.join(room);
        socket.to(room).emit('user-joined');
    });

    socket.on('signal', (data) => {
        io.to(data.room).emit('signal', data);
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));