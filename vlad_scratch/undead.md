* **Node** is an endpoint of an skeleton segment or a point of intersection between skeleton segments.
* **Bone** is a part of a skeleton segment that connects two nodes.
* **Fragment** is a part of a plane surrounded by bones. Fragments are always simple polygons.

Because there are layers, multiple points in the original sheet of paper correspond to a single point in the folded shape.

* **Vertex** is a point from a preimage of a node. There are *corner*, *side*, and *internal* vertices.
* **Edge** is a segment from a preimage of a bone. Some edges are literally paper edges, the rest are internal.
* **Facet** is a polygon from a preimage of a fragment.

Note that mesh formed by vertices, edges, and facets is not necessarily normalized.
It is possible that some internal edges are not creases.
