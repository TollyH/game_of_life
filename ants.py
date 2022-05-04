"""
A simulation of ants finding food and bringing it home along a path.
"""
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple

import pygame

BLACK = (0x00, 0x00, 0x00)
WHITE = (0xFF, 0xFF, 0xFF)
RED = (0xFF, 0x00, 0x00)
GREEN = (0x00, 0xFF, 0x00)
BLUE = (0x00, 0x00, 0xFF)
PINK = (0xFF, 0x95, 0xFF)

# States
FOOD_HUNT = 0
FOLLOW_PATH_FOOD = 1
FOLLOW_PATH_HOME = 2

VIEWPORT_WIDTH = 500
VIEWPORT_HEIGHT = 500
GRID_WIDTH = 50
GRID_HEIGHT = 50

TILE_WIDTH = VIEWPORT_WIDTH // GRID_WIDTH
TILE_HEIGHT = VIEWPORT_HEIGHT // GRID_HEIGHT

ANT_HOME_COORD = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
ANT_COUNT = 100


@dataclass
class Ant:
    """
    Represents a single ant on the grid.
    """
    coord: Tuple[int, int] = ANT_HOME_COORD
    last_vector: Tuple[int, int] = field(
        default_factory=lambda: random.choice([
            (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1),
            (-1, 1), (1, -1)
        ])
    )
    state: int = FOOD_HUNT
    current_path: List[Tuple[int, int]] = field(default_factory=list)
    current_path_index: int = -1

    def tick(self, grid: List[List[bool]], paths: List[List[Tuple[int, int]]]
             ) -> None:
        """
        Update this ant depending on its state and surroundings.
        """
        if self.state == FOOD_HUNT:
            if len(get_adjacent_food(grid, self.coord)) >= 1:
                # Food has been found. Add shallow copy of current path to
                # known paths then return home.
                paths.append([*self.current_path])
                self.state = FOLLOW_PATH_HOME
            else:
                adjacent_paths = get_adjacent_paths(grid, self.coord, paths)
                if len(adjacent_paths) >= 1:
                    new_path = random.choice(adjacent_paths)
                    self.current_path = new_path[0]
                    self.current_path_index = new_path[1]
                    self.coord = self.current_path[self.current_path_index]
                    self.state = FOLLOW_PATH_FOOD
                else:
                    # No food found yet, move in a random direction.
                    directions = [
                        (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1),
                        (-1, 1), (1, -1)
                    ]
                    random.shuffle(directions)
                    for i, vector in enumerate(directions):
                        new_pos = (
                            self.coord[0] + vector[0],
                            self.coord[1] + vector[1]
                        )
                        if (0 <= new_pos[0] < len(grid[0])
                                and 0 <= new_pos[1] < len(grid)):
                            self.coord = new_pos
                            if new_pos in self.current_path:
                                index = self.current_path.index(new_pos)
                                self.current_path = (
                                    self.current_path[:index + 1]
                                )
                                self.current_path_index = index
                            else:
                                self.current_path.append(new_pos)
                                self.current_path_index += 1
                            break
        elif self.state == FOLLOW_PATH_FOOD:
            if self.current_path_index == len(self.current_path) - 1:
                self.state = FOLLOW_PATH_HOME
            else:
                self.current_path_index += 1
                self.coord = self.current_path[self.current_path_index]
        elif self.state == FOLLOW_PATH_HOME:
            if self.current_path_index == 0:
                self.state = FOLLOW_PATH_FOOD
            else:
                self.current_path_index -= 1
                self.coord = self.current_path[self.current_path_index]


def get_adjacent_food(grid: List[List[bool]], pos: Tuple[int, int]
                      ) -> List[Tuple[int, int]]:
    """
    Get the coords of food tiles immediately surrounding a point on a grid.
    Includes diagonals, but not the provided position itself.
    """
    coords: List[Tuple[int, int]] = []
    for y_offset in range(-1, 2):
        for x_offset in range(-1, 2):
            new_pos = (pos[0] + x_offset, pos[1] + y_offset)
            # Don't check the current cell position
            if ((y_offset != 0 or x_offset != 0)
                    and 0 <= new_pos[1] < len(grid)
                    and 0 <= new_pos[0] < len(grid[0])):
                if grid[new_pos[1]][new_pos[0]]:
                    coords.append(new_pos)
    return coords


