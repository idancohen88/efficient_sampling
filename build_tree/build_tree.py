import random
from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch

import numpy as np
from BTrees.OOBTree import OOBTreePy

from btrees.btree_ext import OOBTreeExt

CHUNKS_SIZE = 10000
KEY_LENGTH = 8
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
INT_SUFFIX_LEN = 10
MAX_ZIPF_INT = 10_000_000_000

DEFAULT_SAMPLING_METHODS = ["sample_olken_early_abort",
                "sample_distribution_oriented_height_four",
                "sample_distribution_oriented_height_three",
                "sample_naive_random_walk", ]


def create_zipf_data_and_run_samples(num_of_values, domain_size, skew_factor=0, sampling_sizes=None,
                                     sampling_methods=None):
    print(f'running with num_of_values={num_of_values} domain_size={domain_size} skew_factor={skew_factor}')
    sampling_methods = sampling_methods or DEFAULT_SAMPLING_METHODS
    index = generate_zipf_dist_in_random_order(num_of_values, domain_size, skew_factor)

    if index._btree_height == 4 and "sample_distribution_oriented_height_three" in sampling_methods:
        sampling_methods.remove("sample_distribution_oriented_height_three")
    if index._btree_height == 3 and "sample_distribution_oriented_height_four" in sampling_methods:
        sampling_methods.remove("sample_distribution_oriented_height_four")

    if index._btree_height > 2:
        assert not ("sample_distribution_oriented_height_three" in sampling_methods and
                    "sample_distribution_oriented_height_four" in sampling_methods)
    print('sampling methods: ', sampling_methods)
    sampling_sizes = sampling_sizes or [num_of_values * 0.005, num_of_values * 0.01, num_of_values * 0.05,
                                        num_of_values * 0.1]
    sampling_sizes = list(map(int, sampling_sizes))
    index.run_sample_methods(k=sampling_sizes, iterations=3, sampling_methods=sampling_methods)


def create_clustered_data_and_run_samples(num_of_values, prefix_to_percent, sampling_sizes=None, sampling_methods=None):
    print(f'running with num_of_values={num_of_values}')
    index = generate_btree_index_x_values_with_dist(num_of_values, prefix_to_percent)

    sampling_methods = sampling_methods or DEFAULT_SAMPLING_METHODS

    if index._btree_height == 4 and "sample_distribution_oriented_height_three" in sampling_methods:
        sampling_methods.remove("sample_distribution_oriented_height_three")
    if index._btree_height == 3 and "sample_distribution_oriented_height_four" in sampling_methods:
        sampling_methods.remove("sample_distribution_oriented_height_four")

    if index._btree_height > 2:
        assert not ("sample_distribution_oriented_height_three" in sampling_methods and
                    "sample_distribution_oriented_height_four" in sampling_methods)

    print('generated btree with id %s' % index.btree_id)
    sampling_sizes = sampling_sizes or [num_of_values * 0.005, num_of_values * 0.01, num_of_values * 0.05,
                                        num_of_values * 0.1]
    sampling_sizes = list(map(int, sampling_sizes))
    index.run_sample_methods(k=sampling_sizes, iterations=3, sampling_methods=sampling_methods)


def generate_btree_index_x_values_with_dist(
    num_of_values, disired_prefix_to_percent_dist, my_index=None
):
    print("start time %s" % datetime.now())
    my_index = my_index if my_index is not None else OOBTreeExt()

    for prefix, amount_percent in disired_prefix_to_percent_dist.items():
        amount = int(num_of_values * amount_percent)
        my_index = insert_to_index_random(my_index, amount, prefix)

    print("finish at %s" % datetime.now())
    my_index.set_data_generation_method('prefix_clusters')
    return my_index


def generate_btree_index_x_values_with_dist_and_custom_leaf_size(
    num_of_values, disired_prefix_to_percent_dist, my_index=None, leaf_size=None
):
    assert leaf_size
    with overriding_btree_max_leaf_size(leaf_size):
        my_index = generate_btree_index_x_values_with_dist(
            num_of_values, disired_prefix_to_percent_dist, my_index
        )

    _validate_leaf_size(my_index, leaf_size)
    return my_index


