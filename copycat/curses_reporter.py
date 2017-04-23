import curses
from copycat import Reporter


class CursesReporter(Reporter):
    def __init__(self, window):
        curses.curs_set(0)  # hide the cursor
        height, width = window.getmaxyx()
        slipnetHeight = 10
        coderackHeight = height - 15
        answersHeight = 5
        self.temperatureWindow = window.derwin(height, 5, 0, 0)
        self.slipnetWindow = curses.newwin(slipnetHeight, width-5, 0, 5)
        self.coderackWindow = curses.newwin(coderackHeight, width-5, slipnetHeight, 5)
        self.answersWindow = curses.newwin(answersHeight, width-5, slipnetHeight + coderackHeight, 5)
        for w in [self.temperatureWindow, self.slipnetWindow, self.answersWindow]:
            w.clear()
            w.border()
            w.refresh()
        self.answers = {}

    def report_answer(self, answer):
        d = self.answers.setdefault(answer['answer'], {
            'answer': answer['answer'],
            'count': 0,
            'sumtime': 0,
            'sumtemp': 0,
        })
        d['count'] += 1
        d['sumtemp'] += answer['temp']
        d['sumtime'] += answer['time']
        d['avgtemp'] = d['sumtemp'] / d['count']
        d['avgtime'] = d['sumtime'] / d['count']

        def fitness(d):
            return 3 * d['count'] - d['avgtemp']

        def represent(d):
            return '%s: %d (avg time %.1f, avg temp %.1f)' % (
                d['answer'], d['count'], d['avgtime'], d['avgtemp'],
            )

        answersToPrint = sorted(self.answers.itervalues(), key=fitness, reverse=True)

        w = self.answersWindow
        pageWidth = w.getmaxyx()[1]
        if pageWidth >= 96:
            columnWidth = (pageWidth - 6) / 2
            for i, d in enumerate(answersToPrint[:3]):
                w.addnstr(i+1, 2, represent(d), columnWidth)
            for i, d in enumerate(answersToPrint[3:6]):
                w.addnstr(i+1, pageWidth - columnWidth - 2, represent(d), columnWidth)
        else:
            columnWidth = pageWidth - 4
            for i, d in enumerate(answersToPrint[:3]):
                w.addnstr(i+1, 2, represent(d), columnWidth)
        w.refresh()

    def report_coderack(self, coderack):
        NUMBER_OF_BINS = 7

        # Combine duplicate codelets for printing.
        counts = {}
        for c in coderack.codelets:
            assert 1 <= c.urgency <= NUMBER_OF_BINS
            key = (c.urgency, c.name)
            counts[key] = counts.get(key, 0) + 1

        # Sort the most common and highest-urgency codelets to the top.
        entries = sorted(
            (count, key[0], key[1])
            for key, count in counts.iteritems()
        )

        # Figure out how we'd like to render each codelet's name.
        printable_entries = [
            (urgency, '%s (%d)' % (name, count))
            for count, urgency, name in entries
        ]

        # Render each codelet in the appropriate column,
        # as close to the top of the page as physically possible.
        w = self.coderackWindow
        pageHeight, pageWidth = w.getmaxyx()
        columnWidth = (pageWidth - len('important-object-correspondence-scout (n)')) / (NUMBER_OF_BINS - 1)

        def is_vacant(y, x):
            return (w.inch(y, x) & 0xFF) == 0x20

        w.erase()
        for u, string in printable_entries:
            # Find the highest point on the page where we could place this entry.
            start_column = (u - 1) * columnWidth
            end_column = start_column + len(string)
            for r in range(pageHeight):
                if all(is_vacant(r, c) for c in xrange(start_column, end_column+20)):
                    w.addstr(r, start_column, string)
                    break
        w.refresh()

    def report_slipnet(self, slipnet):
        w = self.slipnetWindow
        pageHeight, pageWidth = w.getmaxyx()
        w.erase()
        w.addstr(1, 2, 'Total: %d slipnodes and %d sliplinks' % (
            len(slipnet.slipnodes),
            len(slipnet.sliplinks),
        ))

        def name_and_attr(node):
            if node.activation == 100:
                return (node.name.upper(), curses.A_STANDOUT)
            if node.activation > 50:
                return (node.name.upper(), curses.A_BOLD)
            else:
                return (node.name.lower(), curses.A_NORMAL)

        for c, node in enumerate(slipnet.letters):
            s, attr = name_and_attr(node)
            w.addstr(2, 2 * c + 2, s, attr)
        for c, node in enumerate(slipnet.numbers):
            s, attr = name_and_attr(node)
            w.addstr(3, 2 * c + 2, s, attr)
        row = 4
        column = 2
        for node in slipnet.slipnodes:
            if node not in slipnet.letters + slipnet.numbers:
                s, attr = name_and_attr(node)
                if column + len(s) > pageWidth - 1:
                    row += 1
                    column = 2
                w.addstr(row, column, s, attr)
                column += len(s) + 1
        w.border()
        w.refresh()

    def report_temperature(self, temperature):
        height = self.temperatureWindow.getmaxyx()[0]
        max_mercury = height - 4
        mercury = max_mercury * temperature.value() / 100.0
        for i in range(max_mercury):
            ch = ' ,o%8'[int(4 * min(max(0, mercury - i), 1))]
            self.temperatureWindow.addstr(max_mercury - i, 1, 3*ch)
        self.temperatureWindow.addnstr(height - 2, 1, '%3d' % temperature.actual_value, 3)
        self.temperatureWindow.refresh()
