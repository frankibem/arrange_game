size(0..3).
block(b1). block(b2). block(b3). block(b4). block(b5). block(b6). block(b7). block(b8). 

% Assigned weights
weight(b4, 1). weight(b1, 3). weight(b2, 2). weight(b5, 3). weight(b3, 3). weight(b7, 4). weight(b8, 4). weight(b6, 2). 

% Initial cell configuration
holds(on(b4, 0, 0), 0).
holds(on(b1, 1, 0), 0).
holds(on(b2, 2, 0), 0).
holds(on(hole, 0, 1), 0).
holds(on(b5, 1, 1), 0).
holds(on(b3, 2, 1), 0).
holds(on(b7, 0, 2), 0).
holds(on(b8, 1, 2), 0).
holds(on(b6, 2, 2), 0).

% Desired goal
goal(I) :- holds(on(b1, 0, 0), I), holds(on(b2, 1, 0), I), holds(on(b3, 2, 0), I), holds(on(b4, 0, 1), I), holds(on(b5, 1, 1), I), holds(on(b6, 2, 1), I), holds(on(b7, 0, 2), I), holds(on(b8, 1, 2), I), holds(on(hole, 2, 2), I).

#const n = 6.
step(0..n).

item(X) :- block(X).
item(hole).

dir(left). dir(right). dir(up). dir(down).

fluent(on(I, X, Y), inertial) :- item(I), size(X), size(Y).
action(move(B, D)) :- block(B), dir(D).

% Weight calculation
total_weight(N) :- goal(I), sum(I, N).

sum(0, 0).
sum(I, N) :- sum(I-1, N1), occurs(move(B, D), I-1), weight(B, W), N = N1 + W.

% Causal laws
% Moving B up causes it to go up and the hole to go down
holds(on(B, X, Y-1), I+1) :- occurs(move(B, up), I), holds(on(B, X, Y), I).
holds(on(hole, X, Y), I+1) :- occurs(move(B, up), I), holds(on(B, X, Y), I).

% Moving B down causes it to go down and the hole up
holds(on(B, X, Y+1), I+1) :- occurs(move(B, down), I), holds(on(B, X, Y), I).
holds(on(hole, X, Y), I+1) :- occurs(move(B, down), I), holds(on(B, X, Y), I).

% Moving B to the right causes it to go right and the hole left
holds(on(B, X+1, Y), I+1) :- occurs(move(B, right), I), holds(on(B, X, Y), I).
holds(on(hole, X, Y), I+1) :- occurs(move(B, right), I), holds(on(B, X, Y), I).

% Moving B to the left causes it to go to the left and the hole right
holds(on(B, X-1, Y), I+1) :- occurs(move(B, left), I), holds(on(B, X, Y), I).
holds(on(hole, X, Y), I+1) :- occurs(move(B, left), I), holds(on(B, X, Y), I).

% State constraints
% An item can only be in one location
-holds(on(C, X1, Y1), I) :- holds(on(C, X2, Y2), I), -same(X1, Y1, X2, Y2).

same(X1, Y1, X2, Y2) :- X1 == X2, Y1 == Y2,
						size(X1), size(X2), size(Y1), size(Y2).
-same(X1, Y1, X2, Y2) :- not same(X1, Y1, X2, Y2),
						 size(X1), size(X2), size(Y1), size(Y2).

% Two items cannot share the same location
-holds(on(C, X, Y), I) :- holds(on(C1, X, Y), I), C != C1,
						  item(C), item(C1).

% Executability conditions
% Block B can't be moved to the right, it the hole is not to its right...
-occurs(move(B, right), I) :- holds(on(B, X, Y), I), -holds(on(hole, X+1, Y), I).
-occurs(move(B, left), I) :- holds(on(B, X, Y), I), -holds(on(hole, X-1, Y), I).
-occurs(move(B, up), I) :- holds(on(B, X, Y), I), -holds(on(hole, X, Y-1), I).
-occurs(move(B, down), I) :- holds(on(B, X, Y), I), -holds(on(hole, X, Y+1), I).


% Inertial axioms
holds(F, I+1) :- fluent(F, inertial), holds(F, I), not -holds(F, I+1), I < n.
-holds(F, I+1) :- fluent(F, inertial), -holds(F, I), not holds(F, I+1), I < n.

% CWA for actions
-occurs(A, I) :- not occurs(A, I),
				 action(A), step(I).

% Planning module
% Failure is unacceptable
success :- goal(I).
:- not success.

% An action either occurs or not when the goal has not been achieved
occurs(A, I) | -occurs(A, I) :- not goal(I),
								action(A), step(I).

% Concurrent actions are not allowed
:- occurs(A1, I), occurs(A2, I), A1 != A2.

% An action must occur at each step before the goal is achieved
action_occurred(I) :- occurs(A, I).
:- not action_occurred(J), goal(I), J < I,
   step(I), step(J), not goal(I - 1).

% We want to minimize the total weight
#minimize { X : total_weight(X) }.

#show occurs/2.
#show total_weight/1.