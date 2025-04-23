const socket = io({ path: '/socket.io', transports: ['websocket'] });

socket.on('connect', () => {
    console.log('Connected to server');
});

function sendCommand(cmd) {
    socket.emit('command', { action: cmd });
}

// Video player setup (HLS)
const video = document.getElementById('videoPlayer');
const hlsUrl = '/hls/live.m3u8';
if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(hlsUrl);
    hls.attachMedia(video);
} else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = hlsUrl;
}
