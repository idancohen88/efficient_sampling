import itertools
from datetime import datetime

from btrees.btree_base import OOBTreeBase


class OOBTreeExtMonkey(OOBTreeBase):
    def sample_monkey(self, k):
        start_time = datetime.now()
        k = self._min_between_k_and_btree_size(k)

        sampled_values = list(itertools.islice(self.iteritems(), k))
        self._persist_sampling_stats(
            start_time=start_time,
            sampled_values=sampled_values,
            name="monkey",
            sample_size=k,
        )

        return sampled_values
