import unittest

def square(idx, x):
    return idx, x * x

def get_generator(iterable):
    yield from iterable

class ParallellTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create some test data. Note that the regular map reads the inputs as a list of single tuples (one argument),
        # whereas parallel.map sees it as a list of argument lists. Therefore we give the regular map a lambda function
        # which mimics the parallel.map behavior.
        self.test_data = [(idx, x) for idx, x in enumerate([1, 2, 3, 5, 6, 9, 37, 42, 1337, 0, 3, 5, 0])]
        self.test_desired_output = list(map(lambda _args: square(*_args), self.test_data))

    def test_worker_pool_map(self):
        """
        Tests the map related function of the worker pool class
        """
        from workerpool import WorkerPool
        import types

        # Test results for different number of jobs to run in parallel and the maximum number of active tasks in the
        # queue
        for n_jobs, n_tasks_max_active in [(1, None), (1, 1), (1, 3), (2, None), (2, 1), (2, 3),
                                           (3, None), (3, 1), (3, 3), (None, None), (None, 1), (None, 3)]:
            with WorkerPool(square, n_jobs=n_jobs) as pool:
                # Test if parallel map results in the same as ordinary map function. Should work both for generators
                # and iterators. Also check if an empty list works as desired.
                results_list = pool.map(self.test_data, n_tasks_max_active)
                self.assertTrue(isinstance(results_list, list))
                self.assertEqual(self.test_desired_output, results_list)

                results_list = pool.map(get_generator(self.test_data), n_tasks_max_active)
                self.assertTrue(isinstance(results_list, list))
                self.assertEqual(self.test_desired_output, results_list)

                results_list = pool.map([], n_tasks_max_active)
                self.assertTrue(isinstance(results_list, list))
                self.assertEqual([], results_list)

                # Test if parallel map_unordered contains all results. Should work both for generators and iterators.
                # Also check if an empty list works as desired.
                results_list = pool.map_unordered(self.test_data, n_tasks_max_active)
                self.assertTrue(isinstance(results_list, list))
                self.assertEqual(self.test_desired_output, sorted(results_list, key=lambda tup: tup[0]))

                results_list = pool.map_unordered(get_generator(self.test_data), n_tasks_max_active)
                self.assertTrue(isinstance(results_list, list))
                self.assertEqual(self.test_desired_output, sorted(results_list, key=lambda tup: tup[0]))

                results_list = pool.map_unordered([], n_tasks_max_active)
                self.assertTrue(isinstance(results_list, list))
                self.assertEqual([], sorted(results_list, key=lambda tup: tup[0]))

                # Test if parallel imap contains all results and if it returns an iterator. Should work for both
                # generators and iterators. Also check if an empty list works as desired.
                result_generator = pool.imap(self.test_data, n_tasks_max_active)
                self.assertTrue(isinstance(result_generator, types.GeneratorType))
                self.assertEqual(self.test_desired_output, list(result_generator))

                result_generator = pool.imap(get_generator(self.test_data), n_tasks_max_active)
                self.assertTrue(isinstance(result_generator, types.GeneratorType))
                self.assertEqual(self.test_desired_output, list(result_generator))

                result_generator = pool.imap([], n_tasks_max_active)
                self.assertTrue(isinstance(result_generator, types.GeneratorType))
                self.assertEqual([], list(result_generator))

                # Test if parallel imap_unordered contains all results and if it returns an iterator. Should work for
                # both generators and iterators. Also check if an empty list works as desired.
                result_generator = pool.imap_unordered(self.test_data, n_tasks_max_active)
                self.assertTrue(isinstance(result_generator, types.GeneratorType))
                self.assertEqual(self.test_desired_output, sorted(result_generator, key=lambda tup: tup[0]))

                result_generator = pool.imap_unordered(get_generator(self.test_data), n_tasks_max_active)
                self.assertTrue(isinstance(result_generator, types.GeneratorType))
                self.assertEqual(self.test_desired_output, sorted(result_generator, key=lambda tup: tup[0]))

                result_generator = pool.imap_unordered([], n_tasks_max_active)
                self.assertTrue(isinstance(result_generator, types.GeneratorType))
                self.assertEqual([], sorted(result_generator, key=lambda tup: tup[0]))

        # Zero (or a negative number of) active tasks should result in a value error
        for n_tasks_max_active in [-3, -1, 0]:
            with self.assertRaises(ValueError):
                with WorkerPool(square, n_jobs=None) as pool:
                    pool.map(self.test_data, n_tasks_max_active)

            with self.assertRaises(ValueError):
                with WorkerPool(square, n_jobs=None) as pool:
                    pool.map_unordered(self.test_data, n_tasks_max_active)

            with self.assertRaises(ValueError):
                with WorkerPool(square, n_jobs=None) as pool:
                    for _ in pool.imap(self.test_data, n_tasks_max_active):
                        pass

            with self.assertRaises(ValueError):
                with WorkerPool(square, n_jobs=None) as pool:
                    for _ in pool.imap_unordered(self.test_data, n_tasks_max_active):
                        pass
