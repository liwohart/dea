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
python [primal|dual]_dea.py \path\to\file.csv N M input1 ... inputN output1 ... outputM [0|1]
```

The last argument is a boolean that indicates if the results will be uploaded to a xlsx file or not.
