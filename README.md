# DEA

Scripts to compute the primal and the dual CCR model for Data Envelopment Analysis.

# Installing

Paste this on your command line to install the dependencies

```
pip install numpy pandas pulp openpyxl
```

# How to use

Syntax:

```
python [primal|dual]_dea.py \path\to\file.csv N M input1 ... inputN output1 ... outputM [0|1:optional]
```

where ``N`` and ``M`` indicate the number of inputs and outputs respectively.
The last argument is a boolean that indicates if the results will be uploaded to a xlsx file or not.

# Example

Let's say we have the following dataset


| dmu |medicos|enfermeiros|internados|ambulatoriais|
| --- | -----:| ---------:| --------:| -----------:|
|A    |     20|        151|       100|           90|
|B    |     19|        131|       150|           50|
|C    |     25|        160|       160|           55|
|D    |     27|        168|       180|           72|
|E    |     22|        158|        94|           66|
|F    |     55|        255|       230|           90|
|G    |     33|        235|       220|           88|
|H    |     31|        206|       150|           80|
|I    |     30|        244|       190|          100|
|J    |     50|        268|       250|          100|
|K    |     53|        306|       260|          147|
|L    |     38|        284|       250|          120|
