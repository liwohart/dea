# About

Scripts to compute the primal and the dual CCR model for Data Envelopment Analysis.

It's a work in progress, here's some issues to be solved in the future:
  - [X] Specify **dmu** column
  - [X] Fix flag system
  - [ ] Save to `.ods`
  - [ ] Choose solver

# Installing Dependencies

Install `pip`, then paste this on your command line to install the dependencies

```console
pip install numpy pandas pulp openpyxl
```

# How to use

Syntax:
```console
python3 (primal|dual)_dea.py /path/to/file.csv [[-d|--dmu] <index>] (-i|--inputs) <input1> [...] (-o|--outputs) <output1> [...] [0|1]
```

If `<index>` id not provided, then `dmu` defaults to `"dmu"`.

## Example

Let's say we have the following dataset taken from the book _Data Envelopment Analysis_, written by William W. Cooper, Lawrewnce M. Seiford and Kaoru Tone.

| dmu | doctors | nurses | outpatients | inpatients |
| --- | -------:| ------:| -----------:| ----------:|
|A    |       20|     151|          100|          90|
|B    |       19|     131|          150|          50|
|C    |       25|     160|          160|          55|
|D    |       27|     168|          180|          72|
|E    |       22|     158|           94|          66|
|F    |       55|     255|          230|          90|
|G    |       33|     235|          220|          88|
|H    |       31|     206|          150|          80|
|I    |       30|     244|          190|         100|
|J    |       50|     268|          250|         100|
|K    |       53|     306|          260|         147|
|L    |       38|     284|          250|         120|

where we have the numbers of doctors and of nurses as **inputs** and the numbers of inpatients and of outpatients as **outputs**.


Say it's stored in `data/hospital.csv`. Then, assuming we want to solve it using the primal CCR model, the command would be

```console
python3 primal_dea.py data/hospital.csv -i doctors nurses -o inpatients outpatients
```
