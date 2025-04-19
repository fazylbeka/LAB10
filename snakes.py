import psycopg2
import pygame
import random
import sys
import time

# CONSTANTS
WIDTH = 640
HEIGHT = 640
PIXELS = 32
SQUARES_X = WIDTH // PIXELS
SQUARES_Y = HEIGHT // PIXELS

# COLORS
BG1 = (156, 210, 54)
BG2 = (147, 203, 57)
RED = (255, 0, 0)
BLUE = (0, 0, 50)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Food types
FOOD_TYPES = [
    {"color": RED, "points": 1, "lifetime": 5},
    {"color": YELLOW, "points": 2, "lifetime": 3},
    {"color": PURPLE, "points": 3, "lifetime": 2}
]

def connect_db():
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="Biba2006",
        host="localhost",
        port="5432",
        options="-c client_encoding=UTF8"
    )
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            level INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_score (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            score INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

class Background:
    def draw(self, surface):
        surface.fill(BG1)
        counter = 0
        for row in range(SQUARES_Y):
            for col in range(SQUARES_X):
                if counter % 2 == 0:
                    pygame.draw.rect(surface, BG2, (col * PIXELS, row * PIXELS, PIXELS, PIXELS))
                if col != SQUARES_X - 1:
                    counter += 1

class Snake:
    def __init__(self):
        self.color = BLUE
        self.headX = random.randrange(0, WIDTH, PIXELS)
        self.headY = random.randrange(0, HEIGHT, PIXELS)
        self.bodies = []
        self.state = "STOP"

    def move_head(self):
        if self.state == "UP":
            self.headY -= PIXELS
        elif self.state == "DOWN":
            self.headY += PIXELS
        elif self.state == "RIGHT":
            self.headX += PIXELS
        elif self.state == "LEFT":
            self.headX -= PIXELS

    def move_body(self):
        if self.bodies:
            for i in range(len(self.bodies) - 1, 0, -1):
                self.bodies[i].posX = self.bodies[i - 1].posX
                self.bodies[i].posY = self.bodies[i - 1].posY
            self.bodies[0].posX = self.headX
            self.bodies[0].posY = self.headY

    def add_body(self):
        body = Body(self.headX, self.headY)
        self.bodies.append(body)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.headX, self.headY, PIXELS, PIXELS))
        for body in self.bodies:
            body.draw(surface)

    def die(self):
        self.__init__()

class Body:
    def __init__(self, posX, posY):
        self.color = BLUE
        self.posX = posX
        self.posY = posY

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.posX, self.posY, PIXELS, PIXELS))

class Food:
    def __init__(self):
        self.spawn()

    def spawn(self):
        food_type = random.choice(FOOD_TYPES)
        self.color = food_type["color"]
        self.points = food_type["points"]
        self.lifetime = food_type["lifetime"]
        self.spawn_time = time.time()
        self.posX = random.randrange(0, WIDTH, PIXELS)
        self.posY = random.randrange(0, HEIGHT, PIXELS)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.posX, self.posY, PIXELS, PIXELS))

    def expired(self):
        return time.time() - self.spawn_time > self.lifetime

class Collision:
    def between_snake_and_food(self, snake, food):
        return snake.headX == food.posX and snake.headY == food.posY

    def between_snake_and_walls(self, snake):
        return snake.headX < 0 or snake.headX >= WIDTH or snake.headY < 0 or snake.headY >= HEIGHT

    def between_head_and_body(self, snake):
        return any(snake.headX == body.posX and snake.headY == body.posY for body in snake.bodies)

class Score:
    def __init__(self):
        self.points = 0
        self.font = pygame.font.SysFont('monospace', 30, bold=False)

    def increase(self, points):
        self.points += points

    def reset(self):
        self.points = 0

    def show(self, surface):
        lbl = self.font.render(f'Score: {self.points}', 1, BLACK)
        surface.blit(lbl, (5, 5))

def main():
    create_tables()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SNAKE")

    username = input("Enter your username: ")

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, level FROM users WHERE username = %s', (username,))
    user = cursor.fetchone()

    if user:
        print(f"Welcome back, {username}! Current level: {user[1]}")
        user_id = user[0]
    else:
        cursor.execute('INSERT INTO users (username, level) VALUES (%s, %s) RETURNING id', (username, 1))
        user_id = cursor.fetchone()[0]
        conn.commit()
        print(f"Welcome, {username}! Your account has been created.")

    conn.close()

    snake = Snake()
    food = Food()
    background = Background()
    collision = Collision()
    score = Score()
    speed = 130

    while True:
        background.draw(screen)
        snake.draw(screen)
        food.draw(screen)
        score.show(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.state != "DOWN":
                    snake.state = "UP"
                elif event.key == pygame.K_DOWN and snake.state != "UP":
                    snake.state = "DOWN"
                elif event.key == pygame.K_RIGHT and snake.state != "LEFT":
                    snake.state = "RIGHT"
                elif event.key == pygame.K_LEFT and snake.state != "RIGHT":
                    snake.state = "LEFT"
                elif event.key == pygame.K_p:
                    print("Game paused. Press any key to resume.")
                    pygame.time.wait(5000)
                    continue

        if collision.between_snake_and_food(snake, food):
            snake.add_body()
            score.increase(food.points)
            food.spawn()

        if food.expired():
            food.spawn()

        if snake.state != "STOP":
            snake.move_body()
            snake.move_head()

        if collision.between_snake_and_walls(snake) or collision.between_head_and_body(snake):
            conn = connect_db()
            cur = conn.cursor()
            cur.execute('INSERT INTO user_score (user_id, score) VALUES (%s, %s)', (user_id, score.points))
            conn.commit()
            conn.close()

            snake.die()
            score.reset()
            food.spawn()

        pygame.time.delay(speed)
        pygame.display.update()

main()