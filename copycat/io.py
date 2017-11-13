
def save_answers(answers, filename):
    answers = sorted(answers.items(), key=lambda kv : kv[1]['count'])
    keys    = [k for k, v in answers]
    counts  = [str(v['count']) for k, v in answers]
    with open(filename, 'w') as outfile:
        outfile.write(','.join(keys))
        outfile.write('\n')
        outfile.write(','.join(counts))
