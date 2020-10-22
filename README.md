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
python [primal|dual]_dea.py \path\to\file.csv number_of_inputs number_of_outputs input1 ... inputn output1 ... outputm [0|1]
```

The last argument is a boolean that indicates if the results will be uploaded to a xlsx file or not.
