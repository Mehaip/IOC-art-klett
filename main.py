import sys
import math
import random
import pygame
import json
import os
from PIL import Image, ImageDraw, ImageFont

# Initialize Pygame
pygame.init()

# Font renderer using PIL/Pillow
class FontWrapper:
    """Text renderer using PIL/Pillow for proper font rendering"""
    def __init__(self, size):
        self.size = size
        try:
            # Try to load a default system font
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except:
            try:
                self.font = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", size)
            except:
                try:
                    # Fallback to basic font
                    self.font = ImageFont.load_default()
                except:
                    self.font = None

    def render(self, text, antialias, color):
        if not text:
            return pygame.Surface((1, 1), pygame.SRCALPHA)

        # Get text size
        if self.font and hasattr(self.font, 'getbbox'):
            bbox = self.font.getbbox(text)
            width = bbox[2] - bbox[0] + 10
            height = bbox[3] - bbox[1] + 10
        else:
            width = len(text) * (self.size // 2) + 20
            height = self.size + 10

        # Create PIL image
        pil_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(pil_image)

        # Draw text
        if self.font:
            draw.text((5, 5), text, font=self.font, fill=color)
        else:
            # Fallback if no font available
            draw.text((5, 5), text, fill=color)

        # Convert PIL image to pygame surface
        mode = pil_image.mode
        size = pil_image.size
        data = pil_image.tobytes()

        surface = pygame.image.fromstring(data, size, mode)

        return surface

# Constants
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SPACE_BLUE = (10, 10, 40)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
PINK = (255, 105, 180)

# Game States
MENU = 0
EXPLORATION = 1
INFO = 2
QUIZ = 3
DODGE = 4
SLIDESHOW = 5
NOTES = 6

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Sa invatam planetele - Aventura educationala")
        self.clock = pygame.time.Clock()
        self.state = MENU
        self.font_large = FontWrapper(120)
        self.font_medium = FontWrapper(80)
        self.font_small = FontWrapper(60)

        # Game objects
        self.astronaut = Astronaut(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.planets = self.create_planets()
        self.current_planet = None
        self.quiz = None
        self.dodge_game = None
        self.visited_planets = set()
        self.slideshow = None
        self.notes = None

    def create_planets(self):
        """Create planets at different positions"""
        planets = [
            Planet("Mercur", 200, 200, 30, (169, 169, 169)),
            Planet("Venus", 700, 150, 45, (255, 198, 73)),
            Planet("Pamant", 300, 500, 50, (100, 149, 237)),
            Planet("Marte", 800, 450, 40, (188, 39, 50)),
            Planet("Jupiter", 500, 600, 80, (201, 138, 87)),
            Planet("Saturn", 150, 400, 70, (238, 217, 130)),
            Planet("Uranus", 650, 600, 55, (79, 208, 231)),
            Planet("Neptun", 900, 250, 55, (62, 84, 232)),
            Planet("Hai sa invatam", 500, 300, 60, PINK, is_slideshow=True, has_smiley=True),
            Planet("Notite", 400, 100, 55, (135, 206, 250), is_notes=True, has_smiley=True),  # Light blue
        ]
        return planets

    def run(self):
        running = True
        while running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.handle_events(event)

            self.update()
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_events(self, event):
        if self.state == MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                # Check if start button clicked
                button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60)
                if button_rect.collidepoint(mouse_pos):
                    self.state = EXPLORATION

        elif self.state == EXPLORATION:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Check if near a planet
                    for planet in self.planets:
                        if planet.check_collision(self.astronaut):
                            self.current_planet = planet
                            if planet.is_slideshow:
                                self.state = SLIDESHOW
                                self.slideshow = Slideshow()
                            elif planet.is_notes:
                                self.state = NOTES
                                self.notes = Notes()
                            else:
                                self.state = INFO
                            break

        elif self.state == INFO:
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self.state = QUIZ
                self.quiz = Quiz(self.current_planet.name)

        elif self.state == QUIZ:
            if self.quiz:
                self.quiz.handle_event(event)
                if self.quiz.finished:
                    if self.quiz.score == 5:
                        self.state = DODGE
                        self.dodge_game = DodgeGame()
                    else:
                        self.state = EXPLORATION
                        self.quiz = None

        elif self.state == DODGE:
            if self.dodge_game:
                self.dodge_game.handle_event(event)
                if self.dodge_game.finished:
                    self.visited_planets.add(self.current_planet.name)
                    self.state = EXPLORATION
                    self.dodge_game = None
                    self.current_planet = None

        elif self.state == SLIDESHOW:
            if self.slideshow:
                self.slideshow.handle_event(event)
                if self.slideshow.closed:
                    self.state = EXPLORATION
                    self.slideshow = None
                    self.current_planet = None

        elif self.state == NOTES:
            if self.notes:
                self.notes.handle_event(event)
                if self.notes.closed:
                    self.state = EXPLORATION
                    self.notes = None
                    self.current_planet = None

    def update(self):
        if self.state == EXPLORATION:
            keys = pygame.key.get_pressed()
            self.astronaut.update(keys)

        elif self.state == DODGE:
            if self.dodge_game:
                self.dodge_game.update()

    def draw(self):
        self.screen.fill(SPACE_BLUE)

        if self.state == MENU:
            self.draw_menu()
        elif self.state == EXPLORATION:
            self.draw_exploration()
        elif self.state == INFO:
            self.draw_info()
        elif self.state == QUIZ:
            self.draw_quiz()
        elif self.state == DODGE:
            self.draw_dodge()
        elif self.state == SLIDESHOW:
            self.draw_slideshow()
        elif self.state == NOTES:
            self.draw_notes()

    def draw_menu(self):
        # Draw stars background
        for i in range(100):
            x = (i * 137) % SCREEN_WIDTH
            y = (i * 219) % SCREEN_HEIGHT
            size = (i % 3) + 1
            pygame.draw.circle(self.screen, WHITE, (x, y), size)

        # Title
        title = self.font_large.render("SA INVATAM PLANETELE", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 - 20))
        self.screen.blit(title, title_rect)

        # Subtitle
        subtitle = self.font_small.render("(cu ajutorul manualului ArtKlett)", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 40))
        self.screen.blit(subtitle, subtitle_rect)

        # Astronaut representation
        pygame.draw.circle(self.screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50), 30)
        pygame.draw.circle(self.screen, SPACE_BLUE, (SCREEN_WIDTH // 2 - 10, SCREEN_HEIGHT // 2 - 60), 5)
        pygame.draw.circle(self.screen, SPACE_BLUE, (SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 - 60), 5)

        # Start button
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 60)
        pygame.draw.rect(self.screen, GREEN, button_rect, border_radius=10)
        start_text = self.font_medium.render("INCEPE", True, BLACK)
        start_rect = start_text.get_rect(center=button_rect.center)
        self.screen.blit(start_text, start_rect)

    def draw_exploration(self):
        # Draw stars
        for i in range(100):
            x = (i * 137) % SCREEN_WIDTH
            y = (i * 219) % SCREEN_HEIGHT
            size = (i % 3) + 1
            pygame.draw.circle(self.screen, WHITE, (x, y), size)

        # Draw planets
        for planet in self.planets:
            planet.draw(self.screen, self.font_small)
            if planet.name in self.visited_planets:
                # Draw checkmark
                pygame.draw.circle(self.screen, GREEN, (planet.x + planet.radius, planet.y - planet.radius), 10)

        # Draw astronaut
        self.astronaut.draw(self.screen)

        # Instructions
        inst_text = self.font_small.render("Foloseste sagetile pentru a te misca | SPACE pentru interactiune", True, WHITE)
        self.screen.blit(inst_text, (20, 20))

        # Progress
        progress_text = self.font_small.render(f"Planete exploratе: {len(self.visited_planets)}/8", True, YELLOW)
        self.screen.blit(progress_text, (20, 60))

    def draw_info(self):
        self.screen.fill(SPACE_BLUE)

        if self.current_planet:
            # Planet name
            title = self.font_large.render(self.current_planet.name, True, YELLOW)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(title, title_rect)

            # Planet visual
            pygame.draw.circle(self.screen, self.current_planet.color,
                             (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50),
                             self.current_planet.radius * 2)

            # Info text
            info = self.current_planet.get_info()
            y_offset = SCREEN_HEIGHT // 2 + 100
            for line in info:
                text = self.font_small.render(line, True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
                y_offset += 40

            # Continue prompt
            prompt = self.font_small.render("Apasa orice tasta pentru a continua la quiz...", True, GREEN)
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(prompt, prompt_rect)

    def draw_quiz(self):
        if self.quiz:
            self.quiz.draw(self.screen, self.font_medium, self.font_small)

    def draw_dodge(self):
        if self.dodge_game:
            self.dodge_game.draw(self.screen, self.font_medium, self.font_small)

    def draw_slideshow(self):
        if self.slideshow:
            self.slideshow.draw(self.screen, self.font_medium, self.font_small)

    def draw_notes(self):
        if self.notes:
            self.notes.draw(self.screen, self.font_medium, self.font_small)


class Astronaut:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.speed = 5

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed

        # Keep on screen
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))

    def draw(self, screen):
        # Body
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)
        # Helmet details
        pygame.draw.circle(screen, SPACE_BLUE, (int(self.x - 7), int(self.y - 5)), 3)
        pygame.draw.circle(screen, SPACE_BLUE, (int(self.x + 7), int(self.y - 5)), 3)
        # Smile
        pygame.draw.arc(screen, SPACE_BLUE,
                       (int(self.x - 8), int(self.y - 2), 16, 12),
                       math.pi, 2 * math.pi, 2)


