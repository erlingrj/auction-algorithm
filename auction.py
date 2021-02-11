# Author: Erling Rennemo Jellum
# Date: November 10 2020
# Purpose: This is an initial implementation of the Auction method this will serve as a baseline
# for FPGA acceleration on the PYNQ platform
# This is largely ported from Edmund Brekkes Matlab implementation

import numpy as np


def stepPrices(priceMatrix):
    # Move prices from real -> stale
    retMatrix = priceMatrix.copy()
    nCols = priceMatrix.shape[0]
    for i in range(nCols-1, 0, -1):
        retMatrix[i-1] = priceMatrix[i]
    return retMatrix


def updatePrices(prices, chosenMeas, newPrice):
    res = stepPrices(prices)
    # Try to assign new price to meas (assign to 0-colum which is realPrice)
    if res[-1][chosenMeas] >= newPrice:
        return (res, False)
    else:
        res[-1][chosenMeas] = newPrice
        return (res, True)



def auctionPipelined(rewardMatrix, depth=1, debug=True):
    # Seek to reduce the number of calculations
    # auctionImproved is an improvement over the Matlab implementation from Edmund.

    if debug:
        print(f"========================================")
        print(f"Beginning Improved Auction Method")

    numMeas = rewardMatrix.shape[0]
    numTracks = rewardMatrix.shape[1]
    epsilon = 0.01

    # Intialize data structures
    prices = np.zeros((depth, numMeas))

    unassigned = list(range(numTracks))
    assignments = np.full(numTracks, fill_value=-1, dtype=np.int)

    k = 0
    while len(unassigned) > 0:
        # Each loop iteration the following things happen
        # 1. Pick an unassigned track
        # 2. Find the measurement with most net value for that track (if it exists)
        # 3. Unassign the track that has already been assigned to that measurement, and assign new track
        # 4. Update the price on that measurement

        k = k + 1
        if debug:
            print(f"k={k}")
            print(f"assignments={assignments}")
            print(f"unassigned={unassigned}")
            print(f"prices={prices}")

        # Step 1 - pick first unassigned target
        trackCurrent = unassigned.pop(0)

        if debug:
            print(f"current track={trackCurrent}")

        # Step 2 - Find the measurement with most net value. Net value is reward - price
        stalePrices = prices[0].copy()

        possibleMeas = np.where(rewardMatrix[:, trackCurrent] > -np.inf)
        reward = rewardMatrix[possibleMeas, np.full_like(possibleMeas, fill_value=trackCurrent)]
        price = stalePrices[possibleMeas]
        netValues = reward - price
        netValuesSorted = np.sort(netValues)[0]
        maxValue = netValuesSorted[-1]
        if maxValue > 0:
            maxIdx = np.where(netValues == maxValue)
            chosenMeas = possibleMeas[0][maxIdx[1]]
            if debug:
                print(f"pick measurement {chosenMeas} with net value {maxValue}")
        else:
            # If we cant find any measurement with value for this track.
            # just skip to next iteration. This means also that this track will stay unassigned
            # The prices will only rise so there is not possible to find a measurement that it can afford
            if debug:
                print(f"No measurements with net value")
            continue



        # Step 4 - Update the price
        # The prices is updated to the maximum value currentTrack is willing to pay given the current prices
        # That is equal to the difference between the two highets net values this track can get
        # We already have the highest net value = maxValue. And we have the netValues sorted in netValuesSorted
        if len(netValuesSorted) > 1:
            nextBest = netValuesSorted[-2]
        else:
            nextBest = 0

        newPrice = stalePrices[chosenMeas] + maxValue - nextBest + epsilon
        (prices, update) = updatePrices(prices, chosenMeas, newPrice)

        if update:
            # We successfully updated the price
            trackOld = np.where(assignments == chosenMeas)

            # Unassign it
            for t in trackOld[0]:
                assignments[t] = -1
                unassigned.append(t)
                if debug:
                    print(f"track {t} was unassigned")

            # Assign preferred measurement of current track to current assignment
            assignments[trackCurrent] = chosenMeas
            if debug:
                print(f"new price = {newPrice}")
                print(f"=============================================")

        else:
            if debug:
                print(f"Failed to update price = {newPrice} due to actual={prices[-1][chosenMeas]}")
                print("==============================================")

            unassigned.append(trackCurrent)

    # Lastly we calcualate the "gain". That is the total reward for our chosen assignment
    gain = 0
    for track, meas in enumerate(assignments):
        if meas != -1:
            gain += rewardMatrix[meas][track]

    # Return gain and assignments and n iterations
    return gain, assignments, k


