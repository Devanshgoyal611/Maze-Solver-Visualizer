from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from heapq import heappop, heappush

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="../frontend/static"), name="static")
templates = Jinja2Templates(directory="../frontend/templates")

class MazeSolver:
    @staticmethod
    def bfs(grid: List[List[int]], start: List[int], end: List[int]) -> Dict[str, Any]:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        rows, cols = len(grid), len(grid[0])
        queue = [(start[0], start[1])]
        visited = set([(start[0], start[1])])
        parent = {}
        visited_order = []
        
        while queue:
            x, y = queue.pop(0)
            visited_order.append([x, y])
            
            if [x, y] == end:
                path = MazeSolver._reconstruct_path(parent, (end[0], end[1]))
                return {"visited": visited_order, "path": path}
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if grid[nx][ny] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = (x, y)
                        queue.append((nx, ny))
        
        return {"visited": visited_order, "path": []}

    @staticmethod
    def dfs(grid: List[List[int]], start: List[int], end: List[int]) -> Dict[str, Any]:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        rows, cols = len(grid), len(grid[0])
        stack = [(start[0], start[1])]
        visited = set([(start[0], start[1])])
        parent = {}
        visited_order = []
        
        while stack:
            x, y = stack.pop()
            visited_order.append([x, y])
            
            if [x, y] == end:
                path = MazeSolver._reconstruct_path(parent, (end[0], end[1]))
                return {"visited": visited_order, "path": path}
            
            # Explore neighbors in reverse order for more natural DFS
            for dx, dy in reversed(directions):
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if grid[nx][ny] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = (x, y)
                        stack.append((nx, ny))
        
        return {"visited": visited_order, "path": []}
    
    @staticmethod
    def iddfs(grid: List[List[int]], start: List[int], end: List[int]) -> Dict[str, Any]:
        """Iterative Deepening Depth-First Search"""
        def dls(current: Tuple[int, int], depth: int) -> Tuple[bool, List[List[int]]]:
            if depth == 0:
                return (current == (end[0], end[1])), []
            if current == (end[0], end[1]):
                return True, [list(current)]
            
            visited.add(current)
            visited_order.append(list(current))
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = current[0] + dx, current[1] + dy
                if (0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and 
                    grid[nx][ny] == 0 and (nx, ny) not in visited):
                    found, path = dls((nx, ny), depth - 1)
                    if found:
                        return True, [list(current)] + path
            return False, []

        max_depth = len(grid) * len(grid[0])  # Worst case
        visited_order = []
        
        for depth in range(max_depth):
            visited = set()
            found, path = dls((start[0], start[1]), depth)
            if found:
                return {
                    "visited": visited_order,
                    "path": path
                }
        
        return {"visited": visited_order, "path": []}

    @staticmethod
    def dijkstra(grid: List[List[int]], start: List[int], end: List[int]) -> Dict[str, Any]:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        rows, cols = len(grid), len(grid[0])
        heap = [(0, start[0], start[1])]
        costs = {(start[0], start[1]): 0}
        parent = {}
        visited_order = []
        
        while heap:
            cost, x, y = heappop(heap)
            visited_order.append([x, y])
            
            if [x, y] == end:
                path = MazeSolver._reconstruct_path(parent, (end[0], end[1]))
                return {"visited": visited_order, "path": path}
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    new_cost = cost + 1
                    if grid[nx][ny] == 0 and ((nx, ny) not in costs or new_cost < costs[(nx, ny)]):
                        costs[(nx, ny)] = new_cost
                        parent[(nx, ny)] = (x, y)
                        heappush(heap, (new_cost, nx, ny))
        
        return {"visited": visited_order, "path": []}
    
    @staticmethod
    def astar(grid: List[List[int]], start: List[int], end: List[int]) -> Dict[str, Any]:
        """A* Search Algorithm with Manhattan distance heuristic"""
        def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        rows, cols = len(grid), len(grid[0])
        open_set = [(0, start[0], start[1])]
        came_from = {}
        g_score = {(start[0], start[1]): 0}
        f_score = {(start[0], start[1]): heuristic((start[0], start[1]), (end[0], end[1]))}
        visited_order = []

        while open_set:
            _, x, y = heappop(open_set)
            visited_order.append([x, y])

            if [x, y] == end:
                path = MazeSolver._reconstruct_path(came_from, (end[0], end[1]))
                return {"visited": visited_order, "path": path}

            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0:
                    tentative_g = g_score[(x, y)] + 1
                    if (nx, ny) not in g_score or tentative_g < g_score[(nx, ny)]:
                        came_from[(nx, ny)] = (x, y)
                        g_score[(nx, ny)] = tentative_g
                        f_score[(nx, ny)] = tentative_g + heuristic((nx, ny), (end[0], end[1]))
                        heappush(open_set, (f_score[(nx, ny)], nx, ny))

        return {"visited": visited_order, "path": []}
    
    @staticmethod
    def bidirectional_bfs(grid: List[List[int]], start: List[int], end: List[int]) -> Dict[str, Any]:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        rows, cols = len(grid), len(grid[0])
        
        queue_start = [(start[0], start[1])]
        visited_start = {(start[0], start[1]): None}
        
        queue_end = [(end[0], end[1])]
        visited_end = {(end[0], end[1]): None}
        
        visited_order = []
        intersection = None

        while queue_start and queue_end:
            # Expand start frontier
            x, y = queue_start.pop(0)
            visited_order.append([x, y])
            
            if (x, y) in visited_end:
                intersection = (x, y)
                break
                
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0:
                    if (nx, ny) not in visited_start:
                        visited_start[(nx, ny)] = (x, y)
                        queue_start.append((nx, ny))

            # Expand end frontier
            x, y = queue_end.pop(0)
            visited_order.append([x, y])
            
            if (x, y) in visited_start:
                intersection = (x, y)
                break
                
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == 0:
                    if (nx, ny) not in visited_end:
                        visited_end[(nx, ny)] = (x, y)
                        queue_end.append((nx, ny))

        # Reconstruct path
        path = []
        if intersection:
            # Path from start to intersection
            current = intersection
            while current is not None:
                path.append([current[0], current[1]])
                current = visited_start.get(current)
            path = path[::-1]
            
            # Path from intersection to end (excluding intersection)
            current = visited_end.get(intersection)
            while current is not None:
                path.append([current[0], current[1]])
                current = visited_end.get(current)
        
        return {"visited": visited_order, "path": path}

    @staticmethod
    def _reconstruct_path(parent: Dict[Tuple[int, int], Optional[Tuple[int, int]]], end: Tuple[int, int]) -> List[List[int]]:
        path = []
        current = end
        while current is not None:
            path.append([current[0], current[1]])
            current = parent.get(current)
        return path[::-1]

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/solve")
async def solve_maze(request: Request):
    try:
        data = await request.json()
        algorithm = data.get('algorithm')
        grid = np.array(data.get('grid')).tolist()
        start = data.get('start')
        end = data.get('end')
        
        if not all([algorithm, grid, start, end]):
            raise HTTPException(status_code=400, detail="Missing required parameters")
            
        solver = MazeSolver()
        
        if algorithm == 'bfs':
            result = solver.bfs(grid, start, end)
        elif algorithm == 'dfs':
            result = solver.dfs(grid, start, end)
        elif algorithm == 'dijkstra':
            result = solver.dijkstra(grid, start, end)
        elif algorithm == 'iddfs':
            result = solver.iddfs(grid, start, end)
        elif algorithm == 'astar':
            result = solver.astar(grid, start, end)
        elif algorithm == 'bidirectional_bfs':
            result = solver.bidirectional_bfs(grid, start, end)
        else:
            raise HTTPException(status_code=400, detail="Invalid algorithm")
            
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )