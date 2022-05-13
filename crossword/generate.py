import sys

from crossword import *
from collections import deque


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for domain in self.domains.keys():
            domainsList = []
            for word in self.domains[domain]:
                if domain.length != len(word):
                    domainsList.append(word)
            for word in domainsList:
                self.domains[domain].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = False
        overlapxy = self.crossword.overlaps[x, y]
        if overlapxy:
            i, j = overlapxy[0], overlapxy[1]
            domainsList = []
            for X in self.domains[x]:
                c = False
                for Y in self.domains[y]:
                    if X != Y and X[i] == Y[j]:##
                        c = True
                if not c:
                    domainsList.append(X)
            
            if domainsList:
                revision = True
                for word in domainsList:
                    self.domains[x].remove(word)

        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs:
            arcs = deque(arcs)
        else:
            arcs = deque()
            for i in self.crossword.variables:
                for j in self.crossword.neighbors(i):
                    arcs.appendleft((i,j))

        while arcs:
            i, j = arcs.pop()
            if self.revise(i,j):
                if len(self.domains[i]) == 0:
                    return False

                for k in self.crossword.neighbors(i) - {j}:
                    arcs.appendleft((k, i))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        complete = True

        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                complete = False
                break
            
            if assignment[variable] not in self.crossword.words:
                complete = False

        return complete

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        consistent = True

        for x, word in assignment.items():
            if x.length != len(word):
                consistent = False

            neighbors = self.crossword.neighbors(x)
            for y in neighbors:
                overlapxy = self.crossword.overlaps[x, y]
                if y in assignment:
                    if assignment[y][overlapxy[1]] != word[overlapxy[0]]:
                        consistent = False

        return consistent

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)
        lista = []
        for variable in self.domains[var]:
            if variable not in assignment:
                c = 0
                for neighbor in neighbors:
                    if variable in self.domains[neighbor]:
                        c+=1
                lista.append([variable,c])
        lista.sort(key=lambda x: x[1])
        lista = [x[0] for x in lista]
        return lista


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        ret = None

        vars = []
        for var in self.crossword.variables:
            if var not in assignment:
                a, b = len(self.domains[var]), len(self.crossword.neighbors(var))
                vars.append((var,a,b))

        if vars:
            vars.sort(key=lambda x: x[1])
            if len(vars) == 1:
                ret = vars[0][0]
            else: 
                if vars[0][1] == vars[1][1]:
                    vars.sort(key=lambda x: x[2])
                    ret = vars[-1][0]
                else:
                    ret = vars[0][0]

        return ret


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var,assignment):
            assignment[var] = value
            if self.consistent(assignment):
                result = self.backtrack(assignment)
                if result:
                    return result
                
                assignment.pop(var)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

#python3 generate.py data/structure2.txt data/words2.txt output.png