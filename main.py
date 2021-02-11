from auction import *
import stonesoup_auction
import numpy as np
import scipy.io
import sys

def main():
    print("Hello World!")
    C = np.array([[-np.inf,     2,          -np.inf,    -np.inf,     3],
                  [7,           -np.inf,    23,         -np.inf,    -np.inf],
                  [ 17,         24,         -np.inf,    -np.inf,    -np.inf],
                  [ -np.inf,    6,          13,         20,         -np.inf]])
    maximize=True
    gain, col4row, row4col=stonesoup_auction.assign2D(C,maximize)
    print(f"col4row={col4row}")
    print(f"row4col={row4col}")
    print(f"gain={gain}")
    C = np.array([[-np.inf, 2, -np.inf, -np.inf, 3],
                  [7, -np.inf, 23, -np.inf, -np.inf],
                  [17, 24, -np.inf, -np.inf, -np.inf],
                  [-np.inf, 6, 13, 20, -np.inf]])
    print(C[0][1])
    gain, ass = auctionMethodExtended(C, debug=False)
    print("Extended done")
    print(gain)
    print(ass)
    print("===============")

    gain, ass, iterations = auctionImproved(C, debug=False)
    print("Improved done")
    print(f"gain={gain}\nass={ass}\niter={iterations}")
    print("===============")


    gain, ass, iterations = auctionPipelined(C, debug=False, depth=2)
    print("Pipelined done")
    print(f"gain={gain}\nass={ass}\niter={iterations}")
    print("===============")


def verifyAss(ssAss, erlingAss):
    for i in range(len(ssAss)):
        if ssAss[i] != erlingAss[i]:
            return False
    return True

def verifyGain(ssGain, erlingGain, threshold=0.1):
    if abs(ssGain - erlingGain) > threshold:
        return False
    else:
        return True

def cleanMatrix(mat):
    # If we have negative values
    res = mat.copy()
    if np.where(mat[:] < 0)[0].shape[0] > 0:
        res = res * -1

    res[np.where(res[:] == np.inf)] = -np.inf
    #res[np.where(res[:] == -np.inf)] = 0
    return res

def runNmRewards():
    rewMats = scipy.io.loadmat('rewards/rewards.mat')
    rewMats = rewMats['nmRewards'][0]

    mats = [cleanMatrix(mat) for mat in rewMats]

    for idx, mat in enumerate(mats):
        print(f"Problem-{idx}")
        gain, col4row, row4col=stonesoup_auction.assign2D(mat,True)
        gainExt, assExt, iterExt = auctionMethodExtended(mat, debug=False)
        gainImp, assImp, iterImp = auctionImproved(mat, debug=False)

        gainPipe, assPipe, iterPipe = auctionPipelined(mat, depth=1, debug=False)
        if not (verifyAss(row4col,assExt) and
                verifyAss(row4col,assImp) and
                verifyAss(row4col,assPipe) and
                verifyGain(gain, gainExt) and
                verifyGain(gain, gainImp) and
                verifyGain(gain, gainPipe)):
            assert(False)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "runNmRewards":
            runNmRewards()
        else:
            print(f"unrecognized option {sys.argv[1]}")
            exit(-1)


    else:
        runNmRewards()