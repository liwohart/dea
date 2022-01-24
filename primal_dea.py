from sys import argv
from os import sep, path
from time import time
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

def get_stem_name(fp):
    sep_pos, dot_pos = fp.rindex(sep), fp.rindex('.') if '.' in fp else -1
    name = f'{fp[sep_pos + 1 : dot_pos]}.xlsx' if sep_pos + 1 < dot_pos else None
    stem = fp[: sep_pos]
    return stem, name

def get_inputs(argv):
    if '-i' in argv:
        flag_pos = argv.index('-i')
    elif '--inputs' in argv:
        flag_pos = argv.index('--inputs')
    else:
        raise ValueError("no inputs provided.")
    end = flag_pos + 1
    while end < len(argv) and not argv[end].startswith('-'):
        end += 1
    assert end != flag_pos + 1, "no inputs provided."
    return argv[flag_pos + 1 : end]

def get_outputs(argv):
    if '-o' in argv:
        flag_pos = argv.index('-o')
    elif '--outputs' in argv:
        flag_pos = argv.index('--outputs')
    else:
        raise ValueError("no outputs provided")
    end = flag_pos + 1
    while end < len(argv) and not argv[end].startswith('-'):
        end += 1
    assert end != flag_pos + 1, "no outputs provided."
    return argv[flag_pos + 1 : end]

def get_dmu(argv):
    if '-d' in argv:
        flag_pos = argv.index('-d')
        assert flag_pos + 1 < len(argv) and not argv[flag_pos + 1].startswith('-'), "no 'dmu' column specified."
        dmu = argv[flag_pos + 1]
    elif '--dmu' in argv:
        flag_pos = argv.index('--dmu')
        assert flag_pos + 1 < len(argv) and not argv[flag_pos + 1].startswith('-'), "no 'dmu' column specified."
        dmu = argv[flag_pos + 1]
    else:
        dmu = 'dmu'
    return dmu

def get_destination(argv, stem, name):
    if '-w' in argv:
        flag_pos = argv.index('-w')
        assert flag_pos + 1 < len(argv) and not argv[flag_pos + 1].startswith('-'), "no destination specified."
        destination, _name = get_stem_name(argv[flag_pos + 1])
    elif '--destination' in argv:
        flag_pos = argv.index('--destination')
        assert flag_pos + 1 < len(argv) and not argv[flag_pos + 1].startswith('-'), "no destination specified."
        destination, _name = get_stem_name(argv[flag_pos + 1])
    else:
        destination = stem
    return destination, name if _name is None else _name

def parse_arguments():
    assert len(argv) > 1 and not argv[1].startswith('-'), 'no file path provided'
    file_path = argv[1]
    stem, name = get_stem_name(file_path)
    dmu = get_dmu(argv)
    inputs = get_inputs(argv)
    outputs = get_outputs(argv)
    destination, name = get_destination(argv,stem,name)
    return file_path, name, dmu, inputs, outputs, destination


if __name__ == '__main__':
    print('parsing : ',end='')
    a = time()*1000
    file_path, name, dmu, inputs, outputs, destination = parse_arguments()
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    print('creating dataframe :')
    print(' - initial dataframe ..: ',end='')
    a = time()*1000
    dt = pd.read_csv(file_path).set_index(dmu)
    v = [f'weight_{i}' for i in inputs]
    u = [f'weight_{o}' for o in outputs]
    inputs_v = [f'{i}_x_weight' for i in inputs]
    outputs_u = [f'{o}_x_weight' for o in outputs]
    razao = ['inputs_v','outputs_u']
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    print(' - solving LP problems : ',end='')
    a = time()*1000
    ppl = {dmu:make_ppl(dmu, dt, inputs, outputs, v, u) for dmu in dt.index}
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    print(' - loadind data .......:',end='')
    a = time()*1000
    for comp in v:
        dt[comp] = [ppl[dmu].variablesDict()[comp].varValue for dmu in dt.index]
    for comp in u:
        dt[comp] = [ppl[dmu].variablesDict()[comp].varValue for dmu in dt.index]
    b = time()*1000
    print(f'{b-a:11.6f} ms')

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

    results_path = path.join(destination,name)

    with pd.ExcelWriter(results_path) as writer:
        print(f'loading {results_path} : ',end='')
        a = time()*1000
        results.to_excel(writer,sheet_name='main_results')
        rests.to_excel(writer,sheet_name='env_map')
        b = time()*1000
        print(f'{b-a:11.6f} ms')