def get_adjacent_paths(grid: List[List[bool]], pos: Tuple[int, int],
                       paths: List[List[Tuple[int, int]]]
                       ) -> List[Tuple[List[Tuple[int, int]], int]]:
    """
    Get any paths immediately surrounding a point on a grid.
    Includes diagonals, but not the provided position itself.
    """
    adjacent_paths: List[Tuple[List[Tuple[int, int]], int]] = []
    for y_offset in range(-1, 2):
        for x_offset in range(-1, 2):
            new_pos = (pos[0] + x_offset, pos[1] + y_offset)
            # Don't check the current cell position
            if ((y_offset != 0 or x_offset != 0)
                    and 0 <= new_pos[1] < len(grid)
                    and 0 <= new_pos[0] < len(grid[0])):
                adjacent_paths += [
                    (x, x.index(new_pos)) for x in paths if new_pos in x
                ]
    return adjacent_paths


def main() -> None:
    """
    Main function for the game. Renders the grid, handles input, and performs
    each tick where applicable.
    """
    pygame.init()
    screen = pygame.display.set_mode((VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
    pygame.display.set_caption("Ant Simulation - Stopped 1t/100ms")
    clock = pygame.time.Clock()
    food_grid = [[False] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    living_ants = [Ant() for _ in range(ANT_COUNT)]
    paths_to_food: List[List[Tuple[int, int]]] = []
    perform_ticks = False
    show_paths = True
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
                if event.key == pygame.K_TAB:
                    # Flip bool value
                    show_paths ^= True
                elif event.key == pygame.K_SPACE:
                    # Flip bool value
                    perform_ticks ^= True
                elif event.key == pygame.K_DOWN and tick_interval > 10:
                    tick_interval -= 10
                elif event.key == pygame.K_UP:
                    tick_interval += 10
                pygame.display.set_caption(
                    f"Ant Simulation - Running 1t/{tick_interval}ms"
                    if perform_ticks else
                    f"Ant Simulation - Stopped 1t/{tick_interval}ms"
                )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_LEFT:
                    mouse_pos = pygame.mouse.get_pos()
                    grid_pos = (
                        mouse_pos[0] // TILE_WIDTH,
                        mouse_pos[1] // TILE_HEIGHT
                    )
                    # Flip bool value of tile
                    food_grid[grid_pos[1]][grid_pos[0]] ^= True
        do_tick = perform_ticks and since_last_tick >= tick_interval
        screen.fill(WHITE)
        if do_tick:
            for ant in living_ants:
                ant.tick(food_grid, paths_to_food)
            since_last_tick = 0
        ant_tiles = {x.coord for x in living_ants}
        for y, row in enumerate(food_grid):
            for x, tile in enumerate(row):
                if do_tick:
                    pass
                pygame.draw.rect(
                    screen, BLACK, (
                        x * TILE_WIDTH, y * TILE_HEIGHT,
                        TILE_WIDTH + 2, TILE_HEIGHT + 2
                    )
                )
                if tile:
                    colour = GREEN
                elif (x, y) == ANT_HOME_COORD:
                    colour = BLUE
                elif (x, y) in ant_tiles:
                    colour = RED
                elif show_paths and any(
                        (x, y) in path for path in paths_to_food):
                    colour = PINK
                else:
                    colour = WHITE
                pygame.draw.rect(
                    screen, colour, (
                        x * TILE_WIDTH + 1, y * TILE_HEIGHT + 1,
                        TILE_WIDTH - 1, TILE_HEIGHT - 1
                    )
                )
        pygame.display.update()
        print(f"\r{clock.get_fps():5.2f} FPS", end="", flush=True)


if __name__ == "__main__":
    main()
