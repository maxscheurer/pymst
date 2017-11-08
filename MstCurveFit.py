import numpy as np
from scipy.optimize import curve_fit

def read_file(fname):
    x = []
    y = []
    with open(fname) as fin:
        dataflag = 0
        # 0: not recording, 1: start of dataset, 2: inside dataset
        for line in fin:
            l = line.strip()
            if "Data Analysis " in l:
                dataflag = 1
                continue
            if dataflag:
                if l == "":
                    continue
                elif "Average and Error Bars" in l:
                    dataflag = 0
                    break
                else:
                    # print(l.split("\t"))
                    xl, yl = l.split("\t")
                    x.append(xl)
                    y.append(yl)
    return [np.array(x, dtype=float), np.array(y, dtype=float)]


class MST_CurveFit(object):
    """docstring for MST_CurveFit."""

    def __init__(self, fname, protein_conc):
        super(MST_CurveFit, self).__init__()
        self.read_in = read_file(fname)
        self.lig_conc_orig = self.read_in[0] # ligand concentrations (unlabeled substance)
        self.ratios_orig = self.read_in[1] # depletion ratio
        self.lig_conc = self.read_in[0] # ligand concentrations (unlabeled substance)
        self.ratios = self.read_in[1] # depletion ratio
        print(self.lig_conc)
        print(self.ratios)
        self.protein_conc = float(protein_conc)

    def fluo_func(self, a, kd, fnb, fnab):
        b = self.protein_conc
        rad = np.power(a+b+kd,2) - 4*a*b
        ab = (a+b+kd-np.sqrt(rad))/2
        b_l = b-ab
        return (ab/b)*fnab + (b_l/b)*fnb

    def fit_mst_curve(self):
        x_min = 10
        x_max_offset = 1e6
        dx = 100
        x = self.lig_conc
        y = self.ratios
        # run fit
        self.popt, self.pcov = curve_fit(self.fluo_func, x, y)
        # prepare plot
        self.kd = self.popt[0]
        residuals = y - self.fluo_func(x, *self.popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        self.r_squared = 1 - (ss_res / ss_tot)
        # print(self.r_squared)

        self.x_lin = np.arange(x_min, np.max(x) + x_max_offset, dx)
