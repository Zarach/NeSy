import json
import os

import pandas as pd
import Utils

action_sequences = Utils.load_csv_from_folder('Barthi/ActionSeq')
action_sequences = action_sequences.replace(['coffee machine'],'coffee')
action_sequences = action_sequences.replace(['floor lamp'],'lamp')
action_sequences = action_sequences.replace(['washing machine'],'washing_machine')
facts = []
activity_id = 0

for index, action in action_sequences.iterrows():
        print( str(action['name']) + " " + str(action['start_time']) + " - " + str(action['end_time']))

        activity_predicate_string = f"{action['name']}({activity_id})."
        facts.append(activity_predicate_string)

        start_date_predicate_string = f"start({activity_id}, \'{action['start_time']}\')."

        facts.append(start_date_predicate_string)

        end_date_predicate_string = f"end({activity_id}, \'{action['end_time']}\')."

        facts.append(end_date_predicate_string)

        activity_id += 1

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "DataBases/facts_ground_truth_hh14.json"
abs_file_path = os.path.join(script_dir, rel_path)

with open(abs_file_path, 'w') as facts_file:
    json_string = json.dumps(facts, ensure_ascii=False, indent=4)
    facts_file.write(json_string)


print('done')