def _validate_leaf_size(my_index, max_leaf_size):
    bucket = my_index._firstbucket
    assert bucket.size <= max_leaf_size
    while bucket._next:
        assert bucket.size <= max_leaf_size
        bucket = bucket._next


def insert_to_index_random(my_index, amount, prefix=""):
    amount_in_iteration = min(CHUNKS_SIZE, amount)
    print(
        "generating %s values, chunk of %s, with prefix='%s'"
        % (amount, amount_in_iteration, prefix)
    )

    proceed = 0
    for i in range(0, amount, amount_in_iteration):
        alphabet = list(ALPHABET)
        np_alphabet = np.array(alphabet)
        np_codes = np.random.choice(np_alphabet, [amount_in_iteration, KEY_LENGTH])
        data_to_insert = {
            prefix + "".join(np_codes[i]): prefix
            for i in range(len(np_codes))
        }
        my_index.update(data_to_insert)

        proceed += amount_in_iteration
        if (proceed % 150000) == 0:
            print("done generating %s values" % (proceed))
    return my_index


@contextmanager
def overriding_btree_max_leaf_size(max_leaf_size):
    try:
        print('warning!!! mocking max_leaf_size!!!')
        with patch.object(OOBTreePy, "max_leaf_size", max_leaf_size):
            yield
    finally:
        print('warning!!! mocking max_leaf_size has over!!')


def _freqs_to_data(freqs):
    return [x for num, freq in freqs.items() for x in [num] * round(freq)]


def generate_zipf_dist_custom_leaf(num_of_values, domain_size, skew_factor=0, leaf_size=30):
    with overriding_btree_max_leaf_size(leaf_size):
        return generate_zipf_dist(num_of_values, domain_size, skew_factor)


def generate_zipf_dist_in_random_order(num_of_values, domain_size, skew_factor=0):
    data = _generate_zipf_key_value_data(domain_size, num_of_values, skew_factor)
    data_items = list(data.items())
    random.shuffle(data_items)
    data_items_dict = dict(data_items)
    my_index = OOBTreeExt()
    my_index.update(data_items_dict)
    my_index.set_skew_factor(skew_factor)
    my_index.set_data_generation_method('zipf_random_order')
    my_index.set_domain_size(domain_size)
    print("finish at %s" % datetime.now())
    return my_index


def generate_zipf_dist(num_of_values, domain_size, skew_factor=0):
    print("start time %s" % datetime.now())
    data = _generate_zipf_key_value_data(domain_size, num_of_values, skew_factor)

    my_index = OOBTreeExt()
    my_index.update(data)
    my_index.set_skew_factor(skew_factor)
    my_index.set_data_generation_method('zipf')
    my_index.set_domain_size(domain_size)
    print("finish at %s" % datetime.now())
    return my_index


def _pad_numeric_value(number):
    # we are padding each number to len(str(MAX_ZIPF_INT)), and then adding 5 random digits.
    number = MAX_ZIPF_INT + number
    random_digits = random.randint(1_000_000_000, 9_999_999_999)
    assert len(str(random_digits)) == INT_SUFFIX_LEN
    number = int(str(number) + str(random_digits))
    return number

def _unpad_numeric_value(number):
    return int(str(number)[:-INT_SUFFIX_LEN]) - MAX_ZIPF_INT


def _generate_zipf_key_value_data(domain_size, num_of_values, skew_factor):
    relation_size = num_of_values
    z = skew_factor
    num_to_freqs = {}
    zipf_denominator = sum(1 / inner_i ** z for inner_i in range(1, domain_size + 1))
    for i in range(1, domain_size + 1):
        num_to_freqs[i] = relation_size * (1 / i ** z) / zipf_denominator
    data = _freqs_to_data(num_to_freqs)
    data = dict(zip(map(_pad_numeric_value, data), data))
    return data