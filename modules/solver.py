import numpy as np

def isValidSudoku(board):
    # check rows for duplicates
    for row in board:
        nums = [i for i in row if i!=0]
        if len(set(nums)) < len(nums):
            return False
    # get columns
    columns = []
    for i in range(9):
        column = [board[j][i] for j in range(9)]
        columns.append(column)
    # check columns for duplicates
    for column in columns:
        nums = [i for i in column if i!=0]
        if len(set(nums)) < len(nums):
            return False
    # get blocks
    row_chunks = []
    for row in board:
        chunks = [row[i * 3:(i + 1) * 3] for i in range((len(row) + 3 - 1) // 3 )]
        row_chunks.append(chunks)
    blocks = []
    for i in range(0, 9, 3):
        for j in range(3):
            block = [item[j] for item in row_chunks[i:i+3]]
            block = [x for y in block for x in y]
            blocks.append(block)
    # check blocks for duplicates
    for block in blocks:
        nums = [i for i in block if i!=0]
        if len(set(nums)) < len(nums):
            return False

    return True

def possible(grid,y,x,n):
    for i in range(0,9):
        if grid[y][i] == n:
            return False
    for i in range(0,9):
        if grid[i][x] == n:
            return False
    x0 = (x//3)*3
    y0 = (y//3)*3
    for i in range(0,3):
        for j in range(0,3):
            if grid[y0+i][x0+i] == n :
                return False
    return True

def solve(grid, solutions):
    for y in range(9):
        for x in range(9):
            if grid[y][x] == 0 :
                for n in range(1,10) :
                    if possible(grid,y,x,n):
                        grid[y][x] = n
                        solve(grid, solutions)
                        grid[y][x] = 0
                return
    solutions.append(np.matrix(grid))