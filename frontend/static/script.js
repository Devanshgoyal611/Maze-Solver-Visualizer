const canvas = document.getElementById('mazeCanvas');
const ctx = canvas.getContext('2d');
const cellSize = 20;
canvas.width = 800;
canvas.height = 400;
let grid = [];
let isDrawing = false;
let start = null;
let end = null;
let placementPhase = 'start'; // 'start' -> 'end' -> 'wall'

// Colors
const colors = {
    empty: '#ffffff',
    wall: '#2c3e50',
    start: '#27ae60',
    end: '#e74c3c',
    visited: '#3498db',
    path: '#f1c40f'
};

function initGrid() {
    const rows = Math.floor(canvas.height / cellSize);
    const cols = Math.floor(canvas.width / cellSize);
    grid = Array(rows).fill().map(() => Array(cols).fill(0));
    drawGrid();
}

function drawGrid() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw cells
    for (let row = 0; row < grid.length; row++) {
        for (let col = 0; col < grid[0].length; col++) {
            ctx.fillStyle = grid[row][col] === 1 ? colors.wall : colors.empty;
            ctx.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
        }
    }
    
    // Draw grid lines
    ctx.strokeStyle = '#bdc3c7';
    for (let i = 0; i <= grid.length; i++) {
        ctx.beginPath();
        ctx.moveTo(0, i * cellSize);
        ctx.lineTo(canvas.width, i * cellSize);
        ctx.stroke();
    }
    for (let i = 0; i <= grid[0].length; i++) {
        ctx.beginPath();
        ctx.moveTo(i * cellSize, 0);
        ctx.lineTo(i * cellSize, canvas.height);
        ctx.stroke();
    }
    
    // Draw start/end
    if (start) {
        ctx.fillStyle = colors.start;
        ctx.fillRect(start.col * cellSize, start.row * cellSize, cellSize, cellSize);
    }
    if (end) {
        ctx.fillStyle = colors.end;
        ctx.fillRect(end.col * cellSize, end.row * cellSize, cellSize, cellSize);
    }
}

function getGridPosition(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const canvasX = clientX - rect.left;
    const canvasY = clientY - rect.top;
    
    return {
        col: Math.floor(canvasX / cellSize),
        row: Math.floor(canvasY / cellSize)
    };
}

function handleClick(e) {
    const pos = getGridPosition(e.clientX, e.clientY);
    
    if (pos.row < 0 || pos.row >= grid.length || 
        pos.col < 0 || pos.col >= grid[0].length) return;

    if (e.button === 0) { // Left click
        switch(placementPhase) {
            case 'start':
                if (!start) {
                    start = pos;
                    placementPhase = 'end';
                }
                break;
            case 'end':
                if (!end && (pos.row !== start.row || pos.col !== start.col)) {
                    end = pos;
                    placementPhase = 'wall';
                }
                break;
            case 'wall':
                if ((pos.row !== start.row || pos.col !== start.col) && 
                    (pos.row !== end.row || pos.col !== end.col)) {
                    grid[pos.row][pos.col] = 1;
                }
                break;
        }
    } else if (e.button === 2) { // Right click
        if (start && pos.row === start.row && pos.col === start.col) {
            start = null;
            placementPhase = 'start';
        } else if (end && pos.row === end.row && pos.col === end.col) {
            end = null;
            placementPhase = 'end';
        }
        grid[pos.row][pos.col] = 0;
    }
    
    drawGrid();
}

// Event Listeners
canvas.addEventListener('contextmenu', e => e.preventDefault());
canvas.addEventListener('mousedown', (e) => {
    isDrawing = true;
    handleClick(e);
});

canvas.addEventListener('mousemove', (e) => {
    if (isDrawing && placementPhase === 'wall') {
        handleClick(e);
    }
});

canvas.addEventListener('mouseup', () => isDrawing = false);

document.getElementById('clear').addEventListener('click', () => {
    initGrid();
    start = null;
    end = null;
    placementPhase = 'start';
    drawGrid();
});

document.getElementById('solve-btn').addEventListener('click', async () => {
    if (!start || !end) {
        alert('Please set both start and end points first!');
        return;
    }
    
    try {
        const algorithm = document.getElementById('algorithm').value;
        const response = await fetch('/solve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                grid: grid,
                start: [start.row, start.col],
                end: [end.row, end.col],
                algorithm: algorithm
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Solution failed');
        }

        const result = await response.json();
        
        if (result.path.length === 0) {
            alert('No path found!');
            return;
        }

        animateSolution(result.visited, result.path);
    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
    }
});

function animateSolution(visitedNodes, path) {
    // Clear previous animations
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawGrid();

    let i = 0;
    function visitAnimation() {
        if (i < visitedNodes.length) {
            const [row, col] = visitedNodes[i];
            if ((!start || row !== start.row || col !== start.col) && 
                (!end || row !== end.row || col !== end.col)) {
                ctx.fillStyle = colors.visited;
                ctx.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
            }
            i++;
            requestAnimationFrame(visitAnimation);
        } else {
            animatePath(path);
        }
    }

    function animatePath(path) {
        let j = 0;
        function pathAnimation() {
            if (j < path.length) {
                const [row, col] = path[j];
                ctx.fillStyle = colors.path;
                ctx.fillRect(col * cellSize, row * cellSize, cellSize, cellSize);
                j++;
                requestAnimationFrame(pathAnimation);
            }
        }
        pathAnimation();
    }

    visitAnimation();
}

// Initialize the grid
initGrid();


