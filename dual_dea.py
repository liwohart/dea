from sys import argv
from os import sep, path
import pandas as pd
import pulp as pl
import numpy as np
from time import time


def make_ppl1(dmu, dt, inputs, outputs, t, l):
    ###FASE I###
    temp_ppl1 = pl.LpProblem(f'{name}_{dmu}_phaseI',pl.LpMinimize)

    temp_t = pl.LpVariable(t)
    temp_l = np.array([pl.LpVariable(comp,lowBound=0) for comp in l])

    temp_ppl1 += temp_t

    for i in inputs:
        temp_ppl1 += temp_t*dt[i][dmu] - np.dot(dt[i],temp_l) >= 0, f'_{i}'

    for o in outputs:
        temp_ppl1 += np.dot(dt[o],temp_l) - dt[o][dmu] >= 0, f'_{o}'

    temp_ppl1.solve(solver=pl.PULP_CBC_CMD(msg=False))

    return temp_ppl1

def make_ppl2(dmu, dt, inputs, outputs, t, l, s):
    temp_ppl1 = make_ppl1(dmu, dt, inputs, outputs, t, l)

    t_star = temp_ppl1.variablesDict()[t].varValue

    temp_ppl2 = pl.LpProblem(f'{name}_{dmu}_phaseII',pl.LpMaximize)

    temp_l = np.array([pl.LpVariable(comp,lowBound=0) for comp in l])
    temp_s = [np.array([pl.LpVariable(comp,lowBound=0) for comp in s[sign]]) for sign in [0,1]]

    temp_ppl2 += temp_s[0].sum() + temp_s[1].sum()

    for i in inputs:
        temp_ppl2 += t_star*dt.loc[dmu][i] - np.dot(dt[i],temp_l) == temp_s[0][inputs.index(i)], f'_{i}'

    for o in outputs:
        temp_ppl2 += np.dot(dt[o],temp_l) - dt.loc[dmu][o] == temp_s[1][outputs.index(o)], f'_{o}'

    temp_ppl2.solve(solver=pl.PULP_CBC_CMD(msg=False))

    return temp_ppl1, temp_ppl2

def get_stem_name(fp):
    sep_pos, dot_pos = fp.rindex(sep), fp.rindex('.') if '.' in fp else -1
    name = f'{fp[sep_pos + 1 : dot_pos]}_dual.xlsx' if sep_pos + 1 < dot_pos else None
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
    print(' - initial dataframe ....: ',end='')
    a = time()*1000
    dt = pd.read_csv(file_path).set_index(dmu)
    t = 'efficiency'
    l = [f'weight_of_{d}' for d in dt.index]
    s = [[f'excess_in_{i}' for i in inputs],
         [f'deficit_in_{o}' for o in outputs]]
    x_hat = [f'optimal_value_of_{i}' for i in inputs]
    y_hat = [f'optimal_value_of_{o}' for o in outputs]
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    print(' - solving LP problems ..: ',end='')
    a = time()*1000
    ppl = {dmu : make_ppl2(dmu, dt, inputs, outputs, t, l, s)
            for dmu in dt.index}
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    print(' - efficiency ...........: ',end='')
    a = time()*1000
    dt[t] = [ppl[dmu][0].variablesDict()[t].varValue
        for dmu in dt.index]
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    print(' - weights ..............: ',end='')
    a = time()*1000
    for comp in l:
        dt[comp] = [ppl[dmu][1].variablesDict()[comp].varValue
            for dmu in dt.index]
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    print(' - excess and deficit ...: ',end='')
    a = time()*1000
    for sign in [0,1]:
        for comp in s[sign]:
            dt[comp] = [ppl[dmu][1].variablesDict()[comp].varValue
                for dmu in dt.index]
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    print(' - optimal input values .: ',end='')
    a = time()*1000
    for i in range(len(inputs)):
        dt[x_hat[i]] = (dt[inputs[i]] * dt[t] - dt[s[0][i]])
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    print(' - optimal output values : ',end='')
    a = time()*1000
    for o in range(len(outputs)):
        dt[y_hat[o]] = (dt[outputs[o]] + dt[s[1][o]])
    b = time()*1000
    print(f'{b-a:11.6f} ms')

    results = dt[inputs + outputs + [t] + s[0] + s[1]]
    optimal = dt[x_hat + y_hat]
    slacks = dt[l]

    results_path = path.join(destination,name)

    with pd.ExcelWriter(results_path) as writer:
        print(f'loading {results_path} : ',end='')
        a = time()*1000
        results.to_excel(writer,sheet_name='main_results')
        optimal.to_excel(writer,sheet_name='optimal_values')
        slacks.to_excel(writer,sheet_name='env_map')
        b = time()*1000
        print(f'{b-a:11.6f} ms')

