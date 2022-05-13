import chunk
import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP EVP | S Conj S | S Conj EVP
NP -> N | Det N | AA N | N PPP | Det AA N | Det N PPP | AA N PPP | Det AA N PPP
VP -> V | V NP | V PP | V NP PP 

PPP -> PP | PP PPP
PP -> P NP
AA -> Adj | Adj AA
EVP -> VP | Adv VP | VP Adv

"""
# PP means prepositional phrase
# PPP means one or more PP
# AA means one or more adjectives
# EVP means extended verbe phrase

# NP seem specific but its just a conbination of a noun (always), 0 or 1 determiners, at least 0 prepositional phrases, and at least 0 adjectives


grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    sentence = sentence.lower() #All characters to lowercase
    tokenized = nltk.word_tokenize(sentence) #Turns sentence into a list
    final_list = [] #Creates the list to be returned

    for word in tokenized: #Removes words from tokenized, that don't have alphabetic characters

        has_alphabetic = False

        for character in word:

            if 96<ord(character)<123: #ascii of a is 97 and ascci of z 122

                has_alphabetic = True
        
        if has_alphabetic:

            final_list.append(word)

    return final_list


def has_sub_np(tree):
    """
    Checks whether a tree contains a NP subtree. 
    True if the tree contains a NP subtree,
    False if not.
    """
    label = tree.label()

    if label == "NP":

        return True

    elif label in ["Adv","Adj","Conj","Det","N","P","V","AA"]: #Checks if it's terminal or if it can't contain a NP subtree

        return False
    
    for subtree in tree:

        if has_sub_np(subtree): #Recursive step

            return True
    
    return False


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunks = []

    for subtree in tree:

        label = subtree.label()

        if has_sub_np(subtree) and label not in ["Adv","Adj","Conj","Det","N","P","V","AA"]: #Checks if the subtree has a NP, and the label can contain a NP,
                                                                                             #otherwise goes to the next subtree
            subsubtree = np_chunk(subtree) # Gets recursive np_chunks

            for chunk in subsubtree:
                
                chunks.append(chunk)

    if tree.label() == "NP" and chunks == []: #Checks if the main tree is itself an np_chunk

        chunks.append(tree)

    return chunks


if __name__ == "__main__":
    main()
