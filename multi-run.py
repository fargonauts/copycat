#!/usr/bin/env python3
import argparse, logging
from copycat import Copycat, Reporter, plot_answers, save_answers
from collections import defaultdict

class SimpleReporter(Reporter):
    """Reports results from a single run."""
    def report_answer(self, answer):
        """Self-explanatory code."""
        print('Answered %s (time %d, final temperature %.1f)' % (
            answer['answer'], answer['time'], answer['temp'],
        ))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--iterations', type=int, default=1, help='Run the given case this many times.')
    options = parser.parse_args()

    copycat = Copycat(reporter=SimpleReporter())

    with open('input/reduced_problems.csv', 'r') as infile:
        for line in infile:
            line = line.replace('\n', '')
            a, b, c = line.split(',')
            answerList = copycat.run(a, b, c, options.iterations, True)
            results = dict()
            for formula, answers in answerList:
                answers = sorted(answers.items(), key=lambda kv : kv[1]['count'])
                keys    = [k for k, v in answers]
                counts  = [v['count'] for k, v in answers]
                results[formula] = (keys, counts)

            originalCounts = defaultdict(lambda : 0)
            originalCounts.update(dict(zip(*results['original'])))
            
            for formula, (keys, counts) in results.items():
                if formula != 'original':
                    chi2 = 0
                    for answer, count in zip(keys, counts):
                        originalCount = originalCounts[answer] 
                        if originalCount != 0:
                            chi2 += (count + originalCount) ** 2 / originalCount
                    print((formula, chi2))



                #for answer, d in sorted(iter(answers.items()), key=lambda kv: kv[1]['avgtemp']):
                    #print('%s: %d (avg time %.1f, avg temp %.1f)' % (answer, d['count'], d['avgtime'], d['avgtemp']))


            #filename = 'output/{}-{}-{}.csv'.format(a, b, c)
            #save_answers(answers, filename)

if __name__ == '__main__':
    main()
