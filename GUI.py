import json
import os
import re

from flask import Flask, render_template, request

from Utils import ActivityFacts

app = Flask(__name__)

@app.route('/')
def home():
   return render_template('test.html')

@app.route('/getFacts', methods=['GET'])
def get_facts():
   args = request.args
   first_activity_id = args.get('activity_id', type=int)

   predicates = []
   predicates_true = []
   fact_string, fact_list = load_facts('facts_grounded.json')
   if(first_activity_id == -1):
      first_activity_id = int(fact_list[0].split('(')[1].split(')')[0])

   # rules = [f"kettle({first_activity_id}) :- act({first_activity_id}), not duration_gt({first_activity_id},130), before_hour({first_activity_id},22)",
   #          f"kettle({first_activity_id}) :- act({first_activity_id}), not duration_gt({first_activity_id},20), duration_gt({first_activity_id},0)",
   #  		f"kettle({first_activity_id}) :- act({first_activity_id}), start_hour({first_activity_id},11), weekday({first_activity_id},4)"];

   rules = [f"kettle({first_activity_id}) :- act({first_activity_id}), not duration_gt({first_activity_id},240), before_hour({first_activity_id},11), not weekday({first_activity_id},4), not weekday({first_activity_id},5), not weekday({first_activity_id},6)",
   f"kettle({first_activity_id}) :- act({first_activity_id}), not duration_gt({first_activity_id},240), before_hour({first_activity_id},12), not before_hour({first_activity_id},10), weekday({first_activity_id},4)",
   f"kettle({first_activity_id}) :- act({first_activity_id}), not duration_gt({first_activity_id},240), not before_hour({first_activity_id},21), weekday({first_activity_id},5), weekday({first_activity_id},6)"]


   for rule in rules:
      splitted_string = rule.split(' :- ')[1].split('), ')
      predicates = predicates + splitted_string
   for predicate in predicates:
      if predicate[-1] != ')':
         predicate = predicate + ')'

      if(predicate[:3] != 'not'):
         predicates_true = predicates_true + [s[:-1] for s in fact_list if predicate in s]
      else:
         contains = False
         for s in fact_list:
            if(predicate[4:] in s):
               contains = True
         if(contains == False):
            predicates_true.append(predicate)

   return json.dumps(predicates_true)


def load_facts(file='facts.json', start="1000-01-01 00:00:00", end="9999-12-31 23:59:59"):
   script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
   rel_path = f"DataBases/Facts/{file}"
   abs_file_path = os.path.join(script_dir, rel_path)

   with open(abs_file_path, 'r') as f:
      facts_list_string = json.load(f)

   facts_string = ' '.join(e for e in facts_list_string)
   facts_string += ' '

   return facts_string, facts_list_string


if __name__ == '__main__':
   app.run()