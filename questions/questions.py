import nltk
import sys
import os
import string
import math

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    dict = {}

    for file in os.listdir(directory): #For each filename in the directory
        path = os.path.join(directory, file) #corpus/python.txt
        f = open(path, "r")                 #file
        dict[file] = f.read()               
    return dict


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    #Part of the code was taken from parser.py
    sentence = document.lower() #All characters to lowercase
    tokenized = nltk.word_tokenize(sentence) #Turns sentence into a list

    final_list = [] #Creates the list to be returned

    for word in tokenized:

        if word not in string.punctuation and word not in nltk.corpus.stopwords.words("english"): #Two conditions

            final_list.append(word)
    
    return final_list


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    IDF_dictionary = {} #Dictionary that maps words to IDF values
    word_dictionary = {} #Dictionary to maps words to the number of documents that contain word

    totalDocuments = len(documents)

    for doc, text in documents.items(): #iterate over the documents and their texts

        words_in_document = set() #Set that contains words that appear in a document (not repeated elements)

        for word in text:

            words_in_document.add(word) #Adds word to word_dictionary
        
        for word in words_in_document: #iterate over all the words in the document (unique)
            
            if word in word_dictionary:

                word_dictionary[word] = word_dictionary[word] + 1 #If the word has appeared in another document, add 1 to the number of documents it has been on

            else: 

                word_dictionary[word] = 1 #If the word hasnt appeared in another document, set to 1 the number of documents it has been on

    for word, appearances in word_dictionary.items():
        
        IDF_dictionary[word] = math.log(totalDocuments/appearances) #Find IDF value

    return IDF_dictionary


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """

    tf_idf = {} #Dictionary mapping documents to their tf-idf values
    
    for doc, text in files.items(): #Iterate over the files

        words = {} #Dictionary mapping words to their frecuency on a document
        
        for word in text: #Iterate over all the words in the document

            if word in query: #Check if the word is in query

                if word in words: 

                    words[word] = words[word] + 1 #If the word has appeared in the document, add 1 to the number of frequencies

                else:

                    words[word] = 1 #Set to 1 the number of frequencies of word in document
        
        total_tf_idf = 0
 
        for word in query: #Multiplies tf by idfs to get tf-idfs if word is in words and in idfs

            if word in words and word in idfs: 

                total_tf_idf += words[word] * idfs[word]

        tf_idf[doc] = total_tf_idf

    top_tf_idf = sorted(tf_idf.items(), key=lambda x:x[1], reverse=True) #List of tuples ordered by tf-idf
    
    final_list = []

    for i in range(n):

        final_list.append(top_tf_idf[i][0])

    return final_list        


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    returned_sentences = []

    sentence_matching_word_measure = {} #Dictionary that maps sentences to a tuple (the sum of IDF values of the words that are both in sentence and in query, #of words in query)

    for sentence, words in sentences.items():
    
        mwm = 0 #Matching word measure of a sentence
        words_in_query = 0

        for word in words:

            if word in query:

                mwm += idfs[word]
                words_in_query += 1

        sentence_matching_word_measure[sentence] = (mwm,words_in_query)
    
    top_sentences = sorted(sentence_matching_word_measure.items(), key=lambda x:x[1][0], reverse=True) #List of tuples ordered by mwm

    top_sentences_by_mwm = {} #Ordered list of lists, ordered by mwm

    for sentence, tup in top_sentences:

        mwm , words_in_query = tup

        if mwm in top_sentences_by_mwm:  #Creates list of sentences associated with a mwm
            top_sentences_by_mwm[mwm] = top_sentences_by_mwm[mwm] + [(sentence,words_in_query)]

        else: 
            top_sentences_by_mwm[mwm] = [(sentence,words_in_query)]

    i = 0 #Number to count the number of sentences that have been added to returned_sentences

    for mwm, ss in top_sentences_by_mwm.items(): #Iterate over the mwm values from highest to lowest

        if i == n:

            return returned_sentences

        if len(ss) == 1: #If they are no ties append sentence to returned_sentences
            
            returned_sentences.append(ss[0][0])
            i+=1

        else:

            query_term_density = {} #Sentences mapped to query term density 
            
            for sentence, words_in_query in ss:

                query_term_density[sentence] = words_in_query/len(sentences[sentence])
            
            for key, value in sorted(query_term_density.items(), key=lambda item: item[1], reverse=True): #Order query term density by its values, append sentences until n or qtd is over.

                if i == n:

                    return returned_sentences

                else:

                    returned_sentences.append(value)

    return returned_sentences

if __name__ == "__main__":
    main()

# python3 questions.py corpus