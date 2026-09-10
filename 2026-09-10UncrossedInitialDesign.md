# Uncrossed
Uncrossed is a daily browser game that is a minimalist take on a crossword puzzle.

The game consists of a single "row" of crossword boxes. 

Each vertical clue is a clue that can be answered with a single letter. the answer
either works by being a real answer, or because the letter that goes in that box
"sounds like" a word that answers the clue.

The final clue is the single horizontal clue that is spelled from all of the letters.

example puzzle:

DOWN
1. Animal that makes honey
2. Mr. T was on the _-Team
3. "Sail the seven _s"
4. Disinterested affirmation

ACROSS
1. Not front but...?

ANSWER:
BACK

# Play
Users should click a square to highlight it, then enter their letter. Upon entry
it should automatically highlight the next square. After entering a letter when
all squares are filled, we should check the answer and report success or failure.

# Pre-work/Offline generation
The first task will be ensuring we have a large set of potential clues with
single letter answers. We should look for data sources that make this possible
before we just generate a bunch using LLMs. Ideally we would have many dozens
or even hundreds of possible clues to use.

# Run Time Generation
Runs should be generated from a seed that resets at midnight pacific time.

The seed should be settable using the url for testing purposes.

From our data source of valid words, pick a fairly common (using zipf) word that
is over 5 letters. Validate that we can spell it using single letter clues
that we have without repeats (ideally we have enough clues for each single
letter for this to never be a problem).

# Available offline data
We already have some available pre-made data for words and their zipf frequency,
as well as some raw dictionary dumps in T:\OtherProjects\Lexicon