class Planet:
    def __init__(self, name, x, y, radius, color, is_slideshow=False, is_notes=False, has_smiley=False):
        self.name = name
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.is_slideshow = is_slideshow
        self.is_notes = is_notes
        self.has_smiley = has_smiley

    def draw(self, screen, font):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Glow effect
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius + 5, 2)

        # Draw smiley face if enabled
        if self.has_smiley:
            # Eyes
            eye_offset_x = self.radius // 3
            eye_offset_y = self.radius // 4
            eye_size = self.radius // 8
            pygame.draw.circle(screen, BLACK, (self.x - eye_offset_x, self.y - eye_offset_y), eye_size)
            pygame.draw.circle(screen, BLACK, (self.x + eye_offset_x, self.y - eye_offset_y), eye_size)

            # Smile
            smile_rect = pygame.Rect(self.x - self.radius // 2, self.y - self.radius // 4,
                                    self.radius, self.radius)
            pygame.draw.arc(screen, BLACK, smile_rect, math.pi, 2 * math.pi, 4)

        # Name
        text = font.render(self.name, True, WHITE)
        text_rect = text.get_rect(center=(self.x, self.y + self.radius + 20))
        screen.blit(text, text_rect)

    def check_collision(self, astronaut):
        distance = math.sqrt((self.x - astronaut.x) ** 2 + (self.y - astronaut.y) ** 2)
        return distance < self.radius + astronaut.size + 20

    def get_info(self):
        info_dict = {
            "Mercur": [
                "Cea mai apropiata planeta de Soare",
                "Cea mai mica planeta din sistemul solar",
                "Un an dureaza doar 88 de zile pamantesti!",
                "Temperatura suprafetei: -173°C pana la 427°C"
            ],
            "Venus": [
                "A doua planeta de la Soare",
                "Cea mai fierbinte planeta din sistem",
                "Atmosfera densa de dioxid de carbon",
                "O zi este mai lunga decat un an!"
            ],
            "Pamant": [
                "Planeta noastra!",
                "Singura planeta cunoscuta cu viata",
                "71% acoperita cu apa",
                "La distanta perfecta de Soare"
            ],
            "Marte": [
                "Planeta Rosie",
                "Are cel mai mare vulcan: Olympus Mons",
                "Doua luni mici: Phobos si Deimos",
                "Posibila viitoare colonie umana"
            ],
            "Jupiter": [
                "Cea mai mare planeta din sistemul solar",
                "O uriasa gazoasa fara suprafata solida",
                "Celebra Pata Rosie Mare este o furtuna",
                "Are 79 de sateliti cunoscuti!"
            ],
            "Saturn": [
                "Celebra pentru inelele sale frumoase",
                "A doua cea mai mare planeta",
                "Formata in mare parte din hidrogen si heliu",
                "Are 82 de sateliti cunoscuti"
            ],
            "Uranus": [
                "Se roteste pe o parte!",
                "Planeta uriasa de gheata",
                "Cea mai rece atmosfera planetara",
                "Are 13 inele slabe"
            ],
            "Neptun": [
                "Cea mai indepartata planeta de Soare",
                "Cele mai puternice vanturi din sistem",
                "Culoare albastra frumoasa din metan",
                "Are 14 sateliti cunoscuti"
            ]
        }
        return info_dict.get(self.name, ["Informatii indisponibile"])


