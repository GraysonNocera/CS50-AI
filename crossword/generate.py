import sys
import time

from crossword import *


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

        # for each variable in domains
        for v in self.domains:

            # initialize a set that will hold all values not the correct length
            wrongLength = set()

            # iterates through the values of v
            for x in self.domains[v]:

                # if the length of the value is not the length of the variable, put in wrongLength
                if len(x) != v.length:
                    wrongLength.add(x)

            # for every word in wrongLength, remove that word from the domain of the variable       
            for word in wrongLength:
                self.domains[v].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        # Sets revision to false, as we have not revised the domains of either variable yet
        revision = False

        # A set of all values in domain of x that are not consistent and will be removed
        inconsistent = set()

        # Finds the overlap between x and y
        tup = self.crossword.overlaps[x, y]

        # If there is no overlap, the two variables are not connected and no arc consistency is necessary
        if tup is None:
            return revision

        # Iterate through the values of x's domain
        for value_x in self.domains[x]:

            # Iterate through the values of y's domain
            for value_y in self.domains[y]:
                # If the two letters do not match at overlap point, we can remove that value from x
                if value_x[tup[0]] != value_y[tup[1]]:
                    inconsistent.add(value_x)
                else:
                    if value_x in inconsistent:
                        inconsistent.remove(value_x)
                    break
        
        # Remove every variable that does not work with variable y
        for value in inconsistent:
            self.domains[x].remove(value)
            revision = True

        # Return True if we made a change to the domain
        return revision

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # Creates a queue of all arcs we need to make arc consistent
        queue = list()

        # If we do not have an input of arcs, we take all arcs in the problem
        if arcs is None:
            for variable in self.crossword.variables:
                for neighbor in self.crossword.neighbors(variable):
                    queue.append((variable, neighbor))
        
        # If we are given a list of arcs, queue becomes all those arcs
        else:
            queue = arcs

        # While there are still arcs in the queue
        while queue != []:

            # For each pair of variables that are connected
            for (x, y) in queue:

                # Remove the tuple from the queue
                queue.remove((x, y))

                # If a change is made to x's domain
                if self.revise(x, y):

                    # If the length of the domain becomse 0, there is no answer for the problem
                    if len(self.domains[x]) == 0:
                        return False

                    # Add neighbors of x back to the queue to evaluate further
                    for z in self.crossword.neighbors(x):
                        if z != y:
                            queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # If the assignment is empty, return False because there is no answer
        if assignment is None:
            return False

        # For every key (variable) in the assignment 
        for key in assignment:

            # If any variable does not have a word associated with it, return False, because the puzzle is not complete
            if len(assignment[key]) == 0:
                return False

        # Otherwise, every variable must have a word with it
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Checks to make sure each word is unique
        if len(assignment) != len(set(assignment.values())):
            return False

        # Checks to make sure every value is the correct length
        for variable in assignment:
            if variable.length != len(assignment[variable]):
                return False

            # Checks that overlaps match
            for variable2 in assignment:
                if variable != variable2 and self.crossword.overlaps[variable, variable2] is not None:
                    if assignment[variable][self.crossword.overlaps[variable, variable2][0]] != assignment[variable2][self.crossword.overlaps[variable, variable2][1]]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Get all the neighbors of var
        neighbors = self.crossword.neighbors(var)

        domainValues = dict()

        # Iterate through the values of var's domain to determine which option is best
        for value in self.domains[var]:

            # Iterate through the neighbors of var
            for neighbor in neighbors:

                domainValues[value] = 0

                # If the neighbor already has a word, we ignore it
                if neighbor not in assignment:

                    # Get the overlap betwen the var and the neighbor
                    overlap = self.crossword.overlaps[var, neighbor]

                    # Iterate through the values of neighbor's domain
                    for possibility in self.domains[neighbor]:

                        # If the value of neighbor's domain equals the value of var's domain, we can eliminate that option
                        if possibility == value:

                            # Add 1 to domainValues[value] because we are keeping track of how many options this value eliminates
                            # From other domains of it's neighbors
                            domainValues[value] += 1

                        # If the overlapping letters do not coincide, we can eliminate that option as well
                        if value[overlap[0]] != possibility[overlap[1]]:
                            domainValues[value] += 1
    
        # Sort the domainValues in order from least options eliminated to most options eliminated
        sortedDomainValues = sorted(domainValues.items(), key=lambda x: x[1])

        # Create a list of these values
        out = [item for t in sortedDomainValues for item in t]
        sortedDomain = list()

        # Remove every instance of an int to get just the variables and not the number of options they eliminate
        for item in out:
            if not isinstance(item, int):
                sortedDomain.append(item)

        # Return the sortedDomain accoridng to how many options they eliminate
        return sortedDomain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        domainValues = dict()

        # Iterate through the variables in the crossword
        for variable in self.crossword.variables:

            # Only choose variables that are not in the assignment (that do not already have a value)
            if variable not in assignment:

                domainValues[variable] = 0

                # Map the variable to how many domain values it has
                for value in self.domains[variable]:
                    domainValues[variable] += 1
        
        # Order the dictionary accoring to which variable has the smallest domain
        sortedDomainValues = sorted(domainValues.items(), key=lambda x: x[1])

        # Create a dictionary of all the variables with the same number of domain values
        ties = dict()
        for (x, y) in sortedDomainValues:
            if y == sortedDomainValues[0][1]:
                ties[x] = 0
        
        # For every variable with the same number of domain values, map it to how many neighbors (arcs) it has
        for var in ties:
            ties[var] = len(self.crossword.neighbors(var))
        
        # Sort the ties according to which variable has the highest degree
        sortedTies = sorted(ties.items(), key=lambda x: x[1], reverse=True)

        # Return the unassigned variable that has the smallest domain and highest degree (# of neighbors)
        # among the unassigned variables
        return sortedTies[0][0]



    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # If the assignment is complete and it has a value for every variable in the crossword puzzle and every value is consistent
        if self.assignment_complete(assignment) and len(assignment) == len(self.crossword.variables) and self.consistent(assignment):
            return assignment
        
        # Select a variable that has not been assigned a value
        var = self.select_unassigned_variable(assignment)

        # Iterate through the ordered domain values of the variable to test each one
        for value in self.order_domain_values(var, assignment):

            # Join var mapped to its value and the assignment to see if it is consistent
            temp = {var:value}
            temp1 = assignment

            # If the value has not already been used and it is consistent with the rest of the assignment
            if value not in assignment.values() and self.consistent(merge(temp, temp1)):

                # Actually add the variable and its value to the assignment
                assignment[var] = value

                # Continue to backtrack until every variable has an assignment
                result = self.backtrack(assignment)

                # If the assignment is complete and if it is consistent, we have found the answer
                if self.assignment_complete(result):
                    if self.consistent(result):
                        return result

                # Otherwise, we picked a wrong value somewhere, so delete the latest value of the variable to try another
                del assignment[var]

        # If we can never find a result to return, the problem has no solution
        return None
    


def merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res


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



# len(assignment) == len(set(assignment.values()))