import collections

def get_stats(vocab):
    """Compute frequency of adjacent character pairs in vocabulary."""
    pairs = collections.defaultdict(int)
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pairs[(symbols[i], symbols[i+1])] += freq
    return pairs

def merge_vocab(pair, vocab):
    """Merge the most common pair in vocabulary."""
    new_vocab = {}
    bigram = ' '.join(pair)
    replacement = ''.join(pair)
    for word in vocab:
        new_word = word.replace(bigram, replacement)
        new_vocab[new_word] = vocab[word]
    return new_vocab

# Sample vocabulary
vocab = {
    'l o w': 5,
    'l o w e r': 2,
    'n e w e s t': 6,
    'w i d e s t': 3
}

num_merges = 5  # Number of merges
for _ in range(num_merges):
    pairs = get_stats(vocab)
    if not pairs:
        break
    best_pair = max(pairs, key=pairs.get)
    vocab = merge_vocab(best_pair, vocab)
    print(f'Merged pair: {best_pair} -> {vocab}')
