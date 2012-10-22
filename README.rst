####
Exam
####

.. image:: https://dl.dropbox.com/u/3663715/exam.jpeg

Exam is a Python toolkit for writing better tests.  It aims to remove a lot of
the boiler plate testing code one often writes, while still following Python
conventions and adhering to the unit testing interface.

Installation
------------

A simple ``pip install exam`` should do the trick.

Usage
-----

Exam is still a growing toolkit, but already contains a collection of usefull
tools.  This is a sample class which describes all of them::


    from exam import before, after, around
    from exam import fixture
    from exam.cases import Exam

    import unittest

    from coffee import Grounds, CoffeMaker


    # The Exam mixin is needed for all of the @before, @after and @around hooks to
    # work.  It implements the appropriate setUp() and tearDown() methods.
    #
    # Note that the @fixture decorator works without needing to be defined inside
    # of an Exam class.
    class TestCoffee(Exam, unittest.TestCase):

        # The @fixture decorator turns a method into a property (similar to the
        # @property decorator, but also memoizes the return value. This lets you
        # reference the property in your tests, i.e. self.grounds, and it will
        # always reference the exact same instance every time.
        @fixture
        def grounds(self):
            return Grounds(origin='Sumatra')

        @fixture
        def coffee_maker(self):
            return CoffeMaker()

        # The @before decorator adds the method to the list of methods which are
        # run as part of the class's setUp() method.
        #
        # @before hooks works through subclasses - that is to say, if a parent
        # class has a @before hook in it, and you subclass it and define a 2nd
        # @before hook in it, both @before hooks will be called.  Exam runs the
        # child class's @before hook first, then runs the parents'.
        @before
        def brew(self):
            self.coffee_maker.brew(self.grounds)

        # The compliment to @before, @after adds the method to the list of methods
        # which are run as part of the class's tearDown() method.
        #
        # Like @before, @after runs child class @after hooks before running their
        # parents'.
        @after
        def clean_coffee_maker(self):
            self.coffee_maker.clean()

        # Methods decorated with the @around hook acts like a context manager that
        # wraps a particular test method.  You must yield inside your method
        # decorated with @around, which signifies the point in your method where
        # the test will run.  Once the test has run, your method will continue and
        # theremainder of it will be called.
        @around
        def put_on_stove(self):
            self.coffee_maker.put_on_stove()
            yield
            self.coffee_maker.take_off_stove()

License
-------

Exam is MIT licensed.  Please see the ``LICENSE`` file for details.