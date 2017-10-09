import curses
import time

from .copycat import Reporter
from .bond import Bond
from .correspondence import Correspondence
from .description import Description
from .group import Group
from .letter import Letter
from .rule import Rule


class SafeSubwindow(object):
    def __init__(self, window, h, w, y, x):
        self.w = window.derwin(h, w, y, x)

    def addnstr(self, y, x, s, n):
        self.w.addnstr(y, x, s, n)

    def addstr(self, y, x, s, attr=curses.A_NORMAL):
        try:
            self.w.addstr(y, x, s, attr)
        except Exception as e:
            if str(e) != 'addstr() returned ERR':
                raise

    def border(self):
        self.w.border()

    def derwin(self, h, w, y, x):
        return self.w.derwin(h, w, y, x)

    def erase(self):
        self.w.erase()

    def getch(self):
        self.w.nodelay(True)  # make getch() non-blocking
        return self.w.getch()

    def getmaxyx(self):
        return self.w.getmaxyx()

    def is_vacant(self, y, x):
        ch_plus_attr = self.w.inch(y, x)
        if ch_plus_attr == -1:
            return True  # it's out of bounds
        return (ch_plus_attr & 0xFF) == 0x20

    def refresh(self):
        self.w.refresh()


class CursesReporter(Reporter):
    def __init__(self, window, focus_on_slipnet=False, fps_goal=None):
        curses.curs_set(0)  # hide the cursor
        curses.noecho()  # hide keypresses
        height, width = window.getmaxyx()
        if focus_on_slipnet:
            upperHeight = 10
        else:
            upperHeight = 25
        answersHeight = 5
        coderackHeight = height - upperHeight - answersHeight
        self.focusOnSlipnet = focus_on_slipnet
        self.fpsGoal = fps_goal
        self.temperatureWindow = SafeSubwindow(window, height, 5, 0, 0) # TODO: use entropy (entropyWindow)
        self.upperWindow = SafeSubwindow(window, upperHeight, width-5, 0, 5)
        self.coderackWindow = SafeSubwindow(window, coderackHeight, width-5, upperHeight, 5)
        self.answersWindow = SafeSubwindow(window, answersHeight, width-5, upperHeight + coderackHeight, 5)
        self.fpsWindow = SafeSubwindow(self.answersWindow, 3, 9, answersHeight - 3, width - 14)
        for w in [self.temperatureWindow, self.upperWindow, self.answersWindow, self.fpsWindow]:
            w.erase()
            w.border()
            w.refresh()
        self.answers = {}
        self.fpsTicks = 0
        self.fpsSince = time.time()
        self.fpsMeasured = 100  # just a made-up number at first
        self.fpsDelay = 0

    def do_keyboard_shortcuts(self):
        w = self.temperatureWindow  # just a random window
        ordch = w.getch()
        if ordch in [ord('P'), ord('p')]:
            w.addstr(0, 0, 'PAUSE', curses.A_STANDOUT)
            w.refresh()
            ordch = None
            while ordch not in [ord('P'), ord('p'), 27, ord('Q'), ord('q')]:
                time.sleep(0.1)
                ordch = w.getch()
            self.fpsTicks = 0
            self.fpsSince = time.time()
            w.erase()
            w.border()
            w.refresh()
        if ordch in [27, ord('Q'), ord('q')]:
            raise KeyboardInterrupt()
        if ordch in [ord('F')]:
            self.fpsGoal = (self.fpsGoal or self.fpsMeasured) * 1.25
        if ordch in [ord('f')]:
            self.fpsGoal = (self.fpsGoal or self.fpsMeasured) * 0.8


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

        answersToPrint = sorted(iter(self.answers.values()), key=fitness, reverse=True)

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

    def depict_fps(self):
        w = self.fpsWindow
        now = time.time()
        elapsed = now - self.fpsSince
        fps = self.fpsTicks / elapsed
        if self.fpsGoal is not None:
            seconds_of_work_per_frame = (elapsed / self.fpsTicks) - self.fpsDelay
            desired_time_working_per_second = self.fpsGoal * seconds_of_work_per_frame
            if desired_time_working_per_second < 1.0:
                self.fpsDelay = (1.0 - desired_time_working_per_second) / fps
            else:
                self.fpsDelay = 0
        w.addstr(1, 1, 'FPS:%3d' % fps, curses.A_NORMAL)
        w.refresh()
        self.fpsSince = now
        self.fpsTicks = 0
        self.fpsMeasured = fps

    def report_coderack(self, coderack):
        self.fpsTicks += 1  # for the purposes of FPS calculation
        if self.fpsDelay:
            time.sleep(self.fpsDelay)
        if time.time() > self.fpsSince + 1.200:
            self.depict_fps()

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
            for key, count in counts.items()
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

        w.erase()
        for u, string in printable_entries:
            # Find the highest point on the page where we could place this entry.
            start_column = int((u - 1) * columnWidth)
            end_column = start_column + len(string)
            for r in range(pageHeight):
                if all(w.is_vacant(r, c) for c in range(start_column, end_column+20)):
                    w.addstr(r, start_column, string)
                    break
        w.refresh()

    def slipnode_name_and_attr(self, slipnode):
        if slipnode.activation == 100:
            return (slipnode.name.upper(), curses.A_STANDOUT)
        if slipnode.activation > 50:
            return (slipnode.name.upper(), curses.A_BOLD)
        else:
            return (slipnode.name.lower(), curses.A_NORMAL)

    def report_slipnet(self, slipnet):
        if not self.focusOnSlipnet:
            return
        w = self.upperWindow
        pageHeight, pageWidth = w.getmaxyx()
        w.erase()
        w.addstr(1, 2, 'Total: %d slipnodes and %d sliplinks' % (
            len(slipnet.slipnodes),
            len(slipnet.sliplinks),
        ))

        for c, node in enumerate(slipnet.letters):
            s, attr = self.slipnode_name_and_attr(node)
            w.addstr(2, 2 * c + 2, s, attr)
        for c, node in enumerate(slipnet.numbers):
            s, attr = self.slipnode_name_and_attr(node)
            w.addstr(3, 2 * c + 2, s, attr)
        row = 4
        column = 2
        for node in slipnet.slipnodes:
            if node not in slipnet.letters + slipnet.numbers:
                s, attr = self.slipnode_name_and_attr(node)
                if column + len(s) > pageWidth - 1:
                    row += 1
                    column = 2
                w.addstr(row, column, s, attr)
                column += len(s) + 1
        w.border()
        w.refresh()

    #TODO: use entropy
    def report_temperature(self, temperature):
        self.do_keyboard_shortcuts()
        w = self.temperatureWindow
        height = w.getmaxyx()[0]
        max_mercury = height - 4
        mercury = max_mercury * temperature.value() / 100.0
        for i in range(max_mercury):
            ch = ' ,o%8'[int(4 * min(max(0, mercury - i), 1))]
            w.addstr(max_mercury - i, 1, 3*ch)
        w.addnstr(height - 2, 1, '%3d' % temperature.actual_value, 3)
        w.refresh()

    def length_of_workspace_object_depiction(self, o, description_structures):
        result = len(str(o))
        if o.descriptions:
            result += 2
            result += 2 * (len(o.descriptions) - 1)
            for d in o.descriptions:
                s, _ = self.slipnode_name_and_attr(d.descriptor)
                result += len(s)
                if d not in description_structures:
                    result += 2
            result += 1
        return result

    def depict_workspace_object(self, w, row, column, o, maxImportance, description_structures):
        if maxImportance != 0.0 and o.relativeImportance == maxImportance:
            attr = curses.A_BOLD
        else:
            attr = curses.A_NORMAL
        w.addstr(row, column, str(o), attr)
        column += len(str(o))
        if o.descriptions:
            w.addstr(row, column, ' (', curses.A_NORMAL)
            column += 2
            for i, d in enumerate(o.descriptions):
                if i != 0:
                    w.addstr(row, column, ', ', curses.A_NORMAL)
                    column += 2
                s, attr = self.slipnode_name_and_attr(d.descriptor)
                if d not in description_structures:
                    s = '[%s]' % s
                w.addstr(row, column, s, attr)
                column += len(s)
            w.addstr(row, column, ')', curses.A_NORMAL)
            column += 1
        return column

    def depict_bond(self, w, row, column, bond):
        slipnet = bond.ctx.slipnet
        if bond.directionCategory == slipnet.right:
            s = '-- %s -->' % bond.category.name
        elif bond.directionCategory == slipnet.left:
            s = '<-- %s --' % bond.category.name
        elif bond.directionCategory is None:
            s = '<-- %s -->' % bond.category.name
        if isinstance(bond.leftObject, Group):
            s = 'G' + s
        if isinstance(bond.rightObject, Group):
            s = s + 'G'
        w.addstr(row, column, s, curses.A_NORMAL)
        return column + len(s)

    def depict_grouping_brace(self, w, firstrow, lastrow, column):
        if firstrow == lastrow:
            w.addstr(firstrow, column, '}', curses.A_NORMAL)
        else:
            w.addstr(firstrow, column, '\\', curses.A_NORMAL)
            w.addstr(lastrow, column, '/', curses.A_NORMAL)
            for r in range(firstrow + 1, lastrow):
                w.addstr(r, column, '|', curses.A_NORMAL)

    def report_workspace(self, workspace):
        if self.focusOnSlipnet:
            return
        slipnet = workspace.ctx.slipnet
        w = self.upperWindow
        pageHeight, pageWidth = w.getmaxyx()
        w.erase()
        w.addstr(1, 2, '%d objects (%d letters in %d groups), %d other structures (%d bonds, %d correspondences, %d descriptions, %d rules)' % (
            len(workspace.objects),
            len([o for o in workspace.objects if isinstance(o, Letter)]),
            len([o for o in workspace.objects if isinstance(o, Group)]),
            len(workspace.structures) - len([o for o in workspace.objects if isinstance(o, Group)]),
            len([o for o in workspace.structures if isinstance(o, Bond)]),
            len([o for o in workspace.structures if isinstance(o, Correspondence)]),
            len([o for o in workspace.structures if isinstance(o, Description)]),
            len([o for o in workspace.structures if isinstance(o, Rule)]),
        ))

        group_objects = {o for o in workspace.objects if isinstance(o, Group)}
        letter_objects = {o for o in workspace.objects if isinstance(o, Letter)}
        group_and_letter_objects = group_objects | letter_objects
        assert set(workspace.objects) == group_and_letter_objects
        assert group_objects <= set(workspace.structures)

        latent_groups = {o.group for o in workspace.objects if o.group is not None}
        assert latent_groups <= group_objects
        assert group_objects <= latent_groups
        member_groups = {o for g in group_objects for o in g.objectList if isinstance(o, Group)}
        assert member_groups <= group_objects

        bond_structures = {o for o in workspace.structures if isinstance(o, Bond)}
        known_bonds = {o.leftBond for o in group_and_letter_objects if o.leftBond is not None}
        known_bonds |= {o.rightBond for o in group_and_letter_objects if o.rightBond is not None}
        assert known_bonds == bond_structures

        description_structures = {o for o in workspace.structures if isinstance(o, Description)}
        latent_descriptions = {d for o in group_and_letter_objects for d in o.descriptions}
        assert description_structures <= latent_descriptions

        current_rules = set([workspace.rule]) if workspace.rule is not None else set()

        correspondences_between_initial_and_target = {o for o in workspace.structures if isinstance(o, Correspondence)}

        assert set(workspace.structures) == set.union(
            group_objects,
            bond_structures,
            description_structures,
            current_rules,
            correspondences_between_initial_and_target,
        )
        for g in group_objects:
            assert g.string in [workspace.initial, workspace.modified, workspace.target]

        row = 2
        for o in current_rules:
            w.addstr(row, 2, str(o), curses.A_BOLD)

        for string in [workspace.initial, workspace.modified, workspace.target]:
            row += 1
            letters_in_string = sorted(
                (o for o in letter_objects if o.string == string),
                key=lambda o: o.leftIndex,
            )
            groups_in_string = sorted(
                (o for o in group_objects if o.string == string),
                key=lambda o: o.leftIndex,
            )
            if groups_in_string or letters_in_string:
                maxImportance = max(o.relativeImportance for o in groups_in_string + letters_in_string)
            bonds_in_string = sorted(
                (b for b in bond_structures if b.string == string),
                key=lambda b: b.leftObject.rightIndex,
            )
            assert bonds_in_string == sorted(string.bonds, key=lambda b: b.leftObject.rightIndex)
            startrow_for_group = {}
            endrow_for_group = {}

            max_column = 0
            for letter in letters_in_string:
                for g in groups_in_string:
                    if g.leftIndex == letter.leftIndex:
                        startrow_for_group[g] = row
                    if g.rightIndex == letter.rightIndex:
                        endrow_for_group[g] = row
                column = self.depict_workspace_object(w, row, 2, letter, maxImportance, description_structures)
                row += 1
                max_column = max(max_column, column)
                for b in bonds_in_string:
                    if b.leftObject.rightIndex == letter.rightIndex:
                        assert b.rightObject.leftIndex == letter.rightIndex + 1
                        column = self.depict_bond(w, row, 4, b)
                        row += 1
                        max_column = max(max_column, column)

            for group in groups_in_string:
                start = startrow_for_group[group]
                end = endrow_for_group[group]
                # Place this group's graphical depiction.
                depiction_width = 3 + self.length_of_workspace_object_depiction(group, description_structures)
                for firstcolumn in range(max_column, 1000):
                    lastcolumn = firstcolumn + depiction_width
                    okay = all(
                        w.is_vacant(r, c)
                        for c in range(firstcolumn, lastcolumn + 1)
                        for r in range(start, end + 1)
                    )
                    if okay:
                        self.depict_grouping_brace(w, start, end, firstcolumn + 1)
                        self.depict_workspace_object(w, (start + end) / 2, firstcolumn + 3, group, maxImportance, description_structures)
                        break

        row += 1
        column = 2

        for o in correspondences_between_initial_and_target:
            slipnet = workspace.ctx.slipnet
            w.addstr(row, column, '%s (%s)' % (str(o), str([m for m in o.conceptMappings if m.label != slipnet.identity])), curses.A_NORMAL)
            row += 1
            column = 2

        w.border()
        w.refresh()
