import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # For someone in one_gene and have_trait: the prob that they have one gene and the trait
    # For someone in two_genes and have_trait: the prob that they have two genes and the trait
    # For someone in have_trait: the prob that they have the trait and have 0 genes
    # For someone in none of them: the prob that they do not have trait and have 0 genes

    # print("People in one gene", one_gene)
    # print("People in two genes", two_genes)
    # print("People in have trait", have_trait)
    # print("People in people", people)

    # Initialize total probability to 1
    probTotal = 1

    for name in people:

        probFather = 0
        probMother = 0
        probGene = 0
        probTrait = 0


        # If the person has parents in the dict
        if people[name]['father'] is not None:

            # Probabilities that the father passed on his gene
            if people[name]['father'] in one_gene:
                probFather = 0.5
            elif people[name]['father'] in two_genes:
                probFather = 1 - PROBS['mutation']
            else:
                probFather = PROBS['mutation']

            # Probabilities that the mother passed on her gene
            if people[name]['mother'] in one_gene:
                probMother = 0.5
            elif people[name]['mother'] in two_genes:
                probMother = 1 - PROBS['mutation']
            else:
                probMother = PROBS['mutation']

            # Determine probabilities that the person has 1, 2, or 0 genes based on parents
            if name in one_gene:
                probGene = (probFather * (1 - probMother)) + (probMother * (1 - probFather))
            elif name in two_genes:
                probGene = probFather * probMother  
            else:
                probGene = (1 - probFather) * (1 - probMother)

        else:

            # If the person has no parents, use PROBS constants
            if name in one_gene:
                probGene = PROBS["gene"][1]
            elif name in two_genes:
                probGene = PROBS["gene"][2]
            else:
                probGene = PROBS["gene"][0]

            
        # Find probability that the individual has the trait
        if name in have_trait:
            if name in one_gene:
                probTrait = PROBS["trait"][1][True]
            elif name in two_genes:
                probTrait = PROBS["trait"][2][True]
            else:
                probTrait = PROBS["trait"][0][True]
        else:
            if name in one_gene:
                probTrait = PROBS["trait"][1][False]
            elif name in two_genes:
                probTrait = PROBS["trait"][2][False]
            else:
                probTrait = PROBS["trait"][0][False]

        probTotal *= probGene * probTrait

    return probTotal


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """

    for person in probabilities:

        if person in one_gene:
            probabilities[person]['gene'][1] += p
        elif person in two_genes:
            probabilities[person]['gene'][2] += p
        else:
            probabilities[person]['gene'][0] += p
        if person in have_trait:
            probabilities[person]['trait'][True] += p
        else:
            probabilities[person]['trait'][False] += p



def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    for person in probabilities:

        sum = 0


        minGene = findMinGene(probabilities[person]['gene'][0], probabilities[person]['gene'][1], probabilities[person]['gene'][2])
        minTrait = findMinTrait(probabilities[person]['trait'][True], probabilities[person]['trait'][False])

        for geneNum in probabilities[person]['gene']:

            probabilities[person]['gene'][geneNum] /= minGene
            
            sum += probabilities[person]['gene'][geneNum]
        
        product = 1.0 / sum

        for geneNum in probabilities[person]['gene']:

            probabilities[person]['gene'][geneNum] *= product

        sum = 0

        for traitVal in probabilities[person]['trait']:

            probabilities[person]['trait'][traitVal] /= minTrait

            sum += probabilities[person]['trait'][traitVal]
        
        product = 1 / sum

        for traitVal in probabilities[person]['trait']:

            probabilities[person]['trait'][traitVal] *= product



def findMinGene(num1, num2, num3):

    minVal = 0

    if num1 == 0:
        minVal = min(num2, num3)
    elif num2 == 0:
        minVal = min(num1, num3)
    elif num3 == 0:
        minVal = min(num1, num2)
    else:
        minVal = min(num1, num2, num3)
    
    return minVal


def findMinTrait(num1, num2):

    minVal = 0

    if num1 == 0:
        minVal = num2
    elif num2 == 0:
        minVal = num1
    else:
        minVal = min(num1, num2)

    return minVal



if __name__ == "__main__":
    main()
