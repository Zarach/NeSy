sunshine(1).
sunshine(2).
0.0::sunshine(3).

windok(1).
0.5::windok(2).
windok(3).

surfing(1).
0.8::surfing(2).
0.0::surfing(3).

base(sunshine(day)).
base(surfing(day)).
base(windok(day)).

mode(sunshine(+)).
mode(windok(+)).

learn(surfing/1).