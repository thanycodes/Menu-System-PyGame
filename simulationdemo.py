import pygame
import numpy as np
from HUD import *
from HUD.button import *
import json

METER = 0.0015
SHIFT = [0.0, 0.0]
zoom = 1.0  # Added a zoom variable to control zoom level

def save_scene(name, data):
    with open(name, 'w') as write:
        json.dump(data, write)

def get_scene(name):
    data = None
    try:
        with open(name, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File {name} not found")
    return data

def normalize(vec):
    d = vec[0] * vec[0] + vec[1] * vec[1]
    return np.array(vec / (d ** 0.5))

class UiTextBox:
    def __init__(self, font_size, rect, color):
        self.focus = False
        self.text = ''
        self.textRect = pygame.Rect(rect)
        self.color = color
        self.font_size = font_size
        
    def render(self, window):
        if self.focus:
            pygame.draw.rect(window, (255, 255, 255), self.textRect, 2)
        else:
            pygame.draw.rect(window, (200, 200, 200), self.textRect, 2)
        textCaption = pygame.font.Font(None, self.font_size).render(self.text, True, self.color)
        window.blit(textCaption, (self.textRect.x + 5, self.textRect.y + 5))

    def update(self, event):
        if self.focus == False or len(self.text) > 15:
            return
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return
        self.text += event.unicode

class GameObject:
    def __init__(self, image_path, x: float = 0.0, y: float = 0.0, mass: float = 1.0, scale = 40.0):
        self.pos = np.array([x, y])
        self.v = np.array([0.0, 0.0])
        self.a = np.array([0.0, 0.0])
        self.scale = scale
        self.mass = mass
        self.color = [255, 1, 1]
        self.image_path = image_path
        self.image = pygame.image.load(image_path)
        self.image = pygame.transform.scale(self.image, (self.scale, self.scale))
        self.apos = [0, 0]

    def render(self, game):
        self.apos = [game.width / 2.0 + self.pos[0] * METER + SHIFT[0], game.height / 2.0 - self.pos[1] * METER - SHIFT[1]]
        game.window.blit(self.image, (self.apos[0], self.apos[1]))
        self.render_v(game)

    def render_v(self, game):
        epos = (self.apos[0] + self.v[0] * 0.3 * METER, self.apos[1] - self.v[1] * 0.3 * METER)
        pygame.draw.line(game.window, (0, 0, 255), (self.apos[0], self.apos[1]), epos, 2)

    def render_a(self, game):
        epos = (self.apos[0] + self.a[0] * 0.3 * METER, self.apos[1] - self.a[1] * 0.3 * METER)
        pygame.draw.line(game.window, (255, 0, 0), (self.apos[0], self.apos[1]), epos, 2)

    def apply_physics(self, dt: float):
        self.render_a(game)
        self.v += self.a * dt
        self.pos += self.v * dt
        self.a[0] = 0.0
        self.a[1] = 0.0

class Game:
    def __init__(self):
        self.width = 960
        self.height = 640
        self.running = True
        self.start_simulation = False
        self.mouse_pre = [0, 0]

        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        self.window.fill(0x111111)

        self.objects = []
        self.textBox = UiTextBox(24, (10, 20, 140, 32), "#61f255")

        self.buttons = [
                Button(image=None, pos=(40, 80), input="START", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(40, 120), input="SAVE", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(40, 240), input="EARTH", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(40, 280), input="JUPITER", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(40, 320), input="MOON", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(40, 360), input="MARS", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
                Button(image=None, pos=(40, 400), input="ROCKET", font=pygame.font.Font(None, 24), baseColor="White", hoverColor="#61f255"),
        ]
        self.buttons_callback = [
                self.start_button_impl,
                self.save_button_impl,
                self.earth_button_impl,
                self.jupiter_button_impl,
                self.moon_button_impl,
                self.mars_button_impl,
                self.rocket_button_impl
        ]
        self.holded_callback = None
        self.edit_obj = None

    # Add a method to handle zooming
    def handle_zoom(self, direction):
        global METER
        global zoom
        zoom_step = 0.1
        if direction == "in":
            zoom += zoom_step
        elif direction == "out" and zoom > zoom_step:
            zoom -= zoom_step
        
        METER = 0.0015 * zoom

    def eventhandle(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            MenuMousePos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.textBox.focus = self.textBox.textRect.collidepoint(event.pos)
                if event.button == 1 and self.holded_callback != None:
                    self.holded_callback()
                    self.mouse_pre = event.pos
                    self.objects[-1].pos[0] = (event.pos[0] - game.width / 2.0 - SHIFT[0]) / METER
                    self.objects[-1].pos[1] = (game.height / 2.0 - event.pos[1] - SHIFT[1]) / METER
                # Handle zoom in and out using scroll wheel
                if event.button == 4:  # Scroll up
                    self.handle_zoom("in")
                elif event.button == 5:  # Scroll down
                    self.handle_zoom("out")
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.holded_callback != None:
                    diff = [event.pos[0] - self.mouse_pre[0], self.mouse_pre[1] - event.pos[1]]
                    self.objects[-1].v[0] = diff[0] * 100
                    self.objects[-1].v[1] = diff[1] * 100
                    self.holded_callback = None
                for i in range(len(self.buttons)):
                    if self.buttons[i].checkForInput(MenuMousePos):
                        self.buttons_callback[i]()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.start_simulation = False
                    if len(self.textBox.text) == 0:
                        self.objects = []
                        return
                    self.local_scene()
                    return
                if event.key == pygame.K_SPACE:
                    self.start_simulation = not self.start_simulation
                self.textBox.update(event)

    def render_ui(self):
        MenuMousePos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.changeColor(MenuMousePos)
            button.update(self.window)
        self.textBox.render(self.window)

    def render(self):
        for obj in self.objects[::-1]:
            obj.render(self)
        self.render_ui()

    def update_simulations(self, dt):
        G = 6.67e-11
        for objA in self.objects:
            for objB in self.objects:
                if objB == objA:
                    continue
                d = np.linalg.norm(objA.pos - objB.pos)
                normal = (objA.pos - objB.pos) / d
                A = objA.mass * G / (d * d)
                objB.a += A * normal
        for obj in self.objects:
            obj.apply_physics(dt)

    def update(self, dt):
        if self.start_simulation:
            self.key_input()
            self.update_simulations(dt)

    def key_input(self):
        if self.textBox.focus:
            return
        speed = 10
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            SHIFT[0] += speed
        if keys[pygame.K_d]:
            SHIFT[0] -= speed
        if keys[pygame.K_w]:
            SHIFT[1] -= speed
        if keys[pygame.K_s]:
            SHIFT[1] += speed

game = Game()
FPS = 60
time = pygame.time.Clock()
while game.running:
    game.eventhandle()
    game.window.fill(0x111111)
    game.render()
    game.update(1.0 / FPS)
    pygame.display.update()
    time.tick(FPS)

pygame.quit()
