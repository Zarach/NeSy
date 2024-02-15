import glob
import os
import pandas as pd
from datetime import datetime

def load_csv_from_folder(folder, index=None, axis=0):
    script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
    rel_path = f"{folder}/*.csv" #DataBases/
    abs_path = os.path.join(script_dir, rel_path)

    all_files = glob.glob(abs_path)
    all_files.sort()

    li = []


    for filename in all_files:
        if index is not None:
            df = pd.read_csv(filename, header=0, index_col=index, parse_dates=[index])
        else:
            df = pd.read_csv(filename, header=0)
        li.append(df)

    return pd.concat(li, axis=axis, ignore_index=False)

def extract_rule_head(string):
    string = string.split(":-")[0]
    string = string.replace(" ", "")
    string = string.replace(")", "")
    string_list = string.split("(")
    functor = string_list[0]
    variables = string_list[1].split(",")
    arity = len(variables)

    return functor, arity

class Fact(object):
    def __init__(self, functor=None, probability=1.0, *args):
        self.__functor = functor
        self.__args = args
        self.__arity = len(self.__args)
        self.__probability = probability
        self.repr = f"{functor}({args})"

    @property
    def args(self):
        """Term arguments"""
        return self.__args

    @property
    def functor(self):
        """Term arguments"""
        return self.__functor

    @property
    def probability(self):
        """Term arguments"""
        return self.__probability

    def from_string(self, string):
        self.repr = string
        string = string.replace(")", "")
        string = string.replace(".", "")
        if "::" in string:
            split_string = string.replace(")", "").split("::")
            self.__probability = split_string[0]
            split_string = split_string[1].split("(")
        else:
            self.__probability = 1.0
            split_string = string.split("(")
        self.__functor = split_string[0]
        self.__args = split_string[1].split(", ")
        self.__arity = len(self.__args)

        return self

    def has_constant(self, string):
        for arg in self.__args:
            if arg == string:
                return True
        return False

class Facts(list):

    @classmethod
    def from_string(cls, string):
        factstring_list = string.split('. ')
        factstring_list.pop()
        facts = cls()
        for fact_string in factstring_list:
            facts.append(Fact().from_string(fact_string))
        return facts

    @classmethod
    def from_list(cls, list):
        facts = cls()
        for fact_string in list:
            facts.append(Fact().from_string(fact_string))
        return facts

    def find_facts_with_value(self, value):
        objs = Facts()
        for obj in self:
            if obj.has_constant(value):
                objs.append(obj)
        return objs

    def find_facts_with_values(self, values):
        objs = Facts()
        for value in values:
            objs = objs + self.find_facts_with_value(value)
        return objs


    def find_facts_with_functor(self, functor):
        objs = Facts()
        for obj in self:
            if obj.functor == functor:
                objs.append(obj)
        return objs

    def remove_facts_with_functor(self, functor):
        return Facts([x for x in self if not x.functor == functor])

    def get_all_values(self, positions=None):
        values_list = []
        if positions is not None:
            for position in positions:
                values = []
                for value in self:
                    values.append(value.args[position])
                values_list.append(values)

        return values_list


def value_to_date(value):
    return datetime.strptime(value.replace("'", ""), '%Y-%m-%d %H:%M:%S')

def intersection(lst1, lst2):
    lst3 = []
    for element in lst1:
        if element in lst2:
            lst3.append(element)
    return lst3


class ActivityFacts(Facts):

    def facts_to_dataframe(self, functor):
        functor_facts = self.find_facts_with_functor(functor)
        start_facts = TemporalFacts(self.find_facts_with_functor('start'))
        end_facts = TemporalFacts(self.find_facts_with_functor('end'))

        start_date = value_to_date(start_facts.give_first())
        end_date = value_to_date(end_facts.give_last())
        periods = (end_date - start_date).total_seconds()+1

        rng = pd.date_range(start_date, periods=periods, freq='s')
        df = pd.DataFrame({'Val': 0}, index=rng)

        for fact in functor_facts:
            for arg in fact.args:
                functor_start_facts = start_facts.find_facts_with_value(arg)
                functor_end_facts = end_facts.find_facts_with_value(arg)
                start_time_activity = value_to_date(functor_start_facts[0].args[1])
                end_time_activity = value_to_date(functor_end_facts[0].args[1])
                df.loc[start_time_activity:end_time_activity, 'Val'] = fact.probability

                if len(functor_start_facts) > 1:
                    print(f"Warning: More than one start date for {fact}")
                if len(functor_end_facts) > 1:
                    print(f"Warning: More than one end date for {fact}")
                if len(functor_start_facts) == 0:
                    print(f"Warning: No start date for {fact}")
                if len(functor_end_facts) == 0:
                    print(f"Warning: No end date for {fact}")

                print(f"{fact.repr}: {functor_start_facts[0].repr} - {functor_end_facts[0].repr}")

        return df

    def loc(self, start, end):
        start_facts = TemporalFacts(self.find_facts_with_functor('start'))
        end_facts = TemporalFacts(self.find_facts_with_functor('end'))
        start_facts = start_facts.loc(start, end)
        end_facts = end_facts.loc(start, end)
        values_start = start_facts.get_all_values([0])
        values_end = end_facts.get_all_values([0])
        matches = intersection(values_start[0], values_end[0])
        resultset = self.find_facts_with_values(matches)
        return resultset


class TemporalFacts(Facts):

    sorted = False

    def give_first(self):
        self.sort()
        return self[0].args[1]

    def give_last(self):
        self.sort()
        return self[len(self)-1].args[1]

    def loc(self, start, end):
        self.sort()
        start = value_to_date(start)
        end = value_to_date(end)
        return TemporalFacts([element for element in self if value_to_date(element.args[1]) >= start and value_to_date(element.args[1]) <= end])


    def sort(self):
        if not sorted:
            self.sort(key=lambda x: x.args[1], reverse=False)

