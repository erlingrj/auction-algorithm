## Background

### Auction algorithm org paper
https://web.mit.edu/dimitrib/www/Auction_Encycl.pdf
- n persons, m objects
- goal gind set of (1,j_1) -> (n, j_n) that maximizes benefit

If object j as price p_j the net value for person i buying object j is
a_ij - p_j.
 
In an auction setting, each object would be sold to the person bidding most and he woud
get the benefit of the difference between the 2 highest a_ij sfor that j.

Each agent would like to be assigned to the object that gives it the most value

#### Naive auction method
Iterative process: Starts out with an arbitrarty assignment and an arbitrary set of prices
If all agents are happy. We terminate

If some agent is unhappy we proceed like this:
- agent i finds object j which offers maximum value to him for the given price
- agent i exchanges objects with agent which has j. Sets the price of j to the level at which he is indifferent between j and next nest

We introduce epsilon to ensure that we will find a solution

- agent is almost happy if his value is within epsilon of maximal value
- Almost at equilibirum if all agents are at least almost happy

At each round the bidder sets the price of object j to a little higher than the value of its second best
so he is almost happy at the end of a round.

Once an object has received a bid for the first time, the agent subscribed to that object for all subsequent rounds will be almost happy

THis means that once all objects have received a bid, the auction terminates as we will be in a state where all agents are almost happy





## November 8
- First implementation based on Edmunds works but it doesnt generate the correct values versus the stonesoup version.
- Basically what happens is that each I pick the best measurement for each track and then the last track automatically gets dumped. It is not correct.
- I should be able to unpick some measurements??

Figure this out ater. But you need a more solid understanding of what is happeniing here....
