# efficient_sampling
This project implement advanced method for effieicnt sampling from B+Trees. \\
For that, we use (B+Trees)[https://pypi.org/project/BTrees/] open source (the "PURE\_PYTHON" version), and implemented the different method over it.

### Theoretical background
This code were used for a research on databases sampling (i.e B+Trees).
More theoretical background will be added soon.

## B+Trees creation
### B+Tree Zipfian Data Distribution
```
import build_tree
index = build_tree.generate_zipf_dist_in_random_order(num_of_values=1_000_000, domain_size=10_000, skew_factor=1.0)
```


### B+Tree Clustered Data Distribution
```
import build_tree

prefix_to_percent = {
    'gggg': 0.25,
    'hhhh': 0.15,
    'mmmm': 0.10,
    'rrrr': 0.03,
    '': 0.47
}

index = build_tree.generate_btree_index_x_values_with_dist(num_of_values=1_000_000, prefix_to_percent=prefix_to_percent)
```

## Sampling
For sampling for the B+Tree, need to call one of the next methods, each one implementing another method for sampling data from a B+Tree:

```
# index_h3 is a B+Tree with 1_000_000 values, which in our case is a B+Tree of height 3
sampled_data = index_h3.sample_distribution_oriented_height_three(k=10_000)
sampled_data = index_h3.sample_olken_early_abort(k=10_000)
sampled_data = index_h3.sample_olken(k=10_000)
sampled_data = index_h3.sample_naive_random_walk(k=10_000)
sampled_data = index_h3.sample_btwrs(k=10_000)

# index_h4 is a B+Tree with 3_000_000 values, which in our case is a B+Tree of height 4
sampled_data = index_h4.sample_distribution_oriented_height_four(k=10_000)
```
