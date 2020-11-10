from auction import *
import stonesoup_auction
import numpy as np

def main():
    print("Hello World!")
    C = np.array([[-np.inf,   2,   -np.inf, -np.inf,  3],
                  [7,   -np.inf,   23, -np.inf,  -np.inf],
                  [ 17, 24,  -np.inf,  -np.inf,  -np.inf],
                  [ -np.inf,   6,  13, 20, -np.inf]])
    maximize=True
    gain, col4row, row4col=stonesoup_auction.assign2D(C,maximize)
    print(f"col4row={col4row}")
    print(f"row4col={row4col}")

    C = np.array([[-np.inf, 2, -np.inf, -np.inf, 3],
                  [7, -np.inf, 23, -np.inf, -np.inf],
                  [17, 24, -np.inf, -np.inf, -np.inf],
                  [-np.inf, 6, 13, 2, -np.inf]])
    ass = auctionMethodExtended(C, debug=True)
    print(ass)


if __name__ == "__main__":
    main()