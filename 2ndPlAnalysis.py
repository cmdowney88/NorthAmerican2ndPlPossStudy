import sys
import pandas as pd
import subprocess
import os

data_file = sys.argv[1]

# CONSTANTS ------------------------------------------------------------------------------------------------------------

the_west = ('the_west', ['Hawaii', 'Alaska', 'Washington', 'Oregon', 'California', 'Idaho', 'Nevada', 'Utah', 'Arizona', 'Montana', 'Wyoming', 'Colorado', 'New_Mexico'])

the_south = ('the_south', ['Texas', 'Arkansas', 'Louisiana', 'Alabama', 'Mississippi', 'Tennessee', 'Kentucky', 'Georgia', 'South_Carolina', 'North_Carolina', 'Virginia'])

the_north = ('the_north', ['North_Dakota', 'South_Dakota', 'Minnesota', 'Wisconsin', 'Illinois', 'Michigan'])

the_midland = ('the_midland', ['Nebraska', 'Kansas', 'Oklahoma', 'Missouri', 'Iowa', 'Indiana', 'Ohio', 'West_Virginia'])

the_east = ('the_east', ['Maryland', 'Delaware', 'Pennsylvania', 'New_Jersey', 'New_York', 'Rhode_Island', 'Connecticut', 'Massachusetts', 'New_Hampshire', 'Vermont', 'Maine'])

canada = ('canada', ['Ontario', 'Nova_Scotia', 'British_Columbia', 'Manitoba'])

florida = ('florida', ['Florida'])

region_list = [the_west, the_south, the_north, the_midland, the_east, canada, florida]

regions = {}

for entry in region_list:
    for state in entry[1]:
        regions[state] = entry[0]

imgkitoptions = {"format": "png"}

# ----------------------------------------------------------------------------------------------------------------------

data = pd.read_csv(data_file)

active_states = {}
for state in data['state']:
    if state not in active_states:
        active_states[state] = 1
    else:
        active_states[state] += 1

base_columns = ['state', 'count', 'region']
ex_1_columns = base_columns + [header + '_top' for header in data.columns.values if header[-4:] == '_nom'] + [header + '_bottom' for header in data.columns.values if header[-4:] == '_nom']
ex_2_columns = base_columns + [header + '_top' for header in data.columns.values if header[-5:] == '_poss'] + [header + '_bottom' for header in data.columns.values if header[-5:] == '_poss']
ex_3_columns = base_columns + [header + '_top' for header in data.columns.values if header[-5:] == '_emph'] + [header + '_bottom' for header in data.columns.values if header[-5:] == '_emph']

experiment_columns = [ex_1_columns, ex_2_columns, ex_3_columns]
experiment_files = ['experiment_1.csv', 'experiment_2.csv', 'experiment_3.csv']
experiment_suffixes = ['_nom', '_poss', '_emph']

for i, experiment in enumerate(experiment_files):
    file = open(experiment, 'w')
    header = ','.join(experiment_columns[i])
    ex_stem = experiment[:-4]

    print(header, file=file)

    for state in sorted(active_states.keys()):
        print(state + ',' + str(active_states[state]) + ',' + regions[state], file=file)

    file.close()

    ex = pd.read_csv(experiment).fillna(0).set_index('state')

    ex.to_csv(ex_stem + '.csv')

    for index, row in data.iterrows():
        for variable in [x for x in data.columns.values if x[-4:] == experiment_suffixes[i] or x[-5:] == experiment_suffixes[i]]:
            if row[variable] < 3:
                ex.at[row['state'], variable + '_top'] += 1
            if row[variable] == 3 and i == 0:
                ex.at[row['state'], variable + '_bottom'] += 1
            if row[variable] == 5 and i > 0:
                ex.at[row['state'], variable + '_bottom'] += 1

    ex.to_csv(ex_stem + '.csv')
    ex.to_html(ex_stem + '.html')
    subprocess.call(
        'wkhtmltoimage -f png --width 0 ' + ex_stem + '.html ' + ex_stem +'.png', shell=True)

    ex_agg = ex.groupby('region').sum()

    for index, row in ex_agg.iterrows():
        for column in ex_agg.columns.values[1:]:
            ex_agg.at[index, column] = round(ex_agg.at[index, column] / ex_agg.at[index, 'count'], 3)

    ex_agg.to_csv(ex_stem + '_agg' + '.csv')
    ex_agg.to_html(ex_stem + '_agg.html')
    subprocess.call(
        'wkhtmltoimage -f png --width 0 ' + ex_stem + '_agg.html ' + ex_stem + '_agg.png', shell=True)

cwd = os.getcwd()

cwd_list = os.listdir(cwd)

for item in cwd_list:
    if item.endswith(".html"):
        os.remove(os.path.join(cwd, item))
