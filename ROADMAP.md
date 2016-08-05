Good news everyone, there seems to be quite a few mostly standalone tasks right now.

Here we have them centralized, feel free to start working on some or add more or whatever. Post in
slack if you want to work on one of them, edit this file when done, also we should probably have
links to github issues here. So, what do we need:

* ioformats.py -- parser for input, composer for output, using namedtuples (high priority obviously)

* validator.py -- validate solution (also check if it's normalized, probably separately at first)

* visualization.py -- problem visualization, solution visualization, dead simple at first, not
  interactive (might be tkinter-based, might be ghetto solution2png)

* convex\_hull\_solver.py -- build a convex hull of the target shape, produce a solution that folds
  the square to get that shape. Not exactly obvious actually because multiple passes could be
required.

* сomputational\_geometry.py (misc stuff like poly area, poly intersection, etc.)

* normalize.py -- normalize a solution (if it's easy?)

* interface to their API. Using the API key Vlad posted in slack.

* interface for getting problems automatically. A database of problems (probably just a directory
  with text files).

* interface for submitting solutions automatically and in a centralized fashion, respecting the
  limits (1000 solutions/hr, 1 solution/sec). Probably would require an actual database.

* We need a problem generator before the end of Lightning (+24 hrs), because after that we have to
  submit/queue a problem per hour, or we miss that timeslot forever. As we understand, submitting a
problem at less than or equal to 2500 difficulty gives us the same amount of points as every team
that figures a perfect solution, so maybe we should randomly generate a bunch of 1250-complexity
stuff just in case.

-----------

Various ideas about the problem:

* We'll need two kinds of solvers: precise and imprecise, obviously. Because producing a precise
  solution for an arbitrary problem is very probably an NP-complete task, because why would the
  organizers choose this problem otherwise? So starting with a convex-hull imprecise solver would be
  a good idea.

* It looks like we shouldn't focus on the exact sequence of folds, which might not even exist in an
  even stronger sense than they imply with their "pulling paper through the fourth dimension". The
requirements are simple: we should give a mapping for vertices, all facets should be transformed
congruently as a result, the topology is preserved automatically because of vertices, the end.

