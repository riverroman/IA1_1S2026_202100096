padre(juan,pedro).
padre(juan, luis).
padre(luis, carlos).

ancestro(X,Y) :- padre(X,Y).
ancestro(X,Y) :- padre(X,Z), ancestro(Z,Y).