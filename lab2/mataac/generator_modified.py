import random

def getWords(filename):
    fp = open(filename)
    temp_list = list()
    for each_line in fp:
        each_line = each_line.strip()
        temp_list.append(each_line)
    words = tuple(temp_list)
    fp.close()
    return words
articles = getWords('articles.txt')
nouns = getWords('nouns.txt')
verbs = getWords('verbs.txt')
prepositions = getWords('prepositions.txt')

def sentence():
    return nounphrase() + " " + verbphrase()
def nounphrase():
    return random.choice(articles) + " " + random.choice(nouns)
def verbphrase():
    return random.choice(verbs) + " " + nounphrase() + " " + prepositionsphrase()
def prepositionsphrase():
    return random.choice(prepositions) + " " + nounphrase()
def main():
    number = int(input('Enter number of sentences: '))
    for count in range(number):
        print(sentence())
if __name__=='__main__':
    main()
