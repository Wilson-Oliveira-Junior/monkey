import sys
import os
import random
import subprocess
import time
import threading
from PySide6.QtWidgets import QApplication, QLabel, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QPainter
from PySide6.QtMultimedia import QSoundEffect
import requests

class MonkeyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(256, 256)  # Aumenta o tamanho do personagem
        self.sprites = self.load_sprites()
        self.current_frame = 0
        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 256, 256)
        if self.sprites:
            self.label.setPixmap(self.sprites[0])
        self.move(100, 100)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_and_move)
        self.timer.start(100)
        self.action_timer = QTimer(self)
        self.action_timer.timeout.connect(self.random_action)
        self.action_timer.start(10000)  # A cada 10 segundos, tenta uma ação
    def load_sprites(self):
        sprite_dir = os.path.join(os.path.dirname(__file__), 'sprites')
        frames = []
        if os.path.exists(sprite_dir):
            for fname in sorted(os.listdir(sprite_dir)):
                if fname.lower().endswith('.png'):
                    pix = QPixmap(os.path.join(sprite_dir, fname)).scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    frames.append(pix)
        if not frames:
            # Placeholder: desenha um círculo marrom
            pix = QPixmap(256, 256)
            pix.fill(Qt.transparent)
            painter = QPainter(pix)
            painter.setBrush(Qt.darkYellow)
            painter.drawEllipse(32, 32, 192, 192)
            painter.end()
            frames.append(pix)
        return frames
    def animate_and_move(self):
        # Animação
        if self.sprites:
            self.current_frame = (self.current_frame + 1) % len(self.sprites)
            self.label.setPixmap(self.sprites[self.current_frame])
        # Movimento aleatório realista
        if not hasattr(self, 'direction'):
            self.direction = [random.choice([-1, 1]), random.choice([-1, 1])]
        if random.random() < 0.05:
            # 5% de chance de mudar de direção
            self.direction = [random.choice([-1, 0, 1]), random.choice([-1, 0, 1])]
            if self.direction == [0, 0]:
                self.direction = [1, 1]
        speed = random.randint(2, 8)
        dx = self.direction[0] * speed
        dy = self.direction[1] * speed
        x = self.x() + dx
        y = self.y() + dy
        screen = QApplication.primaryScreen().geometry()
        if x < 0 or x + self.width() > screen.width():
            self.direction[0] *= -1
            x = self.x() + self.direction[0] * speed
        if y < 0 or y + self.height() > screen.height():
            self.direction[1] *= -1
            y = self.y() + self.direction[1] * speed
        self.move(x, y)
    def play_sound(self, sound_file):
        effect = QSoundEffect()
        effect.setSource(sound_file)
        effect.setVolume(0.5)
        effect.play()
        # Mantém o objeto vivo até o som terminar
        threading.Timer(2, lambda: None).start()
    def random_action(self):
        actions = [self.open_notepad_and_type_fact, self.play_random_sound]
        action = random.choice(actions)
        action()
    def open_notepad_and_type_fact(self):
        fact = self.get_online_fact()
        if not fact:
            facts = [
                'Macacos podem usar ferramentas!',
                'O macaco-prego é muito inteligente.',
                'Macacos vivem em grupos sociais complexos.',
                'Alguns macacos gostam de nadar!',
                'O macaco-aranha tem cauda preênsil.'
            ]
            fact = random.choice(facts)
        # Abre o bloco de notas
        subprocess.Popen(['notepad.exe'])
        # Aguarda o bloco de notas abrir
        time.sleep(1.5)
        # Digita o fato usando pyautogui
        try:
            import pyautogui
            pyautogui.write(fact, interval=0.05)
        except ImportError:
            print('pyautogui não instalado. Rode: pip install pyautogui')
    def get_online_fact(self):
        # Tenta buscar um fato aleatório da internet (em português)
        try:
            resp = requests.get('https://uselessfacts.jsph.pl/random.json?language=pt')
            if resp.status_code == 200:
                data = resp.json()
                return data.get('text')
        except Exception as e:
            print('Erro ao buscar fato online:', e)
        return None
    def play_random_sound(self):
        # Coloque arquivos .wav na pasta 'sounds' (ex: monkey1.wav, monkey2.wav)
        sound_dir = os.path.join(os.path.dirname(__file__), 'sounds')
        if os.path.exists(sound_dir):
            sounds = [f for f in os.listdir(sound_dir) if f.lower().endswith('.wav')]
            if sounds:
                sound_file = os.path.join(sound_dir, random.choice(sounds))
                self.play_sound('file:///' + sound_file.replace('\\', '/'))
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    monkey = MonkeyWidget()
    monkey.show()
    sys.exit(app.exec())
