%mode(coffeemaking(+)).

%mode(hairdryer(+)).
%mode(hairstraightener(+)).
%mode(morning(+)).

%mode(washingmachine(+)).
%mode(toaster(+)).

mode(kettle(+)).
mode(duration_gt(+,c)).
mode(weekday(+,c)).
mode(before_hour(+, c)).
mode(start_hour(+, c)).
%mode(duration_lt(+,c)).

% Type definitions
%base(activity(time,wakeup)).
%base(begin(id,constant)).
%base(tprev(id,id)).
%base(wakeup(id)).
%base(morning(id)).
base(duration_gt(id, dur)).
base(weekday(id, day)).
base(start_hour(id, hour)).
base(before_hour(id, hour)).
%base(duration_lt(id, dur)).
%base(hairdryer(id)).
%base(hairstraightener(id)).
%base(coffeemaking(id)).
%base(toaster(id)).
%base(washingmachine(id)).
base(kettle(id)).
base(coffee(id)).

% Target
learn(kettle/1).

% How to generate negative examples
example_mode(auto).