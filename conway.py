"""
A Python + PyGame implementation of Conway's Game of Life.
https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life
"""
import sys
from typing import List, Tuple

import pygame

BLACK = (0x00, 0x00, 0x00)
WHITE = (0xFF, 0xFF, 0xFF)

VIEWPORT_WIDTH = 1000
VIEWPORT_HEIGHT = 1000
GRID_WIDTH = 50
GRID_HEIGHT = 50

TILE_WIDTH = VIEWPORT_WIDTH // GRID_WIDTH
TILE_HEIGHT = VIEWPORT_HEIGHT // GRID_HEIGHT


def get_living_neighbours(grid: List[List[bool]], pos: Tuple[int, int]) -> int:
    """
    Get the number of True values immediately surrounding a point on a grid.
    Includes diagonals, but not the provided position itself.
    """
    count = 0
    for y_offset in range(-1, 2):
        for x_offset in range(-1, 2):
            # Don't check the current cell position
            if ((y_offset != 0 or x_offset != 0)
                    and 0 <= pos[1] + y_offset < len(grid)
                    and 0 <= pos[0] + x_offset < len(grid[0])):
                # Converting bool to int gives either 0 or 1
                count += int(grid[pos[1] + y_offset][pos[0] + x_offset])
    return count


def get_new_state(grid: List[List[bool]], pos: Tuple[int, int]) -> bool:
    """
    Get whether a position on a grid should be alive or dead in the next tick.
    """
    current_state = grid[pos[1]][pos[0]]
    living_neighbours = get_living_neighbours(grid, pos)
    return (
        living_neighbours in (2, 3)
        if current_state else
        living_neighbours == 3
    )


def main() -> None:
    """
    Main function for the game. Renders the grid, handles input, and performs
    each tick where applicable.
    """
    pygame.init()
    screen = pygame.display.set_mode((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
    pygame.display.set_caption("Conway's Game of Life - Stopped 1t/100ms")
    clock = pygame.time.Clock()
    life_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    perform_ticks = False
    tick_interval = 100
    since_last_tick = 0
    # Main game loop
    while True:
        frame_time = clock.tick()
        since_last_tick += frame_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Flip bool value
                    perform_ticks ^= True
                elif event.key == pygame.K_DOWN and tick_interval > 10:
                    tick_interval -= 10
                elif event.key == pygame.K_UP:
                    tick_interval += 10
                elif event.key == pygame.K_r:
                    life_grid = [
                        [False] * GRID_WIDTH for _ in range(GRID_HEIGHT)
                    ]
                pygame.display.set_caption(
                    f"Conway's Game of Life - Running 1t/{tick_interval}ms"
                    if perform_ticks else
                    f"Conway's Game of Life - Stopped 1t/{tick_interval}ms"
                )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    mouse_pos = pygame.mouse.get_pos()
                    grid_pos = (
                        mouse_pos[0] // TILE_WIDTH,
                        mouse_pos[1] // TILE_HEIGHT
                    )
                    # Flip bool value of tile
                    life_grid[grid_pos[1]][grid_pos[0]] ^= True
        do_tick = perform_ticks and since_last_tick >= tick_interval
        screen.fill(WHITE)
        if do_tick:
            # Perform a deep copy on the 2D list
            old_grid = [[*row] for row in life_grid]
            since_last_tick = 0
        else:
            old_grid = [[]]
        for y, row in enumerate(life_grid):
            for x, tile in enumerate(row):
                if do_tick:
                    life_grid[y][x] = get_new_state(old_grid, (x, y))
                pygame.draw.rect(
                    screen, WHITE if tile else BLACK, (
                        x * TILE_WIDTH, y * TILE_HEIGHT,
                        TILE_WIDTH + 2, TILE_HEIGHT + 2
                    )
                )
                pygame.draw.rect(
                    screen, BLACK if tile else WHITE, (
                        x * TILE_WIDTH + 1, y * TILE_HEIGHT + 1,
                        TILE_WIDTH - 1, TILE_HEIGHT - 1
                    )
                )
        pygame.display.update()
        print(f"\r{clock.get_fps():5.2f} FPS", end="", flush=True)


if __name__ == "__main__":
    main()
