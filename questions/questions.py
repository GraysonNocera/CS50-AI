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

    dictionary = dict()

    for dirName, subdirList, fileList in os.walk(directory):
        for fileName in fileList:
            filePath = os.path.join(directory, fileName)
            with open(filePath, 'r') as f:
                dictionary[fileName] = f.read()

    return dictionary


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    tokens = nltk.word_tokenize(document)

    processedTokens = []

    for token in tokens:
        token = token.lower()
        if token not in string.punctuation and token not in nltk.corpus.stopwords.words("english"):
            processedTokens.append(token)

    return processedTokens


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    dictionary = dict()

    for listWords in documents.values():
        for word in listWords:
            sumDocuments = 0
            if word not in dictionary.keys():
                for listWords in documents.values():
                    if word in listWords:
                        sumDocuments += 1

                dictionary[word] = math.log(len(documents.keys()) / sumDocuments)
            
    return dictionary


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    dictTopFiles = dict()

    for fileName, words in files.items():
        sumTFIDF = 0
        for word in set(words):
            if word in query:
                sumTFIDF += (idfs[word] * words.count(word))
        dictTopFiles[fileName] = sumTFIDF

    sortedDict = sorted(dictTopFiles.items(), key=lambda x: x[1], reverse=True)
    listFiles = list()

    for i in sortedDict:
        listFiles.append(i[0])

    return listFiles[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    dictTopFiles = dict()

    for sentence, words in sentences.items():
        sumIDF = 0
        for word in set(words):
            if word in query:
                sumIDF += idfs[word]
                
        dictTopFiles[sentence] = sumIDF

    sortedList = sorted(dictTopFiles.items(), key=lambda x: x[1], reverse=True)

    for i in range(0, n + 10):
        numSame = 0
        for tup in sortedList:
            if math.isclose(sortedList[i][1], tup[1]):
                numSame += 1

        tempList = sortedList[i:(i + numSame)]

        enum = 0
        for temp in tempList:
            words = sentences[temp[0]]
            sumInQuery = 0
            for word in words:
                if word in query:
                    sumInQuery += 1
            temp = (temp[0], sumInQuery / len(words))
            tempList[enum] = temp
            enum += 1
            
        sortedTempList = sorted(tempList, key = lambda x: x[1], reverse=True)
        index = 0

        if len(sortedTempList) > 1:
            for j in range(i, i+numSame):
                sortedList[j] = sortedTempList[index]
                index += 1

        i += numSame

    listFiles = list()
    for i in sortedList:
        listFiles.append(i[0])

    return listFiles[:n]


if __name__ == "__main__":
    main()