class Quiz:
    def __init__(self, planet_name):
        self.planet_name = planet_name
        self.questions = self.get_questions(planet_name)
        self.current_question = 0
        self.score = 0
        self.selected_answer = None
        self.answered = False
        self.finished = False

    def get_questions(self, planet_name):
        questions_dict = {
            "Mercur": [
                {"q": "Mercur este planeta _____ de Soare", "a": ["Cea mai apropiata", "Cea mai indepartata", "A doua", "A treia"], "c": 0},
                {"q": "Cat dureaza un an pe Mercur?", "a": ["88 zile", "365 zile", "12 zile", "200 zile"], "c": 0},
                {"q": "Mercur este planeta _____", "a": ["Cea mai mica", "Cea mai mare", "Cea mai fierbinte", "Cea mai rece"], "c": 0},
                {"q": "Are Mercur atmosfera?", "a": ["Foarte subtire", "Densa", "Deloc", "Ca Pamantul"], "c": 0},
                {"q": "Mercur are _____ extreme", "a": ["Temperaturi", "Vanturi", "Ploi", "Nori"], "c": 0}
            ],
            "Venus": [
                {"q": "Venus este _____ planeta de la Soare", "a": ["A doua", "Prima", "A treia", "A patra"], "c": 0},
                {"q": "Venus este planeta _____", "a": ["Cea mai fierbinte", "Cea mai rece", "Cea mai mare", "Cea mai mica"], "c": 0},
                {"q": "Venus are o atmosfera densa de _____", "a": ["CO2", "Oxigen", "Azot", "Hidrogen"], "c": 0},
                {"q": "Pe Venus, o zi este _____ decat un an", "a": ["Mai lunga", "Mai scurta", "La fel", "Dublu"], "c": 0},
                {"q": "Venus poarta numele zeitei _____", "a": ["Iubirii", "Razboiului", "Marii", "Cerului"], "c": 0}
            ],
            "Pamant": [
                {"q": "Pamantul este acoperit _____ cu apa", "a": ["71%", "50%", "30%", "90%"], "c": 0},
                {"q": "Pamantul este _____ planeta de la Soare", "a": ["A treia", "A doua", "A patra", "Prima"], "c": 0},
                {"q": "Pamantul are _____ satelit(i)", "a": ["Unul", "Doi", "Deloc", "Trei"], "c": 0},
                {"q": "Ce face Pamantul special?", "a": ["Are viata", "Cel mai mare", "Cel mai fierbinte", "Cel mai rapid"], "c": 0},
                {"q": "Atmosfera Pamantului este formata din", "a": ["Azot", "Oxigen", "CO2", "Heliu"], "c": 0}
            ],
            "Marte": [
                {"q": "Marte este numita planeta _____", "a": ["Rosie", "Albastra", "Verde", "Galbena"], "c": 0},
                {"q": "Marte are _____ sateliti", "a": ["Doi", "Unu", "Deloc", "Patru"], "c": 0},
                {"q": "Cel mai mare vulcan este _____", "a": ["Olympus Mons", "Mt. Everest", "Krakatoa", "Vesuvius"], "c": 0},
                {"q": "Marte este _____ decat Pamantul", "a": ["Mai mica", "Mai mare", "Aceeasi marime", "De doua ori mai mare"], "c": 0},
                {"q": "Marte ar fi putut avea odata _____", "a": ["Apa", "Doar viata", "Orase", "Copaci"], "c": 0}
            ],
            "Jupiter": [
                {"q": "Jupiter este planeta _____", "a": ["Cea mai mare", "Cea mai mica", "Cea mai fierbinte", "Cea mai apropiata"], "c": 0},
                {"q": "Jupiter este o uriasa _____", "a": ["Gazoasa", "De gheata", "Stancоasa", "Metalica"], "c": 0},
                {"q": "Marea Pata Rosie a lui Jupiter este o", "a": ["Furtuna", "Munte", "Ocean", "Desert"], "c": 0},
                {"q": "Jupiter are aproximativ _____ sateliti", "a": ["79", "1", "12", "200"], "c": 0},
                {"q": "Ai putea sta in picioare pe Jupiter?", "a": ["Nu", "Da", "Poate", "Uneori"], "c": 0}
            ],
            "Saturn": [
                {"q": "Saturn este celebru pentru _____", "a": ["Inele", "Culoare", "Marime", "Viteza"], "c": 0},
                {"q": "Saturn este _____ cea mai mare planeta", "a": ["A doua", "Prima", "A treia", "A patra"], "c": 0},
                {"q": "Saturn este format in mare parte din _____", "a": ["Hidrogen", "Piatra", "Apa", "Fier"], "c": 0},
                {"q": "Saturn are _____ sateliti", "a": ["82", "1", "10", "5"], "c": 0},
                {"q": "Saturn este o uriasa _____", "a": ["Gazoasa", "De gheata", "Stancоasa", "Metalica"], "c": 0}
            ],
            "Uranus": [
                {"q": "Uranus se roteste pe _____", "a": ["O parte", "Varful", "Normal", "Baza"], "c": 0},
                {"q": "Uranus este o uriasa de _____", "a": ["Gheata", "Gaz", "Piatra", "Metal"], "c": 0},
                {"q": "Uranus are _____ inele", "a": ["13", "0", "1", "100"], "c": 0},
                {"q": "Uranus are cea mai rece _____", "a": ["Atmosfera", "Nucleu", "Inele", "Sateliti"], "c": 0},
                {"q": "Ce culoare este Uranus?", "a": ["Albastru-verde", "Rosu", "Galben", "Violet"], "c": 0}
            ],
            "Neptun": [
                {"q": "Neptun este planeta _____ de Soare", "a": ["Cea mai indepartata", "Cea mai apropiata", "A doua", "A treia"], "c": 0},
                {"q": "Neptun are cele mai puternice _____", "a": ["Vanturi", "Inele", "Gravitatie", "Caldura"], "c": 0},
                {"q": "Culoarea albastra a lui Neptun vine de la", "a": ["Metan", "Apa", "Gheata", "Nori"], "c": 0},
                {"q": "Neptun are _____ sateliti", "a": ["14", "1", "0", "100"], "c": 0},
                {"q": "Neptun este o uriasa de _____", "a": ["Gheata", "Gaz", "Piatra", "Foc"], "c": 0}
            ]
        }
        return questions_dict.get(planet_name, [])

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.answered:
            mouse_pos = pygame.mouse.get_pos()
            # Check which answer was clicked
            for i in range(4):
                answer_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, 300 + i * 70, 600, 50)
                if answer_rect.collidepoint(mouse_pos):
                    self.selected_answer = i
                    self.answered = True
                    if i == self.questions[self.current_question]["c"]:
                        self.score += 1
                    break

        elif event.type == pygame.KEYDOWN and self.answered:
            self.current_question += 1
            self.answered = False
            self.selected_answer = None
            if self.current_question >= 5:
                self.finished = True

    def draw(self, screen, font_medium, font_small):
        screen.fill(SPACE_BLUE)

        if self.current_question < 5:
            question = self.questions[self.current_question]

            # Question number
            q_num = font_medium.render(f"Intrebarea {self.current_question + 1}/5", True, YELLOW)
            screen.blit(q_num, (SCREEN_WIDTH // 2 - q_num.get_width() // 2, 100))

            # Question text
            q_text = font_small.render(question["q"], True, WHITE)
            screen.blit(q_text, (SCREEN_WIDTH // 2 - q_text.get_width() // 2, 200))

            # Answer options
            for i, answer in enumerate(question["a"]):
                answer_rect = pygame.Rect(SCREEN_WIDTH // 2 - 300, 300 + i * 70, 600, 50)

                if self.answered:
                    if i == question["c"]:
                        color = GREEN
                    elif i == self.selected_answer:
                        color = RED
                    else:
                        color = (100, 100, 100)
                else:
                    color = (50, 50, 150)

                pygame.draw.rect(screen, color, answer_rect, border_radius=10)
                pygame.draw.rect(screen, WHITE, answer_rect, 2, border_radius=10)

                a_text = font_small.render(answer, True, WHITE)
                screen.blit(a_text, (answer_rect.centerx - a_text.get_width() // 2,
                                    answer_rect.centery - a_text.get_height() // 2))

            if self.answered:
                prompt = font_small.render("Apasa orice tasta pentru a continua...", True, YELLOW)
                screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 650))

        # Score
        score_text = font_small.render(f"Scor: {self.score}/5", True, YELLOW)
        screen.blit(score_text, (20, 20))


class DodgeGame:
    def __init__(self):
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT - 100
        self.player_size = 25
        self.speed = 7
        self.asteroids = []
        self.spawn_timer = 0
        self.spawn_rate = 30
        self.time_survived = 0
        self.finished = False
        self.won = False
        self.duration = 1800  # 30 seconds at 60 FPS

    def handle_event(self, event):
        pass

    def update(self):
        if self.finished:
            return

        # Move player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.player_x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.player_x += self.speed

        self.player_x = max(self.player_size, min(SCREEN_WIDTH - self.player_size, self.player_x))

        # Spawn asteroids
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_rate:
            self.spawn_timer = 0
            x = random.randint(20, SCREEN_WIDTH - 20)
            size = random.randint(15, 35)
            speed = random.uniform(3, 7)
            self.asteroids.append({"x": x, "y": -20, "size": size, "speed": speed})

        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid["y"] += asteroid["speed"]

            # Check collision with player
            distance = math.sqrt((asteroid["x"] - self.player_x) ** 2 +
                               (asteroid["y"] - self.player_y) ** 2)
            if distance < asteroid["size"] + self.player_size:
                self.finished = True
                self.won = False
                return

            # Remove off-screen asteroids
            if asteroid["y"] > SCREEN_HEIGHT + 50:
                self.asteroids.remove(asteroid)

        # Check win condition
        self.time_survived += 1
        if self.time_survived >= self.duration:
            self.finished = True
            self.won = True

    def draw(self, screen, font_medium, font_small):
        screen.fill(SPACE_BLUE)

        # Draw stars
        for i in range(100):
            x = (i * 137) % SCREEN_WIDTH
            y = (i * 219 + self.time_survived) % SCREEN_HEIGHT
            size = (i % 3) + 1
            pygame.draw.circle(screen, WHITE, (x, y), size)

        if not self.finished:
            # Draw player
            pygame.draw.circle(screen, WHITE, (int(self.player_x), int(self.player_y)),
                             self.player_size)
            pygame.draw.circle(screen, SPACE_BLUE,
                             (int(self.player_x - 8), int(self.player_y - 5)), 4)
            pygame.draw.circle(screen, SPACE_BLUE,
                             (int(self.player_x + 8), int(self.player_y - 5)), 4)

            # Draw asteroids
            for asteroid in self.asteroids:
                pygame.draw.circle(screen, (139, 69, 19),
                                 (int(asteroid["x"]), int(asteroid["y"])),
                                 asteroid["size"])
                pygame.draw.circle(screen, (101, 67, 33),
                                 (int(asteroid["x"]), int(asteroid["y"])),
                                 asteroid["size"], 3)

            # Timer
            time_left = (self.duration - self.time_survived) // 60
            timer_text = font_medium.render(f"Timp: {time_left}s", True, YELLOW)
            screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 20))

            # Instructions
            inst = font_small.render("Foloseste sagetile STANGA/DREAPTA pentru a evita!", True, WHITE)
            screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 70))
        else:
            if self.won:
                result = font_medium.render("FELICITARI!", True, GREEN)
                msg = font_small.render("Ai evitat toti asteroizii!", True, WHITE)
            else:
                result = font_medium.render("LOVIT DE ASTEROID!", True, RED)
                msg = font_small.render("Mai mult noroc data viitoare!", True, WHITE)

            screen.blit(result, (SCREEN_WIDTH // 2 - result.get_width() // 2,
                               SCREEN_HEIGHT // 2 - 50))
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2,
                            SCREEN_HEIGHT // 2 + 20))

            cont = font_small.render("Apasa orice tasta pentru a continua...", True, YELLOW)
            screen.blit(cont, (SCREEN_WIDTH // 2 - cont.get_width() // 2,
                             SCREEN_HEIGHT // 2 + 100))


class Slideshow:
    def __init__(self):
        self.current_slide = 0
        self.closed = False
        self.images = []

        # Load images from pics/ folder using PIL/Pillow
        for i in range(1, 5):
            try:
                # Load image using PIL
                pil_image = Image.open(f"pics/{i}.png")
                print(f"Loaded image {i} with PIL: {pil_image.size}")

                # Convert PIL image to RGB mode (remove alpha channel if present)
                if pil_image.mode == 'RGBA':
                    # Create white background
                    background = Image.new('RGB', pil_image.size, (255, 255, 255))
                    background.paste(pil_image, mask=pil_image.split()[3])  # Use alpha channel as mask
                    pil_image = background
                elif pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')

                # Scale image to fit screen while maintaining aspect ratio
                img_width, img_height = pil_image.size
                scale_factor = min((SCREEN_WIDTH - 200) / img_width,
                                 (SCREEN_HEIGHT - 200) / img_height)
                new_width = int(img_width * scale_factor)
                new_height = int(img_height * scale_factor)
                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)

                # Convert PIL image to pygame surface
                mode = pil_image.mode
                size = pil_image.size
                data = pil_image.tobytes()
                img = pygame.image.fromstring(data, size, mode)

                self.images.append(img)
                print(f"Converted image {i} to pygame surface: {new_width}x{new_height}")
            except Exception as e:
                print(f"Error loading image {i}: {e}")
                import traceback
                traceback.print_exc()
                # Create placeholder if image fails to load
                placeholder = pygame.Surface((600, 400))
                placeholder.fill((100, 100, 100))
                self.images.append(placeholder)

        print(f"Total images loaded: {len(self.images)}")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check X button (top right)
            x_button_rect = pygame.Rect(SCREEN_WIDTH - 60, 10, 50, 50)
            if x_button_rect.collidepoint(mouse_pos):
                self.closed = True
                return

            # Check Previous button
            if self.current_slide > 0:
                prev_button_rect = pygame.Rect(50, SCREEN_HEIGHT - 80, 150, 60)
                if prev_button_rect.collidepoint(mouse_pos):
                    self.current_slide -= 1
                    return

            # Check Next button
            if self.current_slide < len(self.images) - 1:
                next_button_rect = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 150, 60)
                if next_button_rect.collidepoint(mouse_pos):
                    self.current_slide += 1
                    return

    def draw(self, screen, font_medium, font_small):
        screen.fill(SPACE_BLUE)

        # Draw current image
        if self.current_slide < len(self.images) and self.images:
            img = self.images[self.current_slide]
            img_rect = img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(img, img_rect)
        else:
            # Debug: show if no images
            debug_text = font_small.render(f"No images loaded ({len(self.images)} total)", True, RED)
            screen.blit(debug_text, (SCREEN_WIDTH // 2 - debug_text.get_width() // 2, SCREEN_HEIGHT // 2))

        # Draw X button (top right)
        x_button_rect = pygame.Rect(SCREEN_WIDTH - 60, 10, 50, 50)
        pygame.draw.rect(screen, RED, x_button_rect, border_radius=5)
        x_text = font_medium.render("X", True, WHITE)
        x_text_rect = x_text.get_rect(center=x_button_rect.center)
        screen.blit(x_text, x_text_rect)

        # Draw Previous button
        if self.current_slide > 0:
            prev_button_rect = pygame.Rect(50, SCREEN_HEIGHT - 80, 150, 60)
            pygame.draw.rect(screen, GREEN, prev_button_rect, border_radius=10)
            prev_text = font_small.render("< Inapoi", True, BLACK)
            prev_text_rect = prev_text.get_rect(center=prev_button_rect.center)
            screen.blit(prev_text, prev_text_rect)

        # Draw Next button
        if self.current_slide < len(self.images) - 1:
            next_button_rect = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 80, 150, 60)
            pygame.draw.rect(screen, GREEN, next_button_rect, border_radius=10)
            next_text = font_small.render("Inainte >", True, BLACK)
            next_text_rect = next_text.get_rect(center=next_button_rect.center)
            screen.blit(next_text, next_text_rect)

        # Draw slide counter
        counter_text = font_small.render(f"{self.current_slide + 1} / {len(self.images)}", True, YELLOW)
        screen.blit(counter_text, (SCREEN_WIDTH // 2 - counter_text.get_width() // 2, 20))


class Notes:
    def __init__(self):
        self.closed = False
        self.notes_file = "student_notes.json"
        self.notes = self.load_notes()
        self.current_note = ""
        self.input_active = False
        self.scroll_offset = 0
        self.max_note_length = 200

    def load_notes(self):
        """Load notes from JSON file"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_notes(self):
        """Save notes to JSON file"""
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving notes: {e}")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()

            # Check X button (top right)
            x_button_rect = pygame.Rect(SCREEN_WIDTH - 60, 10, 50, 50)
            if x_button_rect.collidepoint(mouse_pos):
                self.closed = True
                return

            # Check if clicking on input box
            input_rect = pygame.Rect(50, SCREEN_HEIGHT - 180, SCREEN_WIDTH - 100, 100)
            if input_rect.collidepoint(mouse_pos):
                self.input_active = True
            else:
                self.input_active = False

            # Check Add Note button
            if self.input_active or self.current_note:
                add_button_rect = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 70, 150, 50)
                if add_button_rect.collidepoint(mouse_pos) and self.current_note.strip():
                    self.notes.append(self.current_note.strip())
                    self.save_notes()
                    self.current_note = ""
                    self.input_active = False

            # Check scroll buttons
            if len(self.notes) > 5:
                # Scroll up
                if self.scroll_offset > 0:
                    scroll_up_rect = pygame.Rect(SCREEN_WIDTH - 60, 100, 40, 40)
                    if scroll_up_rect.collidepoint(mouse_pos):
                        self.scroll_offset -= 1

                # Scroll down
                if self.scroll_offset < len(self.notes) - 5:
                    scroll_down_rect = pygame.Rect(SCREEN_WIDTH - 60, SCREEN_HEIGHT - 250, 40, 40)
                    if scroll_down_rect.collidepoint(mouse_pos):
                        self.scroll_offset += 1

        elif event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_RETURN:
                # Add note on Enter
                if self.current_note.strip():
                    self.notes.append(self.current_note.strip())
                    self.save_notes()
                    self.current_note = ""
                    self.input_active = False
            elif event.key == pygame.K_BACKSPACE:
                self.current_note = self.current_note[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.input_active = False
            else:
                # Add character if not too long
                if len(self.current_note) < self.max_note_length:
                    if event.unicode.isprintable():
                        self.current_note += event.unicode

    def draw(self, screen, font_medium, font_small):
        screen.fill(SPACE_BLUE)

        # Title
        title = font_medium.render("NOTITE", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        # Draw X button (top right)
        x_button_rect = pygame.Rect(SCREEN_WIDTH - 60, 10, 50, 50)
        pygame.draw.rect(screen, RED, x_button_rect, border_radius=5)
        x_text = font_medium.render("X", True, WHITE)
        x_text_rect = x_text.get_rect(center=x_button_rect.center)
        screen.blit(x_text, x_text_rect)

        # Draw previous notes area
        notes_area_rect = pygame.Rect(50, 90, SCREEN_WIDTH - 120, SCREEN_HEIGHT - 300)
        pygame.draw.rect(screen, (30, 30, 60), notes_area_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, notes_area_rect, 2, border_radius=10)

        # Display notes
        if self.notes:
            y_offset = 110
            visible_notes = self.notes[self.scroll_offset:self.scroll_offset + 5]
            for i, note in enumerate(visible_notes):
                # Wrap text if too long
                max_width = SCREEN_WIDTH - 180
                words = note.split(' ')
                lines = []
                current_line = ""

                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    test_surface = font_small.render(test_line, True, WHITE)
                    if test_surface.get_width() <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)

                # Draw note lines
                for line in lines[:2]:  # Max 2 lines per note
                    note_text = font_small.render(f"• {line}", True, WHITE)
                    screen.blit(note_text, (70, y_offset))
                    y_offset += 40

                y_offset += 10  # Space between notes
        else:
            no_notes_text = font_small.render("Nu exista notite inca. Adauga una mai jos!", True, (150, 150, 150))
            screen.blit(no_notes_text, (SCREEN_WIDTH // 2 - no_notes_text.get_width() // 2, 200))

        # Draw scroll indicators
        if len(self.notes) > 5:
            if self.scroll_offset > 0:
                scroll_up_rect = pygame.Rect(SCREEN_WIDTH - 60, 100, 40, 40)
                pygame.draw.rect(screen, GREEN, scroll_up_rect, border_radius=5)
                up_text = font_small.render("^", True, BLACK)
                screen.blit(up_text, (scroll_up_rect.centerx - up_text.get_width() // 2,
                                     scroll_up_rect.centery - up_text.get_height() // 2))

            if self.scroll_offset < len(self.notes) - 5:
                scroll_down_rect = pygame.Rect(SCREEN_WIDTH - 60, SCREEN_HEIGHT - 250, 40, 40)
                pygame.draw.rect(screen, GREEN, scroll_down_rect, border_radius=5)
                down_text = font_small.render("v", True, BLACK)
                screen.blit(down_text, (scroll_down_rect.centerx - down_text.get_width() // 2,
                                       scroll_down_rect.centery - down_text.get_height() // 2))

        # Draw input box
        input_rect = pygame.Rect(50, SCREEN_HEIGHT - 180, SCREEN_WIDTH - 100, 100)
        input_color = (50, 50, 100) if self.input_active else (30, 30, 60)
        pygame.draw.rect(screen, input_color, input_rect, border_radius=10)
        border_color = YELLOW if self.input_active else WHITE
        pygame.draw.rect(screen, border_color, input_rect, 3, border_radius=10)

        # Draw current note text
        if self.current_note or self.input_active:
            note_text = font_small.render(self.current_note, True, WHITE)
            screen.blit(note_text, (70, SCREEN_HEIGHT - 160))
        else:
            placeholder = font_small.render("Click aici pentru a scrie o notita...", True, (100, 100, 100))
            screen.blit(placeholder, (70, SCREEN_HEIGHT - 160))

        # Character counter
        counter = font_small.render(f"{len(self.current_note)}/{self.max_note_length}", True, (150, 150, 150))
        screen.blit(counter, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100))

        # Draw Add button
        add_button_rect = pygame.Rect(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 70, 150, 50)
        button_color = GREEN if self.current_note.strip() else (100, 100, 100)
        pygame.draw.rect(screen, button_color, add_button_rect, border_radius=10)
        add_text = font_small.render("Adauga", True, BLACK if self.current_note.strip() else (50, 50, 50))
        add_text_rect = add_text.get_rect(center=add_button_rect.center)
        screen.blit(add_text, add_text_rect)

        # Instructions
        inst = font_small.render(f"Total notite: {len(self.notes)}", True, YELLOW)
        screen.blit(inst, (50, SCREEN_HEIGHT - 70))


if __name__ == "__main__":
    game = Game()
    game.run()
