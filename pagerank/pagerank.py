import os
import random
import re
import sys

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
    outgoing_links = corpus[page]
    if len(outgoing_links) == 0:
        for p in corpus:
            probs[p] = 1 / len(corpus)
    else:
        all_link_prob = (1 - damping_factor) / len(corpus)
        inside_link_prob = damping_factor / len(outgoing_links)
        for link in corpus:
            if link not in outgoing_links:
                probs[link] = all_link_prob
            else:
                probs[link] = inside_link_prob + all_link_prob

    return probs


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probs = {page: 0 for page in corpus}
    page = random.choice(tuple(corpus))
    for _ in range(n):
        model = transition_model(corpus, page, damping_factor)
        rand = random.uniform(0, 1)
        span = 0
        for p in corpus:
            span += model[p]
            if rand < span:
                page = p
                probs[p] += 1
                break

    for prob in probs:
        probs[prob] /= n

    return probs


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    n = len(corpus)
    probs = {page: 1 / n for page in corpus}
    while True:
        new_probs = {}
        max_change = 0
        for page in corpus:
            rank = (1 - damping_factor) / n
            for link in corpus:
                if page in corpus[link]:
                    rank += damping_factor * probs[link] / len(corpus[link])
                elif len(corpus[link]) == 0:
                    rank += damping_factor * probs[link] / n

            new_probs[page] = rank
            max_change = max(max_change, abs(probs[page] - new_probs[page]))
        probs = new_probs
        if max_change < 0.001:
            return probs





if __name__ == "__main__":
    main()