def auctionImproved(rewardMatrix, debug=True):
    # auctionImproved is an improvement over the Matlab implementation from Edmund.
    # Seek to reduce the number of calculations

    if debug:
        print(f"========================================")
        print(f"Beginning Improved Auction Method")


    numMeas = rewardMatrix.shape[0]
    numTracks = rewardMatrix.shape[1]
    epsilon = 0.01

    # Intialize data structures
    prices = np.zeros(numMeas)

    unassigned = list(range(numTracks))
    assignments = np.full(numTracks, fill_value=-1, dtype=np.int)

    k = 0
    while len(unassigned) > 0:
        # Each loop iteration the following things happen
        # 1. Pick an unassigned track
        # 2. Find the measurement with most net value for that track (if it exists)
        # 3. Unassign the track that has already been assigned to that measurement, and assign new track
        # 4. Update the price on that measurement

        k = k + 1
        if debug:
            print(f"k={k}")
            print(f"assignmetns={assignments}")
            print(f"unassigned={unassigned}")
            print(f"prices={prices}")

        # Step 1 - pick first unassigned target
        trackCurrent = unassigned.pop(0)

        if debug:
            print(f"current track={trackCurrent}")


        # Step 2 - Find the measurement with most net value. Net value is reward - price
        possibleMeas = np.where(rewardMatrix[:,trackCurrent]  > -np.inf)
        if len(possibleMeas) == 0:
            if debug:
                print("No measurement with net value")
            continue
        reward = rewardMatrix[possibleMeas, np.full_like(possibleMeas, fill_value=trackCurrent)]
        price = prices[possibleMeas]
        netValues = reward - price
        netValuesSorted = np.sort(netValues)
        maxValue = netValuesSorted[0][-1]
        if maxValue > 0:
            maxIdx = np.where(netValues == maxValue)
            chosenMeas = possibleMeas[0][maxIdx[1]]
            if debug:
                print(f"pick measurement {chosenMeas} with net value {maxValue}")
        else:
            # If we cant find any measurement with value for this track.
            # just skip to next iteration. This means also that this track will stay unassigned
            # The prices will only rise so there is not possible to find a measurement that it can afford
            if debug:
                print(f"No measurements with net value")
            continue

        # Step 3: Find the track that currently is assigned to the chosen measurement and un-assign it
        trackOld = np.where(assignments == chosenMeas)

        # Unassign it
        for t in trackOld[0]:
            assignments[t] = -1
            unassigned.append(t)
            if debug:
                print(f"track {t} was unassigned")

        # Assign preferred measurement of current track to current assignment
        assignments[trackCurrent] = chosenMeas

        # Step 4 - Update the price
        # The prices is updated to the maximum value currentTrack is willing to pay given the current prices
        # That is equal to the difference between the two highets net values this track can get
        # We already have the highest net value = maxValue. And we have the netValues sorted in netValuesSorted
        if len(netValuesSorted) > 1:
            nextBest = netValuesSorted[-2]
        else:
            nextBest = 0

        newPrice = maxValue - nextBest + epsilon
        prices[chosenMeas] = newPrice


        if debug:
            print(f"new price = {newPrice}")
            print(f"=============================================")

    # Lastly we calcualate the "gain". That is the total reward for our chosen assignment

    gain = 0
    for track, meas in enumerate(assignments):
        if meas != -1:
            gain += rewardMatrix[meas][track]

    # Return gain and assignments
    return gain, assignments, k


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
        print(f"========================================")
        print(f"Beginning Auction Method")



    epsilon = 0.01
    prices = np.zeros(numMeas)
    unassigned = list(range(numTracks))
    assignments = np.full(numTracks, fill_value=-1, dtype=np.int)


    k = 0
    while len(unassigned) > 0:
        k = k + 1
        if debug:
            print(f"k={k}")
            print(f"unassigned={unassigned}")

        # Step 1 - pick first unassigned target so we can find a measurement for it
        unassignedOld = unassigned
        trackCurrent = unassigned.pop(0)

        if debug:
            print(f"track={trackCurrent}")

        # Step 2 - Find tentative assignment for each track
        assignmentsTentative = np.full((numTracks), fill_value=np.nan, dtype=np.int)
        for i in range(numTracks):
            possibleMeasurements = np.where(rewardMatrix[:, i] > -np.inf) # Find all measurements for the given target that doesnt have infinite price
            if len(possibleMeasurements[0]):
                assignmentsTentative[i] = -1
                continue
            # Calculate the net value for each measurement to that track
            a = rewardMatrix[possibleMeasurements, np.full_like(possibleMeasurements, fill_value=i)]
            p = prices[possibleMeasurements]
            net_value = a-p

            # Find the measurement with highest net value
            max = np.max(net_value)
            if max > 0:

                maxIdx = np.where(net_value==max)[1][0]
                # Pick that as a tentative assigment
                assignmentsTentative[i] = possibleMeasurements[0][maxIdx]
            else:
                assignmentsTentative[i] = -1

        # Step 4 - find all tracks sharing preferred measurement with our trackCurrent
        trackCurrentPreferredMeasurement = assignmentsTentative[trackCurrent]
        if trackCurrentPreferredMeasurement == -1:
            continue
        trackConflicts = np.where(assignments == trackCurrentPreferredMeasurement)
        if debug:
            print(f"preferred meas={trackCurrentPreferredMeasurement}")
        # Remove the current track from the conflicts
        trackConflicts = np.delete(trackConflicts, np.where(trackConflicts == trackCurrent))

        # Loop through all the conflicting tracks
        # If some of the conflicting tracks has already been assigned. Unassign them and add them to
        # the unassigned list. This is presumably done because if a conflicting track is assigned
        # That means it is assigned to the same measurement. But it feels very backwards to do it this way
        # Basically this takes the measurement from the guy who had it before
        for i in range(np.size(trackConflicts)):
            # If The conflicting track is already assigned
            if(np.size(np.where(np.array(unassigned) == trackConflicts[i])) == 0):
                #print(f"Steal meas from track={trackConflicts[i]}")
                assignments[trackConflicts[i]] = -1
                unassigned.append(trackConflicts[i])



        # Assign preferred measurement of current track to current assignment
        assignments[trackCurrent] = trackCurrentPreferredMeasurement


        # Step 5 - Find all measurements feasible for currentTrack and their value
        possibleMeasurements = np.where(rewardMatrix[:,trackCurrent] > -np.inf)
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

        if debug:
            print(f"prices={prices}")
            print(f"assignmetns={assignments}")
            print(f"rewardMatric=\n{rewardMatrix}")
            print(f"=============================================")

    gain = 0
    for track, meas in enumerate(assignments):
        if meas != -1:
            gain += rewardMatrix[meas][track]
    return gain, assignments, k







