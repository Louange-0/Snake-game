import pygame
import serial
import sys
import random

pygame.init()

# Set up the game window
window_size = (800, 600)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Snake Game")

# Load the background image
background_image = pygame.image.load("bg.jpg").convert()
background_image = pygame.transform.scale(background_image, window_size)

# Load the eat sound effect
eat_sound = pygame.mixer.Sound("eat_sound.wav")

# Load or create the highscore file
try:
    with open("highscore.txt", "r") as file:
        highscore = int(file.read())
except FileNotFoundError:
    highscore = 0

# Game variables
snake_size = 20
snake_color = (0, 255, 0)
snake_segments = [(400, 300)]
snake_direction = 'RIGHT'  # Initialize snake direction
snake_speed = 15
snake_length = 1

food_size = 20
food_color = (255, 0, 0)
food_pos = (random.randrange(1, window_size[0] // food_size) * food_size,
            random.randrange(1, window_size[1] // food_size) * food_size)

score = 0
game_over = False

# Initialize serial communication with Arduino
try:
    arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Use the correct serial port
except serial.SerialException:
    print("Error: Could not open port. Make sure the Arduino is connected and not in use by another program.")
    pygame.quit()
    sys.exit()

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

    # Read joystick values from Arduino input
    arduino_data = arduino.readline().decode('ascii', errors='ignore').strip()

    if arduino_data:
        try:
            # Split the data if it contains a comma, otherwise use the entire data as the value for joy_x
            if ',' in arduino_data:
                joy_x, joy_y = map(int, arduino_data.split(','))  # Split X and Y values
            else:
                joy_x = int(arduino_data)
                joy_y = 0  # Set joy_y to 0 or any default value as needed

            # Use joy_x and joy_y to control snake's movement
            # For example, map X and Y values to snake's direction
            if joy_x > 600:
                snake_direction = 'RIGHT'
            elif joy_x < 400:
                snake_direction = 'LEFT'
            elif joy_y > 600:
                snake_direction = 'DOWN'
            elif joy_y < 400:
                snake_direction = 'UP'
        except ValueError:
            print("Data received from Arduino:", arduino_data)
            continue

    # Update snake's position based on its direction and speed
    head_x, head_y = snake_segments[0]
    if snake_direction == 'UP':
        head_y -= snake_size
    elif snake_direction == 'DOWN':
        head_y += snake_size
    elif snake_direction == 'LEFT':
        head_x -= snake_size
    elif snake_direction == 'RIGHT':
        head_x += snake_size

    # Insert new head segment at the beginning of the snake_segments list
    snake_segments.insert(0, (head_x, head_y))

    # Remove the tail segment if snake length exceeds the limit
    if len(snake_segments) > snake_length:
        snake_segments.pop()

    # Check for collisions (snake colliding with food)
    if snake_segments[0] == food_pos:
        score += 10
        eat_sound.play()  # Play the eat sound effect
        food_pos = (random.randrange(1, window_size[0] // food_size) * food_size,
                    random.randrange(1, window_size[1] // food_size) * food_size)
        snake_length += 1

    # Check for collisions (snake colliding with itself)
    # if snake_segments[0] in snake_segments[1:]:
    #     game_over = True

    # Check if the snake hits the screen boundaries
    if head_x < 0 or head_x >= window_size[0] or head_y < 0 or head_y >= window_size[1]:
        game_over = True

    # Clear the screen with background image
    window.blit(background_image, (0, 0))

    # Draw snake segments
    for segment in snake_segments:
        pygame.draw.rect(window, snake_color, pygame.Rect(segment[0], segment[1], snake_size, snake_size))

    # Draw food
    pygame.draw.rect(window, food_color, pygame.Rect(food_pos[0], food_pos[1], food_size, food_size))

    pygame.display.flip()  # Update the display
    pygame.time.Clock().tick(snake_speed)  # Control the game's frame rate

# Update the highscore if the current score is higher
if score > highscore:
    highscore = score

# Save the highscore to the file
with open("highscore.txt", "w") as file:
    file.write(str(highscore))

# Game over screen
font = pygame.font.SysFont(None, 36)
game_over_text = font.render("Game Over - Score: " + str(score) + " - Highscore: " + str(highscore), True, (255, 255, 000))
window.blit(game_over_text, (window_size[0] // 2 - game_over_text.get_width() // 2,
                             window_size[1] // 2 - game_over_text.get_height() // 2))
pygame.display.flip()

# Wait for a few seconds before exiting
pygame.time.wait(3000)

pygame.quit()
sys.exit()
