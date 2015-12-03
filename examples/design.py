#!/usr/bin/python
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

"""Formulate t-designs with lambda = 1 as DLX problems.

Requires the dlx and pyncomb libraries:
http://pypi.python.org/pypi/dlx
http://pypi.python.org/pypi/pyncomb

Can be run as a standalone program, or the designDLX class can be invoked with
the appropriate parameters to create and return the DLX object representing the
problem.

By Sebastian Raaphorst, 2008."""

import sys
import dlx
import pyncomb


class DesignDLX(dlx.DLX):
    """A DLX representation of a t-(v,k,1) design problem."""

    def __init__(self, t, v, k, fixings=True):
        """__init__(self, t, v, k, fixings=True):

        Create a DLX object representing the problem of finding
        t-(v,k,1) designs. If fixings is set to True, establish
        the block fixings to reduce isomorphism:
           0 ... t-2 t-1 ... k-1
           0 ... t-2 k   ... 2k-t
           .     .           .
           .     .           .
           .     .           .
           0 ... t-2 ik-(i-1)t+(i-1) ... (i+1)k-it+(i-1)

        and:

           0 ... t-3 t-1 k ... ik-(i-1)t+(i-1) ..."""

        self.t = t
        self.v = v
        self.k = k

        # Populate the columns variable.
        columns = list(pyncomb.ksubsetlex.all(v,t))

        # Now create the rows, one for each k-set.
        rows = [[pyncomb.ksubsetlex.rank(v,T) for T in pyncomb.ksubsetlex.all(pyncomb.combfuncs.createLookup(S),t)] for S in pyncomb.ksubsetlex.all(v,k)]

        # Add a field to each column to indicate that it is primary.
        dlx.DLX.__init__(self, [(c,dlx.DLX.PRIMARY) for c in columns])
        self.rowsByLexOrder = self.appendRows(rows)

        # Fix the blocks, if required.
        self.fixedBlocks = []
        if fixings:
            # First we fix the 0 ... t-2 ik-(i-1)t+(i-1) ... (i+1)k-it+(i-1)
            # blocks.
            i = 0
            block = range(0,t-1) + [0] * (k-t+1)
            while (i+1)*k - i*t + (i-1) < v:
                # Create the block.
                block[t-1:] = range(i*k - (i-1)*t + (i-1), (i+1)*k - i*t + i)

                # Rank it, mark it as used, and store it.
                r = pyncomb.ksubsetlex.rank(v, block)
                self.fixedBlocks.append(r)
                self.useRow(self.rowsByLexOrder[r])
                
                # Advance to the next block.
                i += 1

            # Now we have the remaining block, namely, the vertical one:
            # 0 ... t-3 t-1 k ... ik-(i-1)t+(i-1) ...
            block[t-2:] = [i*k - (i-1)*t + (i-1) for i in range(k-t+2)]
            r = pyncomb.ksubsetlex.rank(v, block)
            self.fixedBlocks.append(r)
            self.useRow(self.rowsByLexOrder[r])


    def printSolution(self, solution):
        """Convenience method to display solutions."""

        # We need to collapse each row list, which is a collection of t-sets, into its
        # corresponding k-set. This is simply the union of all the t-sets.
        print [list(set(reduce(lambda x,y:x+y, self.getRowList(i), []))) for i in solution]


if __name__ == "__main__":
    # Ensure correct command line arguments.
    if len(sys.argv) not in range(4,7):
        print "Usage: %s t v k [use_fixings=T/*F*] [print_designs=T/*F*]" % sys.argv[0]
        exit(1)

    # Use Psyco to speed things up if it is available.
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

    fixflag = False
    printflag = False
    (t,v,k) = map(int, sys.argv[1:4])
    if len(sys.argv) > 4:
        fixflag = (sys.argv[4] == 'T')
    if len(sys.argv) > 5:
        printflag = (sys.argv[5] == 'T')

    d = DesignDLX(t, v, k, fixflag)
    designlist = list(d.solve())
    print "*** DONE ***"
    print "Number of designs found: %d" % len(designlist)
    if printflag:
        for design in designlist:
            d.printSolution(design)
    print "Nodes per level:", d.statistics.nodes
    print "Updates per level:", d.statistics.updates
