import roman
from sklearn.metrics import f1_score, recall_score, precision_score
from problog import get_evaluatable
from problog.formula import LogicFormula, Term
from problog.program import PrologString
from matplotlib import pyplot as plt


import pandas as pd

import Utils
from ProbFOIL21 import probfoil
import json
import os

from Utils import Fact, Facts, ActivityFacts, extract_rule_head



print('start')
class LogicalPlausibility:

    def numerous_grounding(self, grounding_rule, grounding_facts, ground_members):
        print(f"Grounding -> {grounding_rule}")
        number_of_variables = grounding_rule.split(":-")[0].count(",")
        label = grounding_rule.split("(")[0]
        query = f"query({label}(_{', _'*number_of_variables}))"
        grounding_rule = grounding_rule.replace("[members]", f"member(B, {ground_members})")

        facts_and_rule = f"{grounding_facts} {grounding_rule} {query}. "
        facts_and_rule = f":- use_module(library(bedu)). {facts_and_rule} "
        facts_and_rule = f" :- use_module(library(lists)). {facts_and_rule}"

        pl_string = PrologString(facts_and_rule)


        lf = get_evaluatable().create_from(pl_string).evaluate()
        output = ""
        for fact in lf:
            if lf[fact] != 1.0:
                prob_string = str(lf[fact])+"::"
            else:
                prob_string = ""
            output += prob_string+str(fact)+". "

        return output

    def grounding(self, grounding_rule, grounding_facts):
        print(f"Grounding -> {grounding_rule}")
        number_of_variables = grounding_rule.split(":-")[0].count(",")
        label = grounding_rule.split("(")[0]
        query = f"query({label}(_{', _'*number_of_variables}))"

        facts_and_rule = f":- use_module(library(bedu)). {grounding_facts} {grounding_rule} {query}. "

        pl_string = PrologString(facts_and_rule)

        lf = get_evaluatable().create_from(pl_string).evaluate()
        grounded = ""
        for fact in lf:
            if lf[fact] != 1.0:
                prob_string = str(lf[fact])+"::"
            else:
                prob_string = ""
            grounded += prob_string+str(fact)+". "

        return grounded

    def evaluate(self, rules, fact_file):
        # read facts for testing
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = f"ProbFOIL21/bedu_experiments/{fact_file}"
        abs_file_path = os.path.join(script_dir, rel_path)
        f = open(abs_file_path, "r")
        string = f.read()
        string = string.replace("\n", " ")
        functor, arity = extract_rule_head(rules[0])
        string = string.replace(functor, "act_tmp")

        # List of original facts from Neural Network without the predicate which will be evaluated
        fact_list_start = Facts.from_string(string)
        fact_list_start = fact_list_start.remove_facts_with_functor('act_tmp')

        for rule in rules:
            self.rules_list.append(" " + str(rule))
            string += " " + str(rule)

        query = f" query({functor}(_{', _'*(arity-1)}))."
        pl_string = PrologString(string + query)
        lf = get_evaluatable().create_from(pl_string).evaluate()

        # List of evaluated facts
        fact_list = Facts()
        for i, eval_fact in enumerate(lf):
            fact_list.append(Fact().from_string(str(eval_fact)))

        # List of combined original and evaluated facts
        fact_list_new = ActivityFacts(fact_list_start+fact_list)

        # Build ground truth dataframe for Neural Network training
        df = fact_list_new.facts_to_dataframe(functor)

        print('Found Facts: ' + str(lf))

        return df, fact_list_new

    def learn(self, fact_file):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = f"ProbFOIL21/bedu_experiments/{fact_file}"
        abs_file_path_facts = os.path.join(script_dir, rel_path)

        rel_path = "ProbFOIL21/bedu_experiments/test_settings.pl"
        abs_file_path_settings = os.path.join(script_dir, rel_path)

        rules, accuracy = probfoil.main(
            [abs_file_path_facts, abs_file_path_settings, "-vvvv", "-m", "1"])

        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = "DataBases/rules.json"
        abs_file_path = os.path.join(script_dir, rel_path)

        rules_json = []
        for rule in rules:
            rule_string = str(rule.head) + ' :- ' + 'act(A)'
            for body_predicat in rule.body.args:
                rule_string = rule_string + ', ' + str(body_predicat)
            rule_string = rule_string + '.'
            rules_json.append(rule_string)

        with open(abs_file_path, 'w') as rules_file:
            json_string = json.dumps(rules_json, ensure_ascii=False, indent=4)
            rules_file.write(json_string)

        return rules

    def load_rules(self, file = "rules.json"):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = f"DataBases/{file}"
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path, 'r') as f:
            rules_list = json.load(f)
        #rules = ' '.join(str(e) for e in rules_list)
        return rules_list

    def load_facts(self, database_root, file='facts.json', start="1000-01-01 00:00:00", end="9999-12-31 23:59:59"):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = f"{database_root}/Facts/{file}"
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path, 'r') as f:
            facts_list_string = json.load(f)

        facts_list = ActivityFacts.from_list(facts_list_string)
        facts_list = facts_list.loc(start, end) # Train "2022-12-05 00:00:00", "2023-01-31 23:59:59" Test "2023-02-01 00:00:00", "2023-12-31 23:59:59"
        facts_string = ' '.join(e.repr for e in facts_list)
        facts_string += ' '

        return facts_string, facts_list

    def save_facts(self, facts, database_root):
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = f"{database_root}/Facts/facts_grounded.json"
        abs_file_path = os.path.join(script_dir, rel_path)

        with open(abs_file_path, 'w') as facts_file:
            json_string = json.dumps(facts, ensure_ascii=False, indent=4)
            facts_file.write(json_string)

    def save_facts_for_probfoil(self, facts, filename):
        rel_path = f"ProbFOIL21/bedu_experiments/{filename}"
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, rel_path)
        with open(abs_file_path, 'w') as facts_file:
            facts_file.write(facts)


    def save_apl_on_phases(self, input_filepath: str, output_filepath: str, resampling: int = 1):
        """
        Save the on phases of the appliances given an input file an action sequence input file

        Parameters
        ----------
        input_filepath : str
            path where the input data is loaded

        output_filepath : str
            path where the output data is stored

        resampling : int
            resampling rate of the output

        """
        input_df = pd.read_csv(input_filepath)
        appliances = input_df['name'].str.split(';\s*', expand=True).stack().unique().tolist()
        df = pd.DataFrame(0, index=range(0, 86400, resampling), columns=appliances)
        df.index = pd.to_datetime(df.index, unit='s', origin=pd.Timestamp(input_df.iloc[0, 1].split(" ")[0]))
        df.index.name = 'timestamp'
        for index, row in input_df.iterrows():
            df.loc[pd.to_datetime(row[1]):pd.to_datetime(row[2]), row[0]] = 1
        df.to_csv(f'{output_filepath}{input_filepath.split(".")[0]}_on_phases.csv')


    #duration_fact_string = duration_grounding()

    # Test I: "2022-12-19 00:00:00", "2023-01-01 23:59:59"
    # Test II: "2023-01-02 00:00:00", "2023-01-15 23:59:59"
    # Test III: "2023-01-16 00:00:00", "2023-01-29 23:59:59"
    # Test IV: "2023-01-30 00:00:00", "2023-02-12 23:59:59"
    # Test V: "2023-02-13 00:00:00", "2023-02-26 23:59:59"
    # Test VI: "2023-02-27 00:00:00", "2023-03-12 23:59:59"
    # Test VII: "2023-03-13 00:00:00", "2023-03-26 23:59:59"

    def check_plausibility(self, experiment_number, period_start, period_end, database_root="DataBases", results_root="Results", test=True):
        print(period_start + ' - ' + period_end)
        self.rules_list = []
        rules = self.load_rules("rules_manual.json")
        facts_string, fact_list = self.load_facts(database_root, f'facts_from_ml_sensors_finetuned_{roman.toRoman(experiment_number-1)}.json', period_start, period_end)

        print(f"loading facts from {database_root}facts_from_ml_sensors_finetuned_{roman.toRoman(experiment_number-1)}.json")
        print(f"start period: {period_start}")
        print(f"end period: {period_end}")

        facts_string += self.grounding(grounding_rule='act(A) :- kettle(A).', grounding_facts=facts_string) # ; coffee(A); washing_machine(A); microwave(A); toaster(A); television(A).
        facts_string += self.grounding(grounding_rule='duration(A, B) :- start(A,C), get_stamp(C, D), end(A,E), get_stamp(E, F), B is F-D.', grounding_facts=facts_string)
        facts_string += self.grounding(grounding_rule='weekday(A, B) :- start(A,C), get_weekday(C, B).', grounding_facts=facts_string)
        facts_string += self.grounding(grounding_rule='start_hour(A, B) :- start(A,C), get_hour(C, B).', grounding_facts=facts_string)
        facts_string += self.numerous_grounding(grounding_rule='before_hour(A, B) :- start(A,C), get_hour(C, D), [members], D < B.', grounding_facts=facts_string, ground_members=list(range(0, 24, 1))) #list(range(0, 5000, 5)
        facts_string += self.numerous_grounding(grounding_rule='duration_gt(A, B) :- duration(A, C), [members], C > B.', grounding_facts=facts_string, ground_members=list(range(0, 5000, 10)))


        fact_string_list = [e+'.' for e in facts_string.split('. ') if e]

        self.save_facts(fact_string_list, database_root)

        if test:
            self.save_facts_for_probfoil(facts_string, 'test_facts.pl')
            df, fact_list_evaluated = self.evaluate(rules, 'test_facts.pl')


            df_active_phase = Utils.load_csv_from_folder(f"{database_root}/Barthi/active_phases", "timestamp")[['kettle']]
            df_active_phase = df_active_phase.loc[period_start:period_end]
            pd.to_datetime(df_active_phase.index)

            df_eval = pd.concat([df, df_active_phase], axis=1).fillna(0)
            df_eval = df_eval.rename(columns={'Val': "plausibility", 'kettle': "ground truth"})

            script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
            rel_path = f"{results_root}/evaluation_plausibility_manual_{roman.toRoman(experiment_number-1)}.csv"
            abs_file_path = os.path.join(script_dir, rel_path)

            print(f"saving results to {abs_file_path}")

            df_eval.to_csv(abs_file_path, header=['plausibility', 'ground truth'])


            f1 = f1_score(df_eval.loc[:,'ground truth'], df_eval.loc[:,'plausibility'])
            recall = recall_score(df_eval.loc[:,'ground truth'], df_eval.loc[:,'plausibility'], )
            precision = precision_score(df_eval.loc[:, 'ground truth'], df_eval.loc[:, 'plausibility'])

            print('F1: ' + str(f1))
            print('Recall: ' + str(recall))
            print('Precision: ' + str(precision))

        else:
            self.save_facts_for_probfoil(facts_string, 'learning_facts.pl')
            learned_rules = self.learn('learning_facts.pl')

        print("check plausibility done!")


# pl_string = f":- use_module(library(bedu)). {facts} {rules} query(start_hour(_, A)). query(start_minute(_, A)). query(duration(_, A)). "
# print(pl_string)
# lf = get_evaluatable().create_from(pl_string).evaluate()
# print('probability: ' + str(lf))











