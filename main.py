import pygame
import sys
import random
from collections import deque

# --- Configuration ---
TILE_SIZE = 30
COLS, ROWS = 21, 15
SCREEN_WIDTH = COLS * TILE_SIZE
SCREEN_HEIGHT = ROWS * TILE_SIZE
FPS = 60

# Colors
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
PLAYER_COLOR, GOAL_COLOR, WALL_COLOR = (
    52, 152, 219), (46, 204, 113), (44, 62, 80)
PATH_COLOR = (200, 90, 90)


def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def walk(x, y):
        maze[y][x] = 0
        dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                walk(nx, ny)
    walk(1, 1)
    maze[height-2][width-2] = "G"
    return maze


def solve_bfs(maze, start, goal_val="G"):
    """Finds the shortest path from start to goal using BFS."""
    start_pos = (start[0] // TILE_SIZE, start[1] // TILE_SIZE)
    queue = deque([(start_pos, [])])
    visited = {start_pos}

    while queue:
        (x, y), path = queue.popleft()

        if maze[y][x] == goal_val:
            return path + [(x, y)]

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 1 and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append(((nx, ny), path + [(x, y)]))
    return []


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(
            x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def move(self, dx, dy, MAZE):
        new_x = self.rect.x + dx * TILE_SIZE
        new_y = self.rect.y + dy * TILE_SIZE
        grid_x, grid_y = new_x // TILE_SIZE, new_y // TILE_SIZE
        if 0 <= grid_x < COLS and 0 <= grid_y < ROWS:
            if MAZE[grid_y][grid_x] != 1:
                self.rect.x, self.rect.y = new_x, new_y

    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, self.rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Maze Solver - Press 'A' to Solve")
    clock = pygame.time.Clock()
    player = Player(1, 1)
    font = pygame.font.SysFont("Arial", 32)
    MAZE = generate_maze(COLS, ROWS)

    vx, vy = 0, 0
    dt = 0
    timer = 0

    auto_path = []
    is_auto = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    vy = -1
                elif event.key == pygame.K_DOWN:
                    vy = 1
                elif event.key == pygame.K_LEFT:
                    vx = -1
                elif event.key == pygame.K_RIGHT:
                    vx = 1
                elif event.key == pygame.K_a:  # Automation Key
                    auto_path = solve_bfs(MAZE, (player.rect.x, player.rect.y))
                    is_auto = not is_auto

            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    vy = 0
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    vx = 0

        timer += dt
        if timer >= 100:
            if is_auto and auto_path:
                # Agent moves to the next spot in the path
                next_step = auto_path.pop(0)
                player.rect.x = next_step[0] * TILE_SIZE
                player.rect.y = next_step[1] * TILE_SIZE
                if not auto_path:
                    is_auto = False
            else:
                player.move(vx, vy, MAZE)
            timer -= 100

        # Win Condition
        gx, gy = player.rect.x // TILE_SIZE, player.rect.y // TILE_SIZE
        if MAZE[gy][gx] == "G":
            is_auto = False
            win_screen = True
            while win_screen:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        MAZE = generate_maze(COLS, ROWS)
                        player = Player(1, 1)
                        win_screen = False
                screen.fill((44, 62, 80))
                text = font.render("YOU WIN!",
                                   True, (200, 200, 200))
                t_rect = text.get_rect()
                screen.blit(text, (SCREEN_WIDTH//2 -
                            t_rect.center[0], SCREEN_HEIGHT//2 - t_rect.center[1]))
                pygame.display.flip()

        # Draw
        screen.fill(WHITE)
        for r in range(ROWS):
            for c in range(COLS):
                tile = MAZE[r][c]
                rect = (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == 1:
                    pygame.draw.rect(screen, WALL_COLOR, rect)
                elif tile == "G":
                    pygame.draw.rect(screen, GOAL_COLOR, rect)

        # Optional: Draw the path the agent is following
        if is_auto:
            for step in auto_path:
                p_rect = (step[0]*TILE_SIZE + 10, step[1]
                          * TILE_SIZE + 10, 10, 10)
                pygame.draw.rect(screen, PATH_COLOR, p_rect)

        player.draw(screen)
        pygame.display.flip()
        dt = clock.tick(FPS)


if __name__ == "__main__":
    main()
