def process_ngram(record):
    expected_tokens = record[0]
    data = record[1].split('\t')
    
    # error checking
    if len(data) < 3:
        return []
    
    # unpack data
    ngram = data[0].split()
    year = data[1]
    count = int(data[2])
    
    # more error checking
    if len(ngram) != expected_tokens:
        return []
    
    # generate key
    pair = tuple(sorted([ngram[0], ngram[self.expected_tokens - 1]]))
    k = pair + (year,)
    
    return [(k, count)]


def process_ngram_cheat(record):
    try:
        data = record.split('\t')
        # unpack data
        ngram = data[0].split()
        year = data[1]
        count = int(data[2])
        # generate key
        pair = tuple(sorted([ngram[0], ngram[-1]]))
        k = pair + (year,)
        return [('\t'.join(k), count)]
    except Exception:
        return []
