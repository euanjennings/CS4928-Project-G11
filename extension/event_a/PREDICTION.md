# Event A prediction

The held-out cases are MapperHelper from Mapper (case 13, parent commit 5fda159c7bcf1ec423ba27bd1bb4bacdcdd4b521) and NetClient from Mindustry (case 3490, parent commit a64efce5a0a171d88675f3beccaa617641b8ba78). Both are drawn from the ClassSplitter position-study dataset and were not used in M2.

Using the unchanged M2 decomposition method and seed 2026, we expect ClassSplitter to achieve a higher mean overall MoJoFM than the Bavota baseline, but with a smaller gap than M2's approximately 0.1605. The decompositions will be compared with the dataset's developer-split references.

Positional proximity should help group methods that share a responsibility, but may mislead when unrelated methods are adjacent or cohesive methods are scattered.

If Bavota matches or exceeds ClassSplitter's mean, that would challenge whether M2's advantage transfers to these cases. An equal or larger positive gap would contradict the prediction of a smaller advantage.

The exact input rows and revisions are recorded in [cases.csv](cases.csv).
