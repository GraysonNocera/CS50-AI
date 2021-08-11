import os
import random
import re
import sys
from collections import Counter

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    probs = {}
    # print("page")
    # print(page)

    # If the page has no outgoing links, randomly select a page in corpus
    if corpus[page] == 0:

        equalProb = 1 / corpus.len()

        for key, value in corpus.items():
            probs[key] = equalProb
        
        return probs

    # Add the probability that the next page will be the current page
    if len(corpus[page]) > 0:
        probs[page] = (1 - damping_factor) / len(corpus[page])
    else:
        probs[page] = 0

    # With probability damping_factor, the surfer randomly chooses one of the links from page with equal probability
    # With probability 1 - damping_factor, the surfer randomly chooses of the pages in corpus with equal probability
    if len(corpus[page]) > 0:
        equalProb = 1 / len(corpus[page])
    else:
        # If the page has no outgoing links, we randomly choose one page from corpus
        for key in corpus:
            probs[key] = 1 / len(corpus.keys())
            return probs
        
    for value in corpus[page]:
        probs[value] = equalProb + (probs[page])
    
    return probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # PageRank for each page
    probs = {}

    # Keeps track of our path of visited sites
    pagesVisited = []

    firstSample = random.choice(list(corpus.keys()))
    pagesVisited.append(firstSample)

    d = 1
    while (d < n):

        # print("pagesVisited")
        # print(pagesVisited)
        prevPage = pagesVisited[d - 1]
        # print("prevPage")
        # print(prevPage)
        probPrevPage = transition_model(corpus, prevPage, damping_factor)
        newPage = random.choices(list(probPrevPage.keys()), list(probPrevPage.values()), k=1)
        pagesVisited.append(newPage[0])
        
        # print(d)
        d += 1

    count = Counter(pagesVisited)
    occurences = count.most_common(len(pagesVisited))
    
    # for page in pagesVisited:

    #     if page not in occurences.keys():

    #         occurences[page] = 
    
    for x in occurences:

        probs[x[0]] = x[1] / SAMPLES

    return probs


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    probs = {}

    for key in corpus:

        probs[key] = 1 / len(corpus.keys())

    stop = 0
    while not stop:

        stop = 1
        
        for i in probs.keys():

            temp = probs[i]

            probs[i] = (1 - damping_factor) / len(corpus)

            for key, value in corpus.items():
                if i in value:
                    probs[i] += damping_factor * probs[key] / len(value)

            if abs(temp - probs[i]) > 0.001:
                stop = 0

    return probs




if __name__ == "__main__":
    main()
