from sys import argv
from os import sep, path
import pandas as pd
import pulp as pl
import numpy as np

def make_ppl(dmu, dt, inputs, outputs, v, u):

    temp_v = [pl.LpVariable(comp,
            lowBound=0)
        for comp in v]

    temp_u = [pl.LpVariable(comp,
            lowBound=0)
        for comp in u]

    temp_ppl = pl.LpProblem(
        f'{name}_{dmu}',pl.LpMaximize)

    temp_ppl += np.dot(dt[outputs].loc[dmu],temp_u)

    temp_ppl += np.dot(dt[inputs].loc[dmu],temp_v) == 1, '_Normal'
    for i in dt.index:
        temp_ppl += np.dot(dt[outputs].loc[i],temp_u) - np.dot(dt[inputs].loc[i],temp_v) <= 0, f'_{i}'

    temp_ppl.solve(solver=pl.PULP_CBC_CMD(msg=False))

    return temp_ppl

def get_inputs(argv):
    assert '-i' in argv or '--inputs' in argv, "no inputs provided."
    try:
        flag_pos = argv.index('-i')
    except:
        flag_pos = argv.index('--inputs')
    end = flag_pos + 1
    while end < len(argv) and not argv[end].startswith('-'):
        end += 1
    assert end != flag_pos + 1, "no inputs provided."
    return argv[flag_pos + 1 : end]


def get_outputs(argv):
    assert '-o' in argv or '--outputs' in argv, "no outputs provided."
    try:
        flag_pos = argv.index('-o')
    except:
        flag_pos = argv.index('--outputs')
    end = flag_pos + 1
    while end < len(argv) and not argv[end].startswith('-'):
        end += 1
    assert end != flag_pos + 1, "no outputs provided."
    return argv[flag_pos + 1 : end]

def get_dmu(argv):
    if '-d' in argv or '--dmu' in argv:
        try:
            flag_pos = argv.index('-d')
        except:
            flag_pos = argv.index('--dmu')
        assert flag_pos + 1 < len(argv) and not argv[flag_pos + 1].startswith('-'), "no `dmu` specified."
        dmu = argv[flag_pos + 1]
    else:
        dmu = 'dmu'
    return dmu

def get_destination(argv, stem):
    if '-w' in argv or '--destination' in argv:
        try:
            flag_pos = argv.index('-w')
        except:
            flag_pos = argv.index('--destination')
        assert flag_pos + 1 < len(argv) and not argv[flag_pos + 1].startswith('-'), "no destination specified."
        destination = argv[flag_pos + 1]
    else:
        destination = stem
    return destination

def parse_arguments():
    assert len(argv) > 1 and not argv[1].startswith('-'), 'no file path provided'
    file_path = argv[1]
    name = file_path[file_path.rindex(sep) + 1 : file_path.rindex('.')]
    stem = file_path[: file_path.rindex(sep)]
    dmu = get_dmu(argv)
    inputs = get_inputs(argv)
    outputs = get_outputs(argv)
    destination = get_destination(argv,stem)
    return file_path, name, dmu, inputs, outputs, destination


if __name__ == '__main__':
    file_path, name, dmu, inputs, outputs, destination = parse_arguments()

    print('creating dataframe...')
    dt = pd.read_csv(file_path).set_index(dmu)
    v = [f'weight_{i}' for i in inputs]
    u = [f'weight_{o}' for o in outputs]

    inputs_v = [f'{i}_x_weight' for i in inputs]
    outputs_u = [f'{o}_x_weight' for o in outputs]

    razao = ['inputs_v','outputs_u']

    print(' - solving LP problems...')
    ppl = {dmu:make_ppl(dmu, dt, inputs, outputs, v, u) for dmu in dt.index}

    print(' - loadind data...')
    for comp in v:
        dt[comp] = [ppl[dmu].variablesDict()[comp].varValue for dmu in dt.index]
    for comp in u:
        dt[comp] = [ppl[dmu].variablesDict()[comp].varValue for dmu in dt.index]

    for iv,i,_v in zip(inputs_v,inputs,v):
        dt[iv] = dt[i]*dt[_v]
    for pu,p,_u in zip(outputs_u,outputs,u):
        dt[pu] = dt[p]*dt[_u]

    dt['inputs_v'] = sum(dt[iv] for iv in inputs_v)
    dt['outputs_u'] = sum(dt[pu] for pu in outputs_u)

    dt = dt.round(6)

    rests = pd.DataFrame([[pl.value(ppl[hos1].constraints[f'_{hos2}'])
            for hos2 in dt.index]
            for hos1 in dt.index],
        index=dt.index,
        columns=dt.index.to_list()).round(6)

    results = dt[inputs+outputs+v+u+razao]

    results_path = path.join(destination,f'{name}.xlsx')

    with pd.ExcelWriter(results_path) as writer:
        print(f'loading {results_path}...')
        results.to_excel(writer,sheet_name='main_results')
        rests.to_excel(writer,sheet_name='env_map')

