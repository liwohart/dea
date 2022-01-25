# About

Scripts to compute the primal and the dual CCR model for Data Envelopment Analysis.

It's a work in progress, here's some issues I plan to work on:
  - [X] Fix flag system<ul><li>[X] Fix **input** and **output** flags</li><li>[X] Specify **dmu** column</li><li>[X] Specify **destination** path</li><li>[X] Fix `destination` flag</li></ul>
  - [X] Add times of execution to runtime log
  - [ ] Implement BCC model

# Installing Dependencies

Install `pip`, then paste this on your command line to install the dependencies

```console
pip install numpy pandas pulp openpyxl odfpy
```

# How to use

Syntax:
```console
python3 (primal|dual)_dea.py /path/to/file.csv [(-d|--dmu) <index>] (-i|--inputs) <input1>[ ...] (-o|--outputs) <output1>[ ...] [(-w|--destination) <dir>]
```

The default values for the `--dmu` and `--destination` flags are `'dmu'` and the same directory as the `.csv` file, respectively.

## Example

Let's say we have the following dataset taken from the book _Data Envelopment Analysis_, written by William W. Cooper, Lawrewnce M. Seiford and Kaoru Tone.

| hospital | doctors | nurses | outpatients | inpatients |
| -------- | -------:| ------:| -----------:| ----------:|
|A         |       20|     151|          100|          90|
|B         |       19|     131|          150|          50|
|C         |       25|     160|          160|          55|
|D         |       27|     168|          180|          72|
|E         |       22|     158|           94|          66|
|F         |       55|     255|          230|          90|
|G         |       33|     235|          220|          88|
|H         |       31|     206|          150|          80|
|I         |       30|     244|          190|         100|
|J         |       50|     268|          250|         100|
|K         |       53|     306|          260|         147|
|L         |       38|     284|          250|         120|

where we have the numbers of doctors and of nurses as **inputs** and the numbers of inpatients and outpatients as **outputs**.


Say it's stored in `example/hospital.csv` and we want to store the results in `results/`. Then, assuming we want to solve it using the dual CCR model, the command would be

```console
python3 dual_dea.py ./example/hospital.csv -d hospital -i doctors nurses -o inpatients outpatients -w ./results/
```
