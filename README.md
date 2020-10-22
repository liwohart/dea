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
python [-1:optional] [primal|dual]_dea.py \path\to\file.csv N M input1 ... inputN output1 ... outputM [0|1:optional]
```

where ``N`` and ``M`` indicate the number of inputs and outputs respectively.
The last argument is a boolean that indicates if the results will be uploaded to a xlsx file or not.
