import copy
import math
import sys

from sqlalchemy.orm import backref

from crossword import *


class CrosswordCreator:

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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        for variable in self.crossword.variables:
            domain_copy = copy.copy(self.domains[variable])
            for word in domain_copy:
                if variable.length != len(word):
                    self.domains[variable].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        if self.crossword.overlaps[(x, y)] is None:
            return False

        i, j = self.crossword.overlaps[(x, y)]

        to_remove = set()
        for word_x in self.domains[x]:
            if not any(word_y[j] == word_x[i] for word_y in self.domains[y]):
                to_remove.add(word_x)

        if to_remove:
            self.domains[x] -= to_remove
            return True

        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        q = []
        if arcs is not None:
            q = arcs
        else:
            for u,v in self.crossword.overlaps:
                if self.crossword.overlaps[(u, v)] is not None:
                    q.append((u, v))

        while len(q) != 0:
            x, y = q.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                for neighbor in self.crossword.neighbors(x):
                    if neighbor == y:
                        continue
                    q.append((neighbor, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        if len(assignment) == 0:
            return False

        for var in self.crossword.variables:
            if var not in assignment or assignment[var] is None:
                return False

        # for word in assignment.values():
        #     if word is None or len(word) == 0:
        #         return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        used_words = set()

        for v, k in assignment.items():

            if len(k) != v.length or k in used_words:
                return False

            for neighbor in self.crossword.neighbors(v):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[(v, neighbor)]
                    if overlap is not None:
                        i, j = overlap
                        if k[i] != assignment[neighbor][j]:
                            return False
            used_words.add(k)
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        domains = self.domains[var]
        counts = {}

        for value in self.domains[var]:
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    continue

                if self.crossword.overlaps[(var, neighbor)]:
                    i, j = self.crossword.overlaps[(var, neighbor)]
                    if value[i] != assignment[neighbor][j]:
                        count += 1

            counts[value] = count

        ordered = sorted(domains, key=lambda x:counts[x])
        return ordered


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        answer = None
        minimum = math.inf
        degree = -1
        for variable in self.crossword.variables:
            if variable in assignment:
                continue
            if answer is None or len(self.domains[variable]) < minimum or \
                    (len(self.domains[variable]) == minimum and len(self.crossword.neighbors(variable)) > degree):
                minimum = len(self.domains[variable])
                answer = variable
                degree = len(self.crossword.neighbors(variable))

        return answer

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        variable = self.select_unassigned_variable(assignment)

        for value in self.order_domain_values(variable, assignment):
            assignment[variable] = value

            if self.consistent(assignment):
                backup = copy.deepcopy(self.domains)
                if self.ac3():
                    result = self.backtrack(assignment)
                    if result:
                        return result
                self.domains = backup

            del assignment[variable]

        print(assignment)
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
