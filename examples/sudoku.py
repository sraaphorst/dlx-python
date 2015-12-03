#!/usr/bin/env python
#
# Copyright 2009 Sebastian Raaphorst.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''A Sudoku solver using Donald Knuth's dancing links algorithm.

Requires the dlx library:
http://pypi.python.org/pypi/dlx

The DLXsudoku class is a subclass of the DLX object in the dlx library and
initializes the exact cover problem. Calling solve then generates all solutions
to the Sudoku board.

This file can also be run as an application. Executing:
   python sudoku.py
will provide instructions on how to to use it as a command line utility.

By Sebastian Raaphorst, 2009.'''

import sys
from functools import reduce
import dlx


class DLXsudoku(dlx.DLX):
    def __init__(self, grid, dim=3):
        '''Create a DLX instance representing the dim^2 by dim^2 Sudoku board
        represented by grid, which is a string of length dim^4. grid represents
        the contents of the board read from left-to-right and top-to-bottom,
        with entries from {0,...,dim^2}, where 0 represents an empty space in
        the board, and {1,...,dim^2} represent filled entries.'''

        # Create the columns.
        ctr = 0
        cols = []

        self.dim = dim
        self.dimsq = dim**2

        # Create the row coverage, which determines that entry j appears in row i.
        for i in range(self.dimsq):
            cols += [(('r',i,j),ctr+j-1) for j in range(1,self.dimsq+1)]
            ctr += self.dimsq

        # Create the column coverage, which determines that entry j appears in column i.
        for i in range(self.dimsq):
            cols += [(('c',i,j),ctr+j-1) for j in range(1,self.dimsq+1)]
            ctr += self.dimsq

        # Create the grid coverage, which determines that entry k appears in grid i,j.
        for i in range(dim):
            for j in range(dim):
                cols += [(('g',i,j,k),ctr+k-1) for k in range(1,self.dimsq+1)]
                ctr += self.dimsq

        # Create the entry coverage, which determines that entry i,j in the grid is occupied.
        for i in range(self.dimsq):
            cols += [(('e',i,j),ctr+j) for j in range(self.dimsq)]
            ctr += self.dimsq

        # Create a dictionary from this, which maps column name to column index.
        sdict = dict(cols)

        # Create the DLX object.
        dlx.DLX.__init__(self, [(colname[0], dlx.DLX.PRIMARY) for colname in cols])

        # Now create all possible rows.
        rowdict = {}
        self.lookupdict = {}
        for i in range(self.dimsq):
            for j in range(self.dimsq):
                for k in range(1,self.dimsq+1):
                    val =  self.appendRow([sdict[('r',i,k)], sdict[('c',j,k)], sdict[('g',i//dim,j//dim,k)], sdict[('e',i,j)]], (i,j,k))
                    rowdict[(i,j,k)] = val
                    self.lookupdict[val] = (i,j,k)

        # Now we want to process grid, which we take to be a string of length 81 representing the puzzle.
        # An entry of 0 means blank.
        for i in range(self.dimsq**2):
            if grid[i] != '0':
                self.useRow(rowdict[(i//self.dimsq,i%self.dimsq,int(grid[i]))])


    def createSolutionGrid(self, sol):
        '''Return a two dimensional grid representing the solution.'''

        # We need to determine what is represented by each row. This is easily accessed by rowname.
        solgrid = [['0']*self.dimsq for i in range(self.dimsq)]
        for a in sol:
            i,j,k = self.N[a]
            solgrid[i][j] = k
        return solgrid


    def createSolutionGridString(self, sol):
        '''Create a string representing the solution grid in nice format.'''

        grid = self.createSolutionGrid(sol)
        return reduce(lambda x,y:x+y, [reduce(lambda x,y:x+y, [str(grid[r][c]) + ('|' if c % self.dim == self.dim-1 and c != self.dimsq-1 else '') for c in range(self.dimsq)], '') + ('\n' if r != self.dimsq-1 else '') + ((('-'*self.dim + '+')*(self.dim-1) + '-'*self.dim + '\n') if r % self.dim == self.dim-1 and r != self.dimsq-1 else '') for r in range(self.dimsq)], '')
                

    def createSolutionString(self, sol):
        '''Return a string representation of the solution, read from left-to-right
        and top-to-bottom.'''

        return reduce(lambda x,y:x+y, map(str, reduce(lambda x,y:x+y, self.createSolutionGrid(sol), [])), '')


def checkSudoku(grid, dim=3):
    '''Given a two dimensional array of size dim^2 x dim^2, verify that it is a
    Sudoku board, i.e. that every row is a permutation of {1,...dim^2}, every
    column is a permutation of {1,...,dim^2}, and every subgrid is a permutation
    of dim^2.'''

    dimsq = dim**2

    # Make sure that every row is a permutation.
    for i in range(dimsq):
        if set(grid[i]) != set(range(1,dimsq+1)):
            #print("Row %d failed" % i)
            return False

    # Make sure that every col is a permutation.
    for i in range(dimsq):
        if set([a[i] for a in grid]) != set(range(1,dimsq+1)):
            #print("Column %d failed" % i)
            return False

    # Make sure that every subgrid is a permutation.
    for i in range(dim):
        for j in range(dim):
            if set(reduce(lambda x,y:x+y, [grid[i*dim+k][j*dim:j*dim+dim] for k in range(dim)], [])) != set(range(1,dimsq+1)):
                #print("Subgrid %d,%d failed" % (i,j))
                return False

    return True


if __name__ == '__main__':
    # Ensure correct command line arguments.
    if len(sys.argv) not in [3,4]:
        print('Usage: %s s sboard [print_as_string=T/*F*]' % sys.argv[0])
        print('\twhere sboard is a string representation of a s^2 by s^2 Sudoku board,')
        print('\tread from left-to-right and top-to-bottom, with 0 representing an')
        print('\tempty entry in the board. For example, the following Sudoku board:')
        print('\t\t _ 7 _ | 2 8 5 | _ 1 _')
        print('\t\t _ _ 8 | 9 _ 3 | 5 _ _')
        print('\t\t _ _ _ | _ _ _ | _ _ _')
        print('\t\t ------+-------+------')
        print('\t\t 5 _ _ | _ 1 _ | _ _ 8')
        print('\t\t _ 1 _ | _ _ _ | _ 9 _')
        print('\t\t 9 _ _ | _ 4 _ | _ _ 3')
        print('\t\t ------+-------+------')
        print('\t\t _ _ _ | _ _ _ | _ _ _')
        print('\t\t _ _ 2 | 4 _ 8 | 6 _ _')
        print('\t\t _ 9 _ | 6 3 2 | _ 8 _')
        print('\twould have string representation:')
        print('\t"070285010008903500000000000500010008010000090900040003000000000002408600090632080".')
        print('\n\tIf print_as_string is false (default), the solution is printed')
        print('\tas an easy-to-read grid; otherwise, the solution is printed as')
        print('\ta string in the same format as the sboard input string.')
        exit(1)

    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

    s = int(sys.argv[1])
    printFlag = (False if len(sys.argv) == 3 else (True if sys.argv[3] == 'T' else False))
    d = DLXsudoku(sys.argv[2],s)
    for sol in d.solve():
        if printFlag:
            print(d.createSolutionString(sol))
        else:
            print('SOLUTION:')
            print(d.createSolutionGridString(sol))
