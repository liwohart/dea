from sys import argv
import pandas as pd
import pulp as pl
import numpy as np


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

    temp_ppl1.solve(solver=pl.GLPK(msg=False))

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

    temp_ppl2.solve(solver=pl.GLPK(msg=False))
    
    return temp_ppl1, temp_ppl2

if __name__ == '__main__':
    file_path = argv[1]
    name = file_path[file_path.rindex('\\')+1:file_path.rindex('.')]

    dt = pd.read_csv(file_path,sep=';').set_index('dmu')
    n_inputs, n_outputs = int(argv[2]), int(argv[3])

    inputs = argv[4:4+n_inputs]
    outputs = argv[4+n_inputs:4+n_inputs+n_outputs]
    t = 'eficiencia'
    l = [f'peso_de_{d}' for d in dt.index]
    s = [[f'excesso_em_{i}' for i in inputs],
         [f'deficit_em_{o}' for o in outputs]]
    x_hat = [f'valor_otimo_de_{i}' for i in inputs]
    y_hat = [f'valor_otimo_de_{o}' for o in outputs]

    ppl = {dmu : make_ppl2(dmu, dt, inputs, outputs, t, l, s) for dmu in dt.index}

    ols = [[ppl[dmu][0].variablesDict()[comp].varValue
            for dmu in dt.index]
        for comp in l]

    dt[t] = [ppl[dmu][0].variablesDict()[t].varValue
        for dmu in dt.index]

    for comp in l:
        dt[comp] = [ppl[dmu][1].variablesDict()[comp].varValue
            for dmu in dt.index]

    for sign in [0,1]:
        for comp in s[sign]:
            dt[comp] = [ppl[dmu][1].variablesDict()[comp].varValue
                for dmu in dt.index]

    for i in range(len(inputs)):
        dt[x_hat[i]] = (dt[inputs[i]]*dt[t]-dt[s[0][i]])

    for o in range(len(outputs)):
        dt[y_hat[o]] = (dt[outputs[o]]+dt[s[1][o]])

    results = dt[inputs + outputs + [t] + s[0] + s[1]]
    optimal = dt[x_hat+y_hat]
    slacks = dt[l]

    if argv[-1].isnumeric() and not bool(int(argv[-1])):
        with pd.ExcelWriter(f'results\\{name}_dual.xlsx') as writer:
            results.to_excel(writer,sheet_name='main_results')
            optimal.to_excel(writer,sheet_name='optimal_values')
            slacks.to_excel(writer,sheet_name='env_map')

    print(results)
    print(optimal)
    print(slacks)

