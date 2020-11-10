# Author: Erling Rennemo Jellum
# Date: November 10 2020
# Purpose: This is an initial implementation of the Auction method this will serve as a baseline
# for FPGA acceleration on the PYNQ platform
# This is largely ported from Edmund Brekkes Matlab implementation

import numpy as np

def auctionMethodExtended(rewardMatrix, debug=True):
    ###
    # INPUTS:
    # rewardMatrix    A nxm numpu array containing the costMatrix for the assignment problem
    # OUTPUTS:
    # assignments
    # assignmentsTrack
    numMeas = rewardMatrix.shape[0]
    numTracks = rewardMatrix.shape[1]


    if debug:
        print(f"numMeas={numMeas}")


    epsilon = 0.01
    prices = np.zeros(numMeas)
    unassigned = list(range(numMeas))
    assignments = np.full(numTracks, fill_value=-1, dtype=np.int)


    k = 0
    while len(unassigned) > 0:
        k = k + 1

        # Step 1 - pick first unassigned target so we can find a measurement for it
        unassignedOld = unassigned
        trackCurrent = unassigned.pop(0)

        # Step 2 - Find tentative assignment for each track
        assignmentsTentative = np.full((numTracks), fill_value=np.nan, dtype=np.int)
        for i in range(numTracks):
            possibleMeasurements = np.where(rewardMatrix[:, i] > -np.inf) # Find all measurements for the given target that doesnt have infinite price

            a1 = rewardMatrix[possibleMeasurements, np.full_like(possibleMeasurements, fill_value=i)]
            a2 = prices[possibleMeasurements]

            a = a1-a2
            max = np.max(a)
            maxIdx = np.where(a==max)[1][0]
            assignmentsTentative[i] = possibleMeasurements[0][maxIdx]

        if debug:
            print(f"Iteration-{k} Step 2: tentative ass = {assignmentsTentative}")

        # Step 4 - find all tracks sharing preferred measurement with our trackCyrrent
        trackCurrentPreferredMeasurement = assignmentsTentative[trackCurrent]
        trackConflicts = np.where(assignments == trackCurrentPreferredMeasurement)

        # Remove the current track from the conflicts
        trackConflicts = np.delete(trackConflicts, np.where(trackConflicts == trackCurrent))

        # Loop through all the conflicting tracks
        # If some of the conflicting tracks has already been assigned. Unassign them and add them to
        # the unassigned list
        for i in range(np.size(trackConflicts)):
            # If The conflicting track is already assigned
            if(np.size(np.where(np.array(unassigned) == trackConflicts[i])) == 0):
                assignments[trackConflicts[i]] = -1
                unassigned.append(trackConflicts[i])


        # Assign preferred measurement of current track to current assignment
        assignments[trackCurrent] = trackCurrentPreferredMeasurement

        # Step 5 - Find all measurements feasible for currentTrack and their value
        possibleMeasurements = np.where(rewardMatrix[:,trackCurrent] != np.inf)
        a = rewardMatrix[possibleMeasurements, trackCurrent] - prices[possibleMeasurements]

        # Find 2 best measurements for trackCurrent
        sorted = np.sort(a[0])
        best = sorted[-1]
        if len(sorted) > 1:
            nextBest = sorted[-2]
        else:
            nextBest = 0
        # calculate the gain from choosing best over next best
        gain = best - nextBest

        prices[trackCurrentPreferredMeasurement] = prices[trackCurrentPreferredMeasurement] + gain + epsilon



    return assignments







