"""
A simulation of ants finding food and bringing it home along a path.
"""
import random
import sys
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

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
ANT_COUNT = 500
ANT_DRAW_RADIUS = min(TILE_WIDTH, TILE_HEIGHT) // 4

# Expressed in milliseconds (or None to disable)
FOOD_MOVE_DELAY: Optional[int] = None


@dataclass
class Ant:
    """
    Represents a single ant on the grid.
    """
    coord: Tuple[int, int] = ANT_HOME_COORD
    state: int = FOOD_HUNT
    current_path: List[Tuple[int, int]] = field(default_factory=list)
    current_path_index: int = -1
    draw_offset: Tuple[float, float] = field(default_factory=lambda: (
        random.randint(0, TILE_WIDTH - (ANT_DRAW_RADIUS * 2)),
        random.randint(0, TILE_HEIGHT - (ANT_DRAW_RADIUS * 2))
    ))

    def tick(self, food: List[Tuple[int, int]],
             paths: List[List[Tuple[int, int]]], ants: List['Ant']) -> None:
        """
        Update this ant depending on its state and surroundings.
        """
        if self.state == FOOD_HUNT:
            if len(get_adjacent_food(food, self.coord)) >= 1:
                # Food has been found. Add shallow copy of current path to
                # known paths then return home.
                paths.append([*self.current_path])
                self.state = FOLLOW_PATH_HOME
            else:
                adjacent_paths = get_adjacent_paths(self.coord, paths)
                if len(adjacent_paths) >= 1:
                    new_path = random.choice(adjacent_paths)
                    # Create a copy of the selected path
                    self.current_path = [*new_path[0]]
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
                    for vector in directions:
                        new_pos = (
                            self.coord[0] + vector[0],
                            self.coord[1] + vector[1]
                        )
                        if (0 <= new_pos[0] < GRID_WIDTH
                                and 0 <= new_pos[1] < GRID_HEIGHT):
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
                if len(get_adjacent_food(food, self.coord)) >= 1:
                    # Food is still present and the end of the path.
                    self.state = FOLLOW_PATH_HOME
                else:
                    # Food is gone. Forget this path and stop other ants
                    # following it.
                    paths.remove(self.current_path)
                    old_path = self.current_path
                    for ant in ants:
                        if ant.current_path == old_path:
                            ant.state = FOOD_HUNT
            else:
                self.current_path_index += 1
                self.coord = self.current_path[self.current_path_index]
        elif self.state == FOLLOW_PATH_HOME:
            if self.current_path_index == 0:
                self.state = FOLLOW_PATH_FOOD
            else:
                self.current_path_index -= 1
                self.coord = self.current_path[self.current_path_index]


def get_adjacent_food(food: List[Tuple[int, int]], pos: Tuple[int, int]
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
                    and 0 <= new_pos[1] < GRID_HEIGHT
                    and 0 <= new_pos[0] < GRID_WIDTH):
                if new_pos in food:
                    coords.append(new_pos)
    return coords


def get_adjacent_paths(pos: Tuple[int, int], paths: List[List[Tuple[int, int]]]
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
                    and 0 <= new_pos[1] < GRID_HEIGHT
                    and 0 <= new_pos[0] < GRID_WIDTH):
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
    food_coords: List[Tuple[int, int]] = []
    living_ants = [Ant() for _ in range(ANT_COUNT)]
    paths_to_food: List[List[Tuple[int, int]]] = []
    perform_ticks = False
    show_paths = True
    tick_interval = 100
    since_last_tick = 0
    since_last_move = -FOOD_MOVE_DELAY if FOOD_MOVE_DELAY is not None else 0
    # Main game loop
    while True:
        frame_time = clock.tick()
        since_last_tick += frame_time
        since_last_move += frame_time
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
                elif event.key == pygame.K_DOWN and tick_interval >= 10:
                    tick_interval -= 10
                elif event.key == pygame.K_UP:
                    tick_interval += 10
                elif event.key == pygame.K_r:
                    food_coords = []
                    living_ants = [Ant() for _ in range(ANT_COUNT)]
                    paths_to_food = []
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
                    if grid_pos in food_coords:
                        food_coords.remove(grid_pos)
                    else:
                        food_coords.append(grid_pos)
        do_tick = perform_ticks and since_last_tick >= tick_interval
        screen.fill(WHITE)
        if (FOOD_MOVE_DELAY is not None and perform_ticks
                and since_last_move >= FOOD_MOVE_DELAY
                and len(food_coords) >= 1):
            food_coords[random.randint(0, len(food_coords) - 1)] = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            since_last_move = 0
        if do_tick:
            since_last_tick = 0
        if show_paths:
            path_coords = {coord for path in paths_to_food for coord in path}
        else:
            path_coords = set()
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(
                    screen, BLACK, (
                        x * TILE_WIDTH, y * TILE_HEIGHT,
                        TILE_WIDTH + 2, TILE_HEIGHT + 2
                    )
                )
                if (x, y) in food_coords:
                    colour = GREEN
                elif (x, y) == ANT_HOME_COORD:
                    colour = BLUE
                elif show_paths and (x, y) in path_coords:
                    colour = PINK
                else:
                    colour = WHITE
                pygame.draw.rect(
                    screen, colour, (
                        x * TILE_WIDTH + 1, y * TILE_HEIGHT + 1,
                        TILE_WIDTH - 1, TILE_HEIGHT - 1
                    )
                )
        for ant in living_ants:
            if do_tick:
                ant.tick(food_coords, paths_to_food, living_ants)
            pygame.draw.circle(
                screen, RED, (
                    ant.coord[0] * TILE_WIDTH + ANT_DRAW_RADIUS
                    + ant.draw_offset[0],
                    ant.coord[1] * TILE_HEIGHT + ANT_DRAW_RADIUS
                    + ant.draw_offset[1]
                ), ANT_DRAW_RADIUS
            )
        pygame.display.update()
        print(f"\r{clock.get_fps():5.2f} FPS", end="", flush=True)


if __name__ == "__main__":
    main()
