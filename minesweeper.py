import itertools
import random
import importlib
import copy

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
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()
        # raise NotImplementedError

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()
        # raise NotImplementedError

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        mycell = {(cell)}
        if len(self.cells) != self.count :
            if mycell.issubset(self.cells):
                if len(self.cells) != 1:
                    self.cells.difference_update(mycell)
                    if self.count!=0:
                        self.count-=1


    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if self.count != 0:
            mycell = {(cell)}
            if len(self.cells.difference(mycell)) != 0:
                self.cells.difference_update(mycell)



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

        # Charger le module `runner`
        self.runner_module = importlib.import_module("runner")
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
    def neighborhood(self,cell):
        #return all neighbors of a cell
        myneighborhood=set()

        for line in range(cell[0]-1,cell[0]+2):
                for col in range(cell[1]-1,cell[1]+2):
                    if (line in range(0,self.height)) and (col in range(0,self.width)) and (line,col)!=cell:
                        myneighborhood.add((line,col))
        return myneighborhood

    def update_mines(self):
        # For each Sentence of the KB, I check if mines are in self.mines. If not
        # I update self.mines.
        # I do this because the mark_safe might update a sentence and thus create
        # a "mine" sentence
        for sentence in self.knowledge:
            mines = sentence.known_mines()
            for mine in mines:
                if not {mine}.issubset(self.mines):
                    self.mines.add(mine)
                    self.runner_module.flags.add(mine)
                    self.mark_mine(mine)

    #For each self.mines I update all the kb sentences in order to be consistent
        # for mine in self.mines:
        #     self.myfile2.write("\nMine (update_mine-mark_mine) : " + str(mine))
        #     self.mark_mine(mine)

    def update_safes(self):
        # For each Sentence of the KB, I check if mines are in self.mines. If not
        # I update self.mines.
        # I do this because the mark_safe might update a sentence and thus create
        # a "mine" sentence
        for sentence in self.knowledge:
            safes = sentence.known_safes()
            for safe in safes:
                if not {safe}.issubset(self.safes):
                    self.safes.add(safe)
                    self.mark_safe(safe)

    def find_subsets(self):
    #Find subsets in order to create new sentence and enhance the kb
    # Create a temporary kb to store new sentences and not modify existing kb
        temporaryknowledge = []
    #create a combination of each sentence of the knowledge and compare them
    #each other to find subsets and add it in the kb


        for s1, s2 in itertools.permutations(self.knowledge,2):

            if (len(s1.cells)!=0 and len(s2.cells)!=0) and (len(s1.cells)<len(s2.cells)):

                if s1.cells.issubset(s2.cells):
                    if s1.count <= s2.count and s1.count != 0 and s2.count != 0:
                        newcount = s2.count - s1.count
                        newcells = s2.cells.difference(s1.cells)

                        if len(newcells)!=0:
                            temporaryknowledge.append(Sentence(newcells,newcount))

        if len(temporaryknowledge)!=0:
            for sentencetobeadded in temporaryknowledge:
                if not self.knowledge.count(sentencetobeadded):
                    self.knowledge.append(sentencetobeadded)






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

        #1) Mark the cell as a move has been made

        self.moves_made.add(cell)
        # 2) mark the cell as safe since the game continue.

        self.mark_safe(cell)
        #3) add a new sentence to the AI's knowledge base
        #   based on the value of `cell` and `count`
        #
        #Get the cells around the move
        cellneighborhood = self.neighborhood(cell)
        #I use a deepcopy to avoid 'Set changed size during iteration' error
        temp_cellneighborhood=copy.deepcopy(cellneighborhood)
        #Add it in the knowledge base

        for mycell in cellneighborhood:
            #Remove cells marked as safe
            if {mycell}.issubset(self.safes):
                temp_cellneighborhood.difference_update({mycell})

            # Remove cells marked as mines
            if {mycell}.issubset(self.mines):
                temp_cellneighborhood.difference_update({mycell})
                count-=1

        if len(temp_cellneighborhood) != 0:
            cellneighborhoodsentence = Sentence(temp_cellneighborhood, count)
            self.knowledge.append(cellneighborhoodsentence)

        #4) mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base
        #With the previous mark_safe, I have to check if new mines may be
        #concluded.



        #Case Cell = 0 => Add all cells around as safe.
        # Notice that since self.safes is a set, doublets are handle by python

        if count == 0:
            for c in cellneighborhood:
                if not {c}.issubset(self.mines):
                    self.mark_safe(c)



        #Check if safes can be detected based on the kb

        safecellsfound = []
        for sentence in self.knowledge:
            safes = sentence.known_safes()
            for cell in safes:
                if not {cell}.issubset(self.safes) :
                    safecellsfound.append(cell)
        for mycell in safecellsfound:
            self.mark_safe(mycell)
            

        self.update_mines()

        self.find_subsets()
        self.update_safes()
        # raise NotImplementedError

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safes_not_played = list(self.safes.difference(self.moves_made))
        if len(safes_not_played)==0:
            return None
        else:
            return safes_not_played[0]
        # raise NotImplementedError

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        while True:
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            if not {(i,j)}.issubset(self.moves_made) and not {(i,j)}.issubset(self.mines):

                return (i,j)
        # raise NotImplementedError
