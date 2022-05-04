# Game of Life

## Ants – (`ants.py`)

This simulation contains many "ants" with three possible states: hunting, path following to food, and path following to home. All ants start in the same place (their home) in the hunting state, where they will move in completely random directions until they find themselves adjacent to a tile marked as food, or an existing path. If an ant finds itself adjacent to food, the path that it took all the way from home will be stored and made visible to all ants. If an ant finds itself adjacent to one of these paths, it will begin following it to the food. Once an ant reaches the food at the end of a path, the ant will then traverse backwards along the path, back home. Once it reaches home, it will go to the food again along the same path, and the cycle continues.

Note that, unlike Conway's Game of Life as seen below, not every ant moves simultaneously. This means that if an ant successfully creates a path, other ants that are yet to move in the current tick can then join that path. Ants are iterated over from left-to-right, top-to-bottom.

### Controls

- `Click` – Toggle whether a square is food or not
- `Space` – Start/stop simulation
- `Up/Down` – Adjust simulation speed
- `Tab` – Toggle displaying established paths
- `R` – Reset grid

## Conway's Game of Life – (`conway.py`)

Conway's game of life can be summarised in four rules:

1. Any living (black) cell with less than two living neighbours (including diagonals) dies (becomes white).
2. Any living cell with two or three living neighbours survives.
3. Any living cell with over three living neighbours dies.
4. Any dead cell with exactly three living neighbours becomes alive.

Note that every cell has these rules executed on it simultaneously in a single tick, not one after the other.

More info can be found here: <https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life>

### Controls

- `Click` – Toggle whether a square is alive or not
- `Space` – Start/stop simulation
- `Up/Down` – Adjust simulation speed
- `R` – Reset grid
