import numpy as np

EDGE_WEIGHT_TYPES = {
    "EXPLICIT",
    "EUC_2D",
    "EUC_3D",
    "MAX_2D",
    "MAN_2D",
    "GEO",
    "GEOM",
    "ATT",
    "CEIL_2D",
    "DSJRAND",
}


def write_tsp_file(fp, xs, ys, norm, name):
    """Write data to a TSPLIB file."""
    if len(xs) != len(ys):
        raise ValueError(
            "x and y coordinate vector must have the "
            "same length ({} != {})".format(len(xs), len(ys))
        )
    if norm not in EDGE_WEIGHT_TYPES:
        raise ValueError(
            "Norm {!r} must be one of {}".format(norm, ", ".join(EDGE_WEIGHT_TYPES))
        )

    fp.write("NAME: {}\n".format(name))
    fp.write("TYPE: TSP\n")
    fp.write("DIMENSION: {}\n".format(len(xs)))
    fp.write("EDGE_WEIGHT_TYPE: {}\n".format(norm))
    fp.write("NODE_COORD_SECTION\n")
    for n, (x, y) in enumerate(zip(xs, ys), start=1):
        fp.write("{} {} {}\n".format(n, x, y))
    fp.write("EOF\n")


def read_tsp_tour(fname):
    has_tour = False
    tour = []
    with open(fname) as fp:
        for line in fp:
            if line.startswith("TOUR_SECTION"):
                has_tour = True
            elif line.startswith("EOF"):
                break
            else:
                if has_tour:
                    tour.extend(int(node) for node in line.split())
    if not tour:
        raise RuntimeError("File {} has no valid TOUR_SECTION".format(fname))
    if tour[-1] == -1:
        tour.pop()
    return np.array(tour)

def symmetricize(matrix, k=None):
    """
        Jonker-Volgenant method of transforming (n x n) asymmetric TSP, C into (2n x 2n) symmetric TSP, S.

        Let C be an asymmetric TSP matrix.
        Let k be a very large number, ie k >> C.max()
        Let U = (u_ij) with u_ii = 0, u_ij = k for i != j.

        Construct the (2n x 2n) matrix:
        
                    +-------+
                    | U |C^T|
            S =     |---+---|
                    | C | U |
                    +-------+

        S is a symmetric TSP problem on 2n nodes.
        There is a one-to-one correspondence between solutions of S and solutions of C.
    """
    # if k not provided, make it equal to 10 times the max value:
    if k is None:
        k = round(10*matrix.max())
        
    matrix_bar = matrix.copy()
    np.fill_diagonal(matrix_bar, 0)
    u = np.matrix(np.ones(matrix.shape).astype(int) * k)
    np.fill_diagonal(u, 0)
    matrix_symm_top = np.concatenate((u, np.transpose(matrix_bar)), axis=1)
    matrix_symm_bottom = np.concatenate((matrix_bar, u), axis=1)
    matrix_symm = np.concatenate((matrix_symm_top, matrix_symm_bottom), axis=0)
    
    return matrix_symm
