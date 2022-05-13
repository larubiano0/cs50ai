import os
import random
import re
import sys
import copy

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
    probDistribution = {}
    allNodes = list(corpus.keys())
    nAll = len(allNodes)
    adjacent = list(corpus[page])
    nAdjacent = len(adjacent)
    for i in allNodes:
        probDistribution[i] = 0
    for i in adjacent:
        probDistribution[i] = probDistribution[i] + damping_factor/nAdjacent
    for i in allNodes:
        probDistribution[i] = probDistribution[i] + (1 - damping_factor)/nAll
    return probDistribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    #First sample
    visits = {}
    allNodes = list(corpus.keys())
    for i in allNodes:
        visits[i] = 0

    firstPage = random.choice(allNodes)
    visits[firstPage] = visits[firstPage] + 1

    distributions = transition_model(corpus,firstPage,damping_factor)

    #Next samples
    while n>1:
        nextPage = (random.choices(list(distributions.keys()), weights = list(distributions.values()), k=1))[0]
        visits[nextPage] = visits[nextPage] + 1

        distributions = transition_model(corpus,nextPage,damping_factor)

        n-=1

    #Getting the pagerank value from visits
    totalVisits = sum(visits.values())

    for i in allNodes:
        visits[i] = (visits[i]) / (totalVisits)

    return visits
    

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    allNodes = list(corpus.keys())
    nAll = len(allNodes)

    probDistribution = {}
    for i in allNodes:
        probDistribution[i] = 1/nAll

    maxChange = float('inf')

    while maxChange>0.001:

        newProbDistribution = copy.deepcopy(probDistribution)
        maxInnerChange = 0

        for p in allNodes:

            newValue = (1 - damping_factor)/nAll
            sumation = 0
            
            for i in allNodes:

                if p in corpus[i]:
                    sumation += probDistribution[i] / len(corpus[i])

            newValue += damping_factor * sumation


            oldValue = probDistribution[p]

            newProbDistribution[p] = newValue

            if abs(newValue-oldValue)>=maxInnerChange:
                maxInnerChange = abs(newValue-oldValue)
            
        if maxInnerChange < maxChange:
            maxChange = maxInnerChange

        probDistribution = newProbDistribution


    return probDistribution

if __name__ == "__main__":
    main()
