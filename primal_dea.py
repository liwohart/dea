from sys import argv
import os
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

    temp_ppl.solve()

    return temp_ppl

if __name__ == '__main__':
    file_path = argv[1]
    name = file_path[file_path.rindex(os.sep)+1:file_path.rindex('.')]

    dt = pd.read_csv(file_path,sep=';').set_index('dmu')
    n_inputs, n_outputs = int(argv[2]), int(argv[3])

    inputs = argv[4:4+n_inputs]
    outputs = argv[4+n_inputs:4+n_inputs+n_outputs]

    v = [f'peso_{i}' for i in inputs]
    u = [f'peso_{o}' for o in outputs]

    inputs_v = [f'{i}_x_peso' for i in inputs]
    outputs_u = [f'{o}_x_peso' for o in outputs]

    razao = ['inputs_v','outputs_u']

    ppl = {dmu:make_ppl(dmu, dt, inputs, outputs, v, u) for dmu in dt.index}

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

    if argv[-1].isnumeric() and bool(int(argv[-1])):
        results_path = os.path.join('results',f'{name}.xlsx')

        with pd.ExcelWriter(results_path) as writer:
            print(f'loading {results_path}...')
            results.to_excel(writer,sheet_name='main_results')
            rests.to_excel(writer,sheet_name='env_map')

    print(results)
    print(rests)

