Copycat
=========

![GUI](https://i.imgur.com/AhhpzVQ.png)

An implementation of [Douglas Hofstadter](http://prelectur.stanford.edu/lecturers/hofstadter/) and [Melanie Mitchell](https://melaniemitchell.me/)'s Copycat algorithm.
The Copycat algorithm is explained [on Wikipedia](https://en.wikipedia.org/wiki/Copycat_%28software%29), in Melanie Mitchell's Book [Analogy-making as perception](https://www.amazon.com/Analogy-Making-Perception-Computer-Modeling-Connectionism/dp/026251544X/ref=sr_1_5?crid=1FC76DCS33513&dib=eyJ2IjoiMSJ9.TQVbRbFf696j7ZYj_sb4tIM3ZbFbuCIdtdYCy-Mq3EmJI6xbG5hhVXuyOPjeb7E4b8jhKiJlfr6NnD_O09rEEkNMwD_1zFxkLT9OkF81RSFL4kMCLOT7K-7KnPwBFbrc9tZuhLKFOWbxMGNL75koMcetQl2Lf6V7xsNYLYLCHBlXMCrusJ88Kv3Y8jiPKwrEr1hUwhWB8vtwEG9vSYXU7Gw-b4fZRNNbUtBBWNwiK3k.IJZZ8kA_QirWQK1ax5i42zD2nV7XvKoPYRgN94en4Dc&dib_tag=se&keywords=melanie+mitchell&qid=1745436638&sprefix=melanie+mitchell%2Caps%2C206&sr=8-5#), and in [this paper](https://github.com/Alex-Linhares/FARGonautica/blob/master/Literature/Foundations-Chalmers.French.and.Hofstadter-1992-Journal%20of%20Experimental%20and%20Theoretical%20Artificial%20Intelligence.pdf). The wikipedia page has additional links for deeper reading.  See also [FARGonautica](https://github.com/Alex-Linhares/Fargonautica), where a collection of Fluid Concepts projects are available.

This implementation is a copycat of Scott Boland's [Java implementation](https://archive.org/details/JavaCopycat).
The original Java-to-Python translation work was done by J Alan Brogan (@jalanb on GitHub).
The Java version has a GUI similar to the original Lisp; this Python version has no GUI code built in but can be incorporated into a larger GUI program.

J. Alan Brogan writes:
> In cases where I could not grok the Java implementation easily, I took ideas from the
> [LISP implementation](http://web.cecs.pdx.edu/~mm/how-to-get-copycat.html), or directly
> from [Melanie Mitchell](https://en.wikipedia.org/wiki/Melanie_Mitchell)'s book
> "[Analogy-Making as Perception](http://www.amazon.com/Analogy-Making-Perception-Computer-Melanie-Mitchell/dp/0262132893/ref=tmm_hrd_title_0?ie=UTF8&qid=1351269085&sr=1-3)".

Running the command-line program
--------------------------------

To clone the repo locally, run these commands:

```
$ git clone https://github.com/fargonauts/copycat.git
$ cd copycat/copycat
$ python main.py abc abd ppqqrr --iterations 10
```

The script takes three or four arguments.
The first two are a pair of strings with some change, for example "abc" and "abd".
The third is a string which the script should try to change analogously.
The fourth (which defaults to "1") is a number of iterations.

This might produce output such as

```
ppqqss: 6 (avg time 869.0, avg temp 23.4)
ppqqrs: 4 (avg time 439.0, avg temp 37.3)
```

The first number indicates how many times Copycat chose that string as its answer; higher means "more obvious".
The last number indicates the average final temperature of the workspace; lower means "more elegant".

Code structure
---------------------

This Copycat system consists of 4,981 lines of Python code across 40 files. Here's a breakdown.

Core Components:
- codeletMethods.py: 1,124 lines (largest file)
- curses_reporter.py: 436 lines
- coderack.py: 310 lines
- slipnet.py: 248 lines
- Workspace Components:
- group.py: 237 lines
- bond.py: 211 lines
- correspondence.py: 204 lines
- workspace.py: 195 lines
- workspaceObject.py: 194 lines

Control Components:
- temperature.py: 175 lines
- conceptMapping.py: 153 lines
- rule.py: 149 lines
- copycat.py: 144 lines

GUI Components:
- gui/gui.py: 96 lines
- gui/workspacecanvas.py: 70 lines
- gui/status.py: 66 lines
- gui/control.py: 59 lines


The system is well-organized with clear separation of concerns:
- Core logic (codelets, coderack, slipnet)
- Workspace management (groups, bonds, correspondences)
- Control systems (temperature, rules)
- User interface (GUI components)

The largest file, codeletMethods.py, contains all the codelet behavior implementations, which makes sense as it's the heart of the system's analogical reasoning capabilities.

{code.py}README.md Files
---------------------

We've got an LLM to document every code file, so people can look at a particular readme before delving into the work.


Installing the module
---------------------

To install the Python module and get started with it, run these commands:

```
$ pip install -e git+git://github.com/fargonauts/copycat.git#egg=copycat
$ python
>>> from copycat import Copycat
>>> Copycat().run('abc', 'abd', 'ppqqrr', 10)
{'ppqqrs': {'count': 4, 'avgtime': 439, 'avgtemp': 37.3}, 'ppqqss': {'count': 6, 'avgtime': 869, 'avgtemp': 23.4}}
```

The result of `run` is a dict containing the same information as was printed by `main.py` above.
