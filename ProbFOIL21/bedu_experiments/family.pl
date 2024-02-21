0.5::father(john, mary).
0.5::father(john, billy).
father(helm, kopf).
father(kopf, hals).
father(hulu, an).

mother(mary, tom).
mother(an, jenny).

parent(X,Y) :- mother(X,Y).
parent(X,Y) :- father(X,Y).

0.3::grandfather(john, tom).
grandfather(helm, hals).
grandfather(hulu, jenny).


base(father(person,person)).
base(mother(person,person)).
base(parent(person,person)).
base(grandfather(person,person)).

mode(father(+,-)).
mode(parent(+,-)).
mode(parent(-,+)).
mode(parent(+,+)).

learn(grandfather/2).

example_mode(auto).