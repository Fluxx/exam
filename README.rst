####
Exam
####

.. image:: https://dl.dropbox.com/u/3663715/exam.jpeg

Exam is a Python toolkit for writing better tests.  It aims to remove a lot of the boiler plate testing code one often writes, while still following Python conventions and adhering to the unit testing interface.

Installation
------------

A simple ``pip install exam`` should do the trick.

Rationale
--------

Aside from the obvious "does the code work?", writings tests has many additional goals and bennefits:

1. If written semantically, reading tests can help demostrate how the code is supposed to work to other developers.
2. If quick running, tests provide feedback during development that your changes are working or not having an adverse side effects.
3. If they're easy to write correctly, developers will write more tests and they will be of a higher quality.

Unfortunately, the common pattern for writing Python unit tests tends to not offer any of these advantages.  Often times results in ineffecient and unnessarily obtuse testing code.  Additionally, common uses of the `mock` library can often result in repetitive boiler-plate code or ineffeciency during test runs.

`exam` aims to improve the state of Python test writing by providing a toolkit of useful functionality to make writing quick, correct and useful tests and painless as possible.

Usage
--------

Usage of Exam is best described with a hypothetical test case which exhibits all of exam's features:

.. code:: python

    from exam.decoratprs import fixture, before, after, around, patcher
    from exam.cases import Exam
    from exam.helpers import track

    import unittest
    import mock

    from coffee import Grounds, CoffeMaker
    from coffee import roast


    # The ``Exam`` mixin is needed for all of the ``@before``, ``@after``,
    # ``@around`` and ``@patcher`` decorators to work. It implements the
    # appropriate ``setUp()`` and ``tearDown()`` methods necessary to make the
    # decorators work.
    #
    # Note that the ``@fixture`` decorator works without needing to be defined
    # inside of an Exam class.  Still, it's a best practice to add the ``Exam``
    # mixin to your test cases.
    class TestCoffee(Exam, unittest.TestCase):

        # The ``@fixture`` decorator turns a method into a property (similar to
        # the @property decorator, but also memoizes the return value. This lets
        # you reference the property in your tests, i.e. ``self.grounds``, and
        # it will always reference the exact same instance every time.
        @fixture
        def grounds(self):
            return Grounds(origin='Sumatra')

        # If all your fixture method is doing is contructing a new instance of
        # type or calling a class method, exam provides a shorthand inline
        # ``fixture`` syntax for constructing fixture objects.  Simply set a
        # class variable equal to ``fixture(type_or_class_method)`` and exam
        # witll automatically call your type or class method.  Any ``*args`` or
        # ``**kwargs`` passed to ``fixture(type_or_class_method)`` will be
        # passed to the ``type_or_class_method`` when called.
        #
        # In the example below, ``self.coffee_maker`` is set to a newly
        # constructed ``CoffeeMaker`` instance with the passed args, i.e.
        # ``CoffeeMaker(brand='Coffee Mate')``
        coffee_maker = fixture(CoffeeMaker, brand='Coffee Mate')

        # The ``@before`` decorator adds the method to the list of methods which
        # are run as part of the class's ``setUp()`` routine.
        #
        # ``@before`` hooks works through subclasses - that is to say, if a
        # parent class has a ``@before`` hook in it, and you subclass it and
        # define a 2nd ``@before`` hook in it, both ``@before`` hooks will be
        # called.  Exam runs the child class's ``@before`` hook first, then runs
        # the parents'.
        @before
        def brew(self):
            self.coffee_maker.brew(self.grounds)

        # The compliment to ``@before``, ``@after`` adds the method to the list
        # of methods which are run as part of the class's ``tearDown()``
        # routine.
        #
        # Like ``@before``, ``@after`` runs child class ``@after`` hooks before
        # running their parents'.
        @after
        def clean_coffee_maker(self):
            self.coffee_maker.clean()

        # Methods decorated with the ``@around`` hook act like a context manager
        # that wraps a particular test method.  You must yield inside your
        # method decorated with ``@around``, which signifies the point in your
        # method where the test will run.  Once the test has run, your method
        # willcontinue and theremainder of it will be called.
        @around
        def put_on_stove(self):
            self.coffee_maker.put_on_stove()
            yield
            self.coffee_maker.take_off_stove()

        # The ``@patcher`` decorator is shorthand for the following boiler plate
        # code:
        #
        #     def setUp(self):
        #         self.stats_patcher = patch('mylib.stats', new=dummy_stats)
        #         self.stats = self.stats_patcher.start()
        #
        #     def tearDown(self):
        #         self.stats_patcher.stop()
        #
        # Often, manually controlling a patch's start/stop is done to provide a
        # test case property (here, ``self.stats``) for the mock object you are
        # patching with.  This is handy if you want the mock to have defaut
        # behavior for most tests, but change it slightly for certain ones --
        # i.e absorb all calls most of the time, but for certain tests have it
        # raise an exception.
        #
        # The above code can simply be written with the ``@patcher`` as:
        @patcher
        def stats(self):
            return dummy_stats

        # Exam takes care of starting and stopping the patcher appropriately, as
        # well as constructing the ``patch`` object with the return value from
        # the decorated method.
        #
        # If you're happy with the default constructed mock object for a patch
        # (``MagicMock``), then ``patcher`` can simply be used as an inline
        # as a function.  This method still starts and stops the patcher when
        # needed, and returns the constructed ``MagicMock`` object, which you
        # can set as a class attribute.  Exam will add the ``MagicMock`` object
        # to the test case as an instance attribute automatically.
        logger = patcher('coffee.logger')

        # The ``track`` helper is intended to assist in tracking call orders of
        # independent mock objects.  ``track`` is called with kwargs, where the
        # key is the mock name (a string) and the value is the mock object you
        # want to track.  ``track`` returns a newly constructed ``MagicMock``
        # object, with each mock object attached at a attribute named after the
        # mock name.
        #
        # For example, below ``track()`` creates a new mock with ``tracker.cool`
        # as the ``cool_mock`` and ``tracker.heat`` as the ``heat_mock``.
        @mock.patch('coffee.roast.heat')
        @mock.patch('coffee.roast.cool')
        def test_roasting_heats_then_cools_beans(self, cool_mock, heat_mock):
            tracker = track(heat=heat_mock, cool=cool_mock)
            roast.perform()
            tracker.assert_has_calls([mock.call.heat(), mock.call.cool()])

License
-------

Exam is MIT licensed.  Please see the ``LICENSE`` file for details.