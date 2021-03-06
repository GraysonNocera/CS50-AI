import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mines = set()

        if len(self.cells) == self.count:
            for thing in self.cells:
                mines.add(thing)

        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safes = set()
        # print("sentence: ", self.cells, self.count)

        if self.count == 0:
            for thing in self.cells:
                safes.add(thing)

        # print("safes in known_safes: ", safes)
        return safes

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # print("mark_mine before: ", self.cells)
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        # print("mark_mine after: ", self.cells)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # Marks the cell as a move that has been made
        self.moves_made.add(cell)

        # Marks the cell as a safe space
        self.mark_safe(cell)
        # print("known safe: ", cell)
    
        nearby = set()
        i = cell[0]
        j = cell[1]

        nearby.add((i + 1, j + 1))
        nearby.add((i - 1, j - 1))
        nearby.add((i - 1, j + 1))
        nearby.add((i + 1, j - 1))
        nearby.add((i + 1, j))
        nearby.add((i - 1, j))
        nearby.add((i, j + 1))
        nearby.add((i, j - 1))

        # If the spot is in the top left corner
        if i == 0 and j == 0:
            print("top left corner")
            nearby.remove((i - 1, j - 1))
            nearby.remove((i - 1, j))
            nearby.remove((i - 1, j + 1))
            nearby.remove((i, j - 1))
            nearby.remove((i + 1, j - 1))
        
        # If the spot is in the top right corner
        elif i == 0 and j == self.width-1:
            print("top right corner")
            nearby.remove((i - 1, j + 1))
            nearby.remove((i - 1, j))
            nearby.remove((i - 1, j - 1))
            nearby.remove((i, j + 1))
            nearby.remove((i + 1, j + 1))

        # If the spot is in the bottom left corner
        elif i == self.height-1 and j == 0:
            print("bottom left corner")
            nearby.remove((i + 1, j - 1))
            nearby.remove((i + 1, j))
            nearby.remove((i + 1, j + 1))
            nearby.remove((i, j - 1))
            nearby.remove((i - 1, j - 1))
        
        # If the spot is in the bottom right corner
        elif i == self.height-1 and j == self.width-1:
            print("bottom right corner")
            nearby.remove((i + 1, j + 1))
            nearby.remove((i + 1, j))
            nearby.remove((i + 1, j - 1))
            nearby.remove((i, j + 1))
            nearby.remove((i - 1, j + 1))
        
        # If the spot is in the top row, excluding corners
        elif i == 0:
            print("top row")
            nearby.remove((i - 1, j))
            nearby.remove((i - 1, j - 1))
            nearby.remove((i - 1, j + 1))
        
        # If the spot is in the bottom row, excluding corners
        elif i == self.height-1:
            print("bottom row")
            nearby.remove((i + 1, j))
            nearby.remove((i + 1, j - 1))
            nearby.remove((i + 1, j + 1))

        # If the spot is in the leftmost column, excluding corners
        elif j == 0:
            print("leftmost row")
            nearby.remove((i, j - 1))
            nearby.remove((i - 1, j - 1))
            nearby.remove((i + 1, j - 1))

        # If the spot is in the rightmost column, excluding corners
        elif j == self.width-1:
            print("rightmost row")
            nearby.remove((i, j + 1))
            nearby.remove((i - 1, j + 1))
            nearby.remove((i + 1, j + 1))

        remove = set()
        for things in nearby:
            if things in self.moves_made:
                remove.add(things)

        nearby -= remove

        # Creates a new Sentence object to append to knowledge
        # Set the cells and count property of the Sentence before appending to knowledge
        newSentence = Sentence(nearby, count)
        self.knowledge.append(newSentence)
        # print("new sentence: ", newSentence)
        
        # If one set of cells in a sentence is a subset of another, draw inferences
        for i in range(len(self.knowledge)):
            for j in range(len(self.knowledge) - 1):
                if set(self.knowledge[i].cells).issubset(set(self.knowledge[j + 1].cells)) and len(self.knowledge[j + 1].cells) > len(self.knowledge[i].cells) and self.knowledge[j + 1].count > self.knowledge[i].count:
                    print()
                    print()
                    print("subset found ", self.knowledge[i], self.knowledge[j + 1])
                    sent = Sentence(set(self.knowledge[j + 1].cells) - set(self.knowledge[i].cells), self.knowledge[j + 1].count - self.knowledge[i].count)
                    self.knowledge.append(sent)
                    print(f"new sentence cells: {sent.cells}, count: {sent.count}")
                    print()
                    print()
        
        for sent in self.knowledge:
            knownSafes = sent.known_safes()
            for thing_ss in self.safes:
                self.mark_safe(thing_ss)
            for thing_s in knownSafes:
                self.safes.add(thing_s)
                self.mark_safe(thing_s)
                # print("known safe: ", thing_s)
            knownMines = sent.known_mines()
            for thing_mm in self.mines:
                self.mark_mine(thing_mm)
            for thing_m in knownMines:
                self.mines.add(thing_m)
                self.mark_mine(thing_m)
                # print("known mine: ", thing_m)

        res = []
        for sent in self.knowledge: 
            if sent not in res: 
                if len(sent.cells) > 0:
                    res.append(sent)
                    # print("cells", sent.cells)
                    # print("count", sent.count)
                    # print()
                    print("sentence: ", sent)
        self.knowledge = res
        safesNotPicked = set()
        for thingy in self.safes:
            if thingy not in self.moves_made:
                safesNotPicked.add(thingy)
        # print("safes", safesNotPicked)
        # print("safes count", len(safesNotPicked))
        print()



    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        knownSafes = set()
        for safe in self.safes:
            if safe not in self.moves_made:
                knownSafes.add(safe)

        if len(knownSafes) > 0:
            return random.choice(list(knownSafes))

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        knownRandoms = set()
        for i in range(self.height - 1):
            for j in range(self.width - 1):
                if (i, j) not in self.moves_made:
                    if (i, j) not in self.mines:
                        knownRandoms.add((i, j))
        
        if len(knownRandoms) > 0:
            return random.choice(list(knownRandoms))

        return None
