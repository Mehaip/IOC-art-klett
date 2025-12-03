# Sa invatam planetele - Joc Educational

Un joc educational pentru tablete, conceput pentru copiii de scoala sa invete despre planete si univers.

(English: Educational game for tablets designed for school kids to learn about planets and the universe.)

## Features

- **Main Menu**: Start screen with astronaut character
- **Exploration Mode**: Top-down movement (like Undertale) through a universe with planets
- **Planet Information**: Interactive learning with facts about each planet
- **Quiz System**: 5-question quiz for each planet
- **Dodge Game**: Fun asteroid dodging mini-game as a reward for perfect quiz scores
- **Progress Tracking**: Track which planets have been explored

## Installation

1. Make sure you have Python 3.7+ installed
2. Install required dependencies:
```bash
pip install pygame pillow
```

**Note**: If you're using Python 3.14+, there's a known circular import bug in pygame 2.6.1. This game uses PIL/Pillow as a workaround for font rendering.

## How to Run

```bash
python main.py
```

## Controls

### Menu
- **Mouse Click** on START button to begin

### Exploration Mode
- **Arrow Keys**: Move astronaut up, down, left, right
- **SPACE**: Interact with nearby planets

### Quiz Mode
- **Mouse Click**: Select answers

### Dodge Game
- **LEFT/RIGHT Arrow Keys**: Move to dodge asteroids

## Game Flow

1. Start at the main menu
2. Explore the universe and approach planets
3. Press SPACE when near a planet to learn about it
4. Read the planetary information
5. Take a 5-question quiz
6. If you score 5/5, play the dodge game (30 seconds)
7. Continue exploring other planets

## Educational Content / Continut Educational

The game includes information and quizzes about all 8 planets (in Romanian):
- Mercur (Mercury)
- Venus
- Pamant (Earth)
- Marte (Mars)
- Jupiter
- Saturn
- Uranus
- Neptun (Neptune)

**Note**: All game text, planet information, and quiz questions are in Romanian, created with reference to the ArtKlett educational manual.

## Customization

You can easily customize:
- Planet positions in `create_planets()` method
- Quiz questions in the `Quiz.get_questions()` method
- Planet information in `Planet.get_info()` method
- Game difficulty (asteroid speed, quiz time, etc.)

## For Teachers

This game is designed to make learning about space fun and engaging. Students must:
1. Read information about each planet
2. Answer quiz questions correctly
3. Stay engaged with the fun dodge game reward

The game tracks progress so students can see which planets they've completed.
