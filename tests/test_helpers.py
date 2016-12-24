import itertools

from tests import TestCase
from mock import patch, Mock, sentinel

from exam.helpers import intercept, rm_f, track, mock_import, call, effect
from exam.decorators import fixture


@patch('exam.helpers.shutil')
class TestRmrf(TestCase):

    path = '/path/to/folder'

    def test_calls_shutil_rmtreee(self, shutil):
        rm_f(self.path)
        shutil.rmtree.assert_called_once_with(self.path, ignore_errors=True)

    @patch('exam.helpers.os')
    def test_on_os_errors_calls_os_remove(self, os, shutil):
        shutil.rmtree.side_effect = OSError
        rm_f(self.path)
        os.remove.assert_called_once_with(self.path)


class TestTrack(TestCase):

    @fixture
    def foo_mock(self):
        return Mock()

    @fixture
    def bar_mock(self):
        return Mock()

    def test_makes_new_mock_and_attaches_each_kwarg_to_it(self):
        tracker = track(foo=self.foo_mock, bar=self.bar_mock)
        self.assertEqual(tracker.foo, self.foo_mock)
        self.assertEqual(tracker.bar, self.bar_mock)


class TestMockImport(TestCase):

    def test_is_a_context_manager_that_yields_patched_import(self):
        with mock_import('foo') as mock_foo:
            import foo
            self.assertEqual(foo, mock_foo)

    def test_mocks_import_for_packages(self):
        with mock_import('foo.bar.baz') as mock_baz:
            import foo.bar.baz
            self.assertEqual(foo.bar.baz, mock_baz)

    @mock_import('foo')
    def test_can_be_used_as_a_decorator_too(self, mock_foo):
        import foo
        self.assertEqual(foo, mock_foo)

    @mock_import('foo')
    @mock_import('bar')
    def test_stacked_adds_args_bottom_up(self, mock_bar, mock_foo):
        import foo
        import bar
        self.assertEqual(mock_bar, bar)
        self.assertEqual(mock_foo, foo)


class TestIntercept(TestCase):

    class Example(object):
        def method(self, positional, keyword):
            return sentinel.METHOD_RESULT

    def test_intercept(self):
        ex = self.Example()

        def counter(positional, keyword):
            assert positional is sentinel.POSITIONAL_ARGUMENT
            assert keyword is sentinel.KEYWORD_ARGUMENT
            result = yield
            assert result is sentinel.METHOD_RESULT
            counter.calls += 1

        counter.calls = 0

        intercept(ex, 'method', counter)
        self.assertEqual(counter.calls, 0)
        assert ex.method(
            sentinel.POSITIONAL_ARGUMENT,
            keyword=sentinel.KEYWORD_ARGUMENT) is sentinel.METHOD_RESULT
        self.assertEqual(counter.calls, 1)

        ex.method.unwrap()
        assert ex.method(
            sentinel.POSITIONAL_ARGUMENT,
            keyword=sentinel.KEYWORD_ARGUMENT) is sentinel.METHOD_RESULT
        self.assertEqual(counter.calls, 1)


