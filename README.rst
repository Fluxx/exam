.. image:: https://api.travis-ci.org/Fluxx/exam.png?branch=master
   :target: http://travis-ci.org/fluxx/exam

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

Exam features a collection of useful modules:

``exam.decorators``
~~~~~~~~~~~~~~~~~~~

Exam has some useful decorators to make your tests easier to write and understand.  To utilize the ``@before``, ``@after``, ``@around`` and ``@patcher`` decorators, you must mixin the ``exam.cases.Exam`` class into your test case.  It implements the appropriate ``setUp()`` and ``tearDown()`` methods necessary to make the decorators work.

Note that the ``@fixture`` decorator works without needing to be defined inside of an Exam class.  Still, it's a best practice to add the ``Exam`` mixin to your test cases.

All of the decorators in ``exam.decorators``, as well as the ``Exam`` test case are available for import from the main ``exam`` package as well. I.e.:

.. code:: python

    from exam import Exam
    from exam import fixture, before, after, around, patcher

``exam.decorators.fixture``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``@fixture`` decorator turns a method into a property (similar to the ``@property`` decorator, but also memoizes the return value. This lets you reference the property in your tests, i.e. ``self.grounds``, and it will always reference the exact same instance every time.

.. code:: python

    from exam.decorators import fixture
    from exam.cases import Exam

    class MyTest(Exam, TestCase):

        @fixture
        def user(self):
            return User(name='jeff')

        def test_user_name_is_jeff(self):
            assert self.user.name == 'jeff'

As you can see, ``self.user`` was used to reference the ``user`` property defined above.

If all your fixture method is doing is contructing a new instance of type or calling a class method, exam provides a shorthand inline ``fixture`` syntax for constructing fixture objects.  Simply set a class variable equal to ``fixture(type_or_class_method)`` and exam witll automatically call your type or class method.

.. code:: python

    from exam.decorators import fixture
    from exam.cases import Exam

    class MyTest(Exam, TestCase):

        user = fixture(User, name='jeff')

        def test_user_name_is_jeff(self):
            assert self.user.name == 'jeff'

Any ``*args`` or ``**kwargs`` passed to ``fixture(type_or_class_method)`` will be passed to the ``type_or_class_method`` when called.


``exam.decorators.before``
^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``@before`` decorator adds the method to the list of methods which are run as part of the class's ``setUp()`` routine.

.. code:: python

    from exam.decorators import before
    from exam.cases import Exam

    class MyTest(Exam, TestCase):

        @before
        def reset_database(self):
            mydb.reset()


``@before`` also hooks works through subclasses - that is to say, if a parent class has a ``@before`` hook in it, and you subclass it and define a 2nd ``@before`` hook in it, both ``@before`` hooks will be called.  Exam runs the parent's ``@before`` hook first, then runs the childs'.  Also, if your override a `@before` hook in your child class, the overriden method is run when the rest of the child classes `@before` hooks are run.

For example, with hooks defined as such:

.. code:: python

    from exam.decorators import before
    from exam.cases import Exam

    class MyTest(Exam, TestCase):

        @before
        def reset_database(self):
            print 'parent reset_db'

        @before
        def parent_hook(self):
            print 'parent hook'


    class RedisTest(MyTest):

        @before
        def reset_database(self):
            print 'child reset_db'

        @before
        def child_hook(self):
            print 'child hook'

When Exam runs these hooks, the output would be:

.. code:: python

    "prent hook"
    "child reset_db"
    "child hook"

As you can see even though the parent class defines a ``reset_database``, because the child class overwrote it, the child's version is run intead, and also at the same time as the rest of the child's ``@before`` hooks.

``exam.decorators.after``
^^^^^^^^^^^^^^^^^^^^^^^^^

The compliment to ``@before``, ``@after`` adds the method to the list of methods which are run as part of the class's ``tearDown()`` routine. Like ``@before``, ``@after`` runs parent class ``@after`` hooks before running ones defined in child classes.

.. code:: python

    from exam.decorators import after
    from exam.cases import Exam

    class MyTest(Exam, TestCase):

        @after
        def remove_temp_files(self):
            myapp.remove_temp_files()


``exam.decorators.around``
^^^^^^^^^^^^^^^^^^^^^^^^^

Methods decorated with ``@around`` act as a conxtext manager around each test method.  In your around method, you're responsible for calling ``yield`` where you want the test case to run:

.. code:: python

    from exam.decorators import around
    from exam.cases import Exam

    class MyTest(Exam, TestCase):

        @around
        def run_in_transaction(self):
            db.begin_transaction()
            yield  # Run the test
            db.rollback_transaction()

``@around`` also follows the same parent/child ordering rules as ``@before`` and ``@after``, so parent ``@arounds`` will run (up until the ``yield`` statmement), then child ``@around``s will run.  After the test method has finished, however, the rest of the child's ``@around`` will run, and then the parents's.  This is done to preserve the normal behavior of nesting with context managers.


``exam.decorators.patcher``
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``@patcher`` decorator is shorthand for the following boiler plate code:

.. code:: python

    from mock import patch

     def setUp(self):
         self.stats_patcher = patch('mylib.stats', new=dummy_stats)
         self.stats = self.stats_patcher.start()

     def tearDown(self):
         self.stats_patcher.stop()

Often, manually controlling a patch's start/stop is done to provide a test case property (here, ``self.stats``) for the mock object you are patching with.  This is handy if you want the mock to have defaut behavior for most tests, but change it slightly for certain ones -- i.e absorb all calls most of the time, but for certain tests have it raise an exception.

Using the ``@patcher`` decorator, the above code can simply be written as:

.. code:: python

    from exam.decorators import patcher
    from exam.cases import Exam

    class MyTest(Exam, TestCase):

       @patcher('mylib.stats')
       def stats(self):
           return dummy_stats

Exam takes care of starting and stopping the patcher appropriately, as well as constructing the ``patch`` object with the return value from the decorated method.

If you're happy with the default constructed mock object for a patch (``MagicMock``), then ``patcher`` can simply be used as an inline as a function inside the class body.  This method still starts and stops the patcher when needed, and returns the constructed ``MagicMock`` object, which you can set as a class attribute.  Exam will add the ``MagicMock`` object to the test case as an instance attribute automatically.

.. code:: python

    from exam.decorators import patcher
    from exam.cases import Exam

    class MyTest(Exam, TestCase):

        logger = patcher('coffee.logger')

``exam.helpers``
~~~~~~~~~~~~~~~~

The ``helpers`` module features a collection of helper methods for common testing patterns:

``exam.helpers.track``
^^^^^^^^^^^^^^^^^^^^^^

The ``track`` helper is intended to assist in tracking call orders of independent mock objects.  ``track`` is called with kwargs, where the key is the mock name (a string) and the value is the mock object you want to track.  ``track`` returns a newly constructed ``MagicMock`` object, with each mock object attached at a attribute named after the mock name.

For example, below ``track()`` creates a new mock with ``tracker.cool` as the ``cool_mock`` and ``tracker.heat`` as the ``heat_mock``.

.. code:: python

    from exam.helpers import track

    @mock.patch('coffee.roast.heat')
    @mock.patch('coffee.roast.cool')
    def test_roasting_heats_then_cools_beans(self, cool_mock, heat_mock):
        tracker = track(heat=heat_mock, cool=cool_mock)
        roast.perform()
        tracker.assert_has_calls([mock.call.heat(), mock.call.cool()])

``exam.helpers.rm_f``
^^^^^^^^^^^^^^^^^^^^^

This is a simple helper that just removes all folders and files at a path:

.. code:: python

    from exam.helpers import rm_f

    rm_f('/folder/i/do/not/care/about')

``exam.helpers.mock_import``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Removes most of the boiler plate code needed to mock imports, which usually consists of making a ``patch.dict`` from ``sys.modules``.  Instead, the ``patch_import`` helper can simply be used as a decorator or context manager for when certain modules are imported.

.. code:: python

    from exam.helpers import mock_import

    with mock_import('os.path') as my_os_path:
        import os.path as imported_os_path
        assert my_os_path is imported_os_path

``mock_import`` can also be used as a decorator, which passed the mock value to
the testing method (like a normal ``@patch``) decorator:

.. code:: python

    from exam.helpers import mock_import

    @mock_import('os.path')
    def test_method(self):
        import os.path as imported_os_path
        assert my_os_path is imported_os_path

``exam.mock``
~~~~~~~~~~~~~

Exam has a subclass of the normal ``mock.Mock`` object that adds a few more useful methods to your mock objects.  Use it in place of a normal ``Mock`` object:

.. code:: python

    from exam.mock import Mock

    mock_user = Mock(spec=User)

The subclass has the following extra methods:

* ``assert_called()`` - Asserts the mock was called at least once.
* ``assert_not_called()`` - Asserts the mock has never been called.
* ``assert_not_called_with(*args, **kwargs)`` - Asserts the mock was not most recently called with the specified ``*args`` and ``**kwargs``.
* ``assert_not_called_once_with(*args, **kwargs)`` - Asserts the mock has only every been called once with the specified ``*args`` and ``**kwargs``.
* ``assert_not_any_call(*args, **kwargs)`` - Asserts the mock has never been called with the specified ``*args`` and ``**kwargs``.

``exam.fixtures``
~~~~~~~~~~~~~~~~~

Helpful fixtures that you may want to use in your tests:

* ``exam.fixtures.two_px_square_image`` - Image data as a string of a 2px square image.
* ``exam.fixtures.one_px_spacer`` - Image data as a string of a 1px square spacer image.

``exam.objects``
~~~~~~~~~~~~~~~~

Useful objectgs for use in testing:

``exam.objects.noop`` - callable object that always returns ``None``. no matter how it was called.

``exam.asserts``
~~~~~~~~~~~~~~~~

The `asserts` module contains an `AssertsMixin` class, which is mixed into the main `Exam` test case mixin.  It contains additional asserts beoynd the ones in Python's `unittest`.

``assertChanges``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Used when you want to assert that a section of code changes a value.  For example, imagine if you had a function that changed a soldier's rank.

To properly test this, you should save that soldier's rank to a temporary variable, then run the function to change the rank, and then finally assert that the rank is the new expected value, as well as **not** the old value:

.. code:: python

    test_changes_rank(self):
        old_rank = self.soldier.rank
        promote(self.soldier, 'general')
        self.assertEaual(self.soldier.rank, 'general')
        self.assertNotEqual(self.soldier.rank, old_rank)

Checking the old rank is not the same is the new rank is important.  If, for some reason there is a bug or something to where `self.soldier` is created with the rank of `general`, but `promote` is not working, this test would still pass!

To solve this, you can use Exam's `assertChanges`:

.. code:: python

    test_changes_rank(self):
        self.assertChanges(getattr, self.soldier, 'rank', after='general'):
            promote(self.soldier, 'general')

This assert is doing a few things.

# It asserts that the rank once the cotext is run is the expected `general`.
# It asserts that the context **changes** the value of `self.soldier.rank`.
# It doesn't actually care what the old value of `self.soldier.rank` was, as long as it changed when the context was run.

The definition of `assertChanges` is:

.. code:: python
    def assertChanges(thing, *args, **kwargs)

# You pass it a `thing`, which wich be a callable.
# `assertChanges` then calls your `thing` with any `*args` and `**kwargs` additionally passed in and captures the value as the "before" value.
# The context is run, and then the callable is captured again as the "after" value.
# If before and after are not different, an `AssertionError` is raised.
# Additionally, if the special kwarg `before` or `after` are passed, those values are extracted and saved.  In this case an `AssertionError` can also be raised if the "before" and/or "after" values provided do not match their extracted values.

License
-------

Exam is MIT licensed.  Please see the ``LICENSE`` file for details.
