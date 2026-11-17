# Preserved negative result: ambient exhaustive membership search

The initial exact implementation classified every scenario by enumerating all supports of size at most four from every other ambient point. It passed the unit witnesses but did not complete the frozen 105-case evaluation after more than two minutes and was interrupted.

This failed the protocol's practicality gate. It was not deleted or reframed as a positive result.

The replacement keeps the same exact acceptance criterion but uses a floating hull only to propose a small candidate set. Exact rational membership then proves candidate extremality relative to the proposal and proves coverage of every original point by the final vertices. Any incomplete numerical proposal fails closed.