class TestEffect(TestCase):

    def test_creates_callable_mapped_to_config_dict(self):
        config = [
            (call(1), 2),
            (call('a'), 3),
            (call(1, b=2), 4),
            (call(c=3), 5)
        ]
        side_effect = effect(*config)

        self.assertEqual(side_effect(1), 2)
        self.assertEqual(side_effect('a'), 3)
        self.assertEqual(side_effect(1, b=2), 4)
        self.assertEqual(side_effect(c=3), 5)

    def test_raises_type_error_when_called_with_unknown_args(self):
        side_effect = effect((call(1), 5))
        self.assertRaises(TypeError, side_effect, 'junk')

    def test_can_be_used_with_mutable_data_structs(self):
        side_effect = effect((call([1, 2, 3]), 'list'))
        self.assertEqual(side_effect([1, 2, 3]), 'list')
        
    def test_can_be_used_to_return_class(self):
        class Some(object):
            pass
        side_effect = effect((call(1), Some))
        self.assertEqual(side_effect(1), Some)
        self.assertEqual(side_effect(1), Some)#always returns Some
    
    def test_can_be_used_to_return_instance(self):
        class Some(object):
            pass
        side_effect = effect((call(1), Some()))
        self.assertEqual(side_effect(1).__class__, Some().__class__)
        self.assertEqual(side_effect(1).__class__, Some().__class__)#always returns a Some instance
    
    def test_can_be_used_to_return_mock_instance(self):
        side_effect = effect((call(1), Mock()))
        self.assertEqual(side_effect(1).__class__.__name__, Mock().__class__.__name__)
        self.assertEqual(side_effect(1).__class__.__name__, Mock().__class__.__name__)#always returns a Mock instance
    
    def test_can_be_used_with_various_iterators(self):
        side_effect = effect((call(1), itertools.repeat(10, 3)))
        for i in range(3):
            self.assertEqual(side_effect(1), 10)
        with self.assertRaises(TypeError):
            side_effect(1)
        #trying another iterator    
        side_effect = effect((call(1), itertools.chain([1,1,1], [2,2,2])))
        for i in range(3):
            self.assertEqual(side_effect(1), 1)
        for i in range(3):
            self.assertEqual(side_effect(1), 2)
        with self.assertRaises(TypeError):
            side_effect(1)
    
    def test_sequential_config_with_generator(self):
        def ten_times():
            for i in range(9):
                yield i
        config = (
            (call('can be called ten times'), ten_times()),#note generator must be called
        )
        side_effect = effect(*config)
        for i in range(9):
            self.assertEqual(side_effect('can be called ten times'), i)
        with self.assertRaises(TypeError):
            side_effect('can be called ten times')
        
    def test_sequential_config_with_multiple_elements_each_called_only_once(self):
        config = (
            (call('with 1, again and then TypeError'), ['with 1', 'with 1 again']), 
        )
        side_effect = effect(*config)
        self.assertEqual(side_effect('with 1, again and then TypeError'), 'with 1')
        self.assertEqual(side_effect('with 1, again and then TypeError'), 'with 1 again')
        with self.assertRaises(TypeError):
            side_effect('with 1, again and then TypeError')
    
    def test_sequential_config_with_one_element_called_only_once(self):
        config = (
            (call('with 2, followed by TypeError'), ['with 2']), 
        )
        side_effect = effect(*config)
        self.assertEqual(side_effect('with 2, followed by TypeError'), 'with 2')
        with self.assertRaises(TypeError):
            side_effect('with 2, followed by TypeError')
    
    def test_empty_sequential_config_raises_exception_on_first_call(self):
        config = (
            (call('Empty iterable, raises TypeError on first call'), []), 
        )
        side_effect = effect(*config)
        with self.assertRaises(TypeError):
            side_effect('Empty iterable, raises TypeError on first call')
            
    def test_using_cycle_config_can_be_called_infinitely(self):
        config = (
            (call('Can be called forever'), itertools.cycle(['with 1', 'with 1 again'])), 
        )
        side_effect = effect(*config)
        self.assertEqual(side_effect('Can be called forever'), 'with 1')
        self.assertEqual(side_effect('Can be called forever'), 'with 1 again')
        self.assertEqual(side_effect('Can be called forever'), 'with 1')
        self.assertEqual(side_effect('Can be called forever'), 'with 1 again')
    
    def test_dicts_should_be_returned_as_is(self):
        config = (
            (call('A dict should always be returned as is'), {'this': 'is a dict'}), 
        )
        side_effect = effect(*config)
        self.assertEqual(side_effect('A dict should always be returned as is'), {'this': 'is a dict'})
        self.assertEqual(side_effect('A dict should always be returned as is'), {'this': 'is a dict'})
        
    def test_you_can_put_data_structures_into_sequential_configs(self):
        config = (
            (call('returns a dict and then TypeError'), [{'this': 'is a dict in a list'}]), 
        )
        side_effect = effect(*config)
        self.assertEqual(side_effect('returns a dict and then TypeError'), {'this': 'is a dict in a list'})
        with self.assertRaises(TypeError):
            side_effect('returns a dict and then TypeError')
    
    def test_you_can_put_data_structures_into_infinite_sequential_configs(self):
        config = (
            (call('Always a dict'), itertools.cycle([{'this': 'is a dict in a list'}])), 
        )
        side_effect = effect(*config)
        self.assertEqual(side_effect('Always a dict'), {'this': 'is a dict in a list'})
        self.assertEqual(side_effect('Always a dict'), {'this': 'is a dict in a list'})
    
    def test_sequential_callable_with_a_bunch_of_configs(self):
        config = (
            (call(1), itertools.cycle(['with 1', 'with 1 again'])), 
            (call(2), 'with 2'), 
            (call(3), ['with 3',]),
            (call(4), []),
            (call(5), [{'this': 'is a dict in a list'}]),
            (call(6), {'this': 'is a dict'})
        )
        side_effect = effect(*config)
        self.assertEqual(side_effect(1), 'with 1')
        self.assertEqual(side_effect(2), 'with 2')
        self.assertEqual(side_effect(3), 'with 3')
        self.assertEqual(side_effect(1), 'with 1 again')
        self.assertEqual(side_effect(1), 'with 1')
        self.assertEqual(side_effect(2), 'with 2')#second call
        with self.assertRaises(TypeError):
            side_effect(3)
        with self.assertRaises(TypeError):
            side_effect(4)
        self.assertEqual(side_effect(5), {'this': 'is a dict in a list'})
        with self.assertRaises(TypeError):
            side_effect(5)
        self.assertEqual(side_effect(6), {'this': 'is a dict'})
        
