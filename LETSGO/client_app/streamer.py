import asyncio
import json
import os
import subprocess
import sys
import websockets
import threading
import PySimpleGUI as sg

VPS_HOST = '78.135.85.65'
PANEL_PORT = 8181
SOCKET_PORT = 5000

FFMPEG_CMD = [
    'ffmpeg',
    '-y',
    '-f', 'gdigrab', '-framerate', '30', '-i', 'desktop',
    '-f', 'dshow', '-i', 'video=Integrated Webcam',
    '-filter_complex', '[1:v]scale=320:-1[cam];[0:v][cam]overlay=main_w-330:main_h-250',
    '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '2M',
    '-f', 'flv', f'rtmp://{VPS_HOST}/live/stream'
]

class Streamer:
    def __init__(self):
        self.proc = None
        self.cam_enabled = True
        self.thread = threading.Thread(target=self.ws_loop, daemon=True)
        self.thread.start()

    def start_stream(self):
        if self.proc:
            return
        cmd = FFMPEG_CMD.copy()
        if not self.cam_enabled:
            # remove camera input/overlay
            cmd = [
                'ffmpeg', '-y',
                '-f', 'gdigrab', '-framerate', '30', '-i', 'desktop',
                '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '2M',
                '-f', 'flv', f'rtmp://{VPS_HOST}/live/stream'
            ]
        print('Başlatılıyor:', ' '.join(cmd))
        self.proc = subprocess.Popen(cmd)

    def stop_stream(self):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
            self.proc = None

    async def ws_handler(self):
        uri = f'ws://{VPS_HOST}:{SOCKET_PORT}/socket.io/?EIO=4&transport=websocket&role=client'
        async with websockets.connect(uri) as websocket:
            print('WebSocket bağlı')
            while True:
                msg = await websocket.recv()
                # socket.io framing: 42["command",{"action":"start"}]
                if msg.startswith('42'):
                    payload = json.loads(msg[2:])[1]
                    action = payload.get('action')
                    if action == 'start':
                        self.start_stream()
                    elif action == 'stop':
                        self.stop_stream()
                    elif action == 'toggle_cam':
                        self.cam_enabled = not self.cam_enabled
                        if self.proc:
                            self.stop_stream()
                            self.start_stream()

    def ws_loop(self):
        asyncio.run(self.ws_handler())


if __name__ == '__main__':
    streamer = Streamer()

    layout = [[sg.Text('Yayıncı')],
              [sg.Button('Başlat'), sg.Button('Durdur'), sg.Button('Kamera Aç/Kapa')]]
    window = sg.Window('Yayıncı', layout)

    while True:
        event, _ = window.read(timeout=100)
        if event == sg.WIN_CLOSED:
            break
        elif event == 'Başlat':
            streamer.start_stream()
        elif event == 'Durdur':
            streamer.stop_stream()
        elif event == 'Kamera Aç/Kapa':
            streamer.cam_enabled = not streamer.cam_enabled
            if streamer.proc:
                streamer.stop_stream()
                streamer.start_stream()

    streamer.stop_stream()
    window.close()
