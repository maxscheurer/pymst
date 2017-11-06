import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
plt.style.use('ggplot')


def read_file(fname):
    x = []
    y = []
    with open(fname) as fin:
        dataflag = 0
        # 0: not recording, 1: start of dataset, 2: inside dataset
        for line in fin:
            l = line.strip()
            if "Data Analysis [Thermophoresis With Temperature Jump]" in l:
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

    def onpick(self, event, line):
        print("EVENT!")
        if event.artist!=line: return True

        N = len(event.ind)
        if not N: return True


        # figi = plt.figure()
        for subplotnum, dataind in enumerate(event.ind):
            print(subplotnum, dataind)
        return True

    def __init__(self, fname, protein_conc):
        super(MST_CurveFit, self).__init__()
        self.read_in = read_file(fname)
        self.lig_conc = self.read_in[0] # ligand concentrations (unlabeled substance)
        self.ratios = self.read_in[1] # depletion ratio
        self.protein_conc = protein_conc

    def fluo_func(self, a, kd, fnb, fnab):
        b = self.protein_conc
        rad = np.power(a+b+kd,2) - 4*a*b
        ab = (a+b+kd-np.sqrt(rad))/2
        b_l = b-ab
        return (ab/b)*fnab + (b_l/b)*fnb

    def fit_mst_curve(self, name):
        x_min = 10
        x_max_offset = 1e6
        dx = 100
        x = self.lig_conc
        y = self.ratios
        # run fit
        popt, pcov = curve_fit(self.fluo_func, x, y)
        # prepare plot
        kd = popt[0]
        residuals = y - self.fluo_func(x, *popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r_squared = 1 - (ss_res / ss_tot)
        print(r_squared)

        x_lin = np.arange(x_min, np.max(x) + x_max_offset, dx)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        line, = ax.semilogx(x, y, "o", picker=5)

        ax.semilogx(x_lin, self.fluo_func(x_lin, *popt), "-", label=r"$K_d$ = %.2f nM" % kd)
        # plt.semilogx(x, y, "o")

        plt.legend()
        plt.ylim([870,940])
        fig.canvas.mpl_connect('pick_event', lambda event: self.onpick(event, line))
        plt.savefig(name + ".png")
        # plt.show()

# data = np.loadtxt("am01-38.txt")
# x, y  = data[:,0], data[:,1]
prot_conc = 50 # nM

jobs = [
# ["/Users/Max/Documents/MST/17_10_16/F2DM_Max_IP3.txt", "f2dm_max_ip3"],
# ["/Users/Max/Documents/MST/17_10_16/F2WT_Alina_IP3.txt", "f2wt_alina_ip3"],
# ["/Users/Max/Documents/MST/17_10_16/F2WT_Max_IP3.txt", "f2wt_max_ip3"],
# ["/Users/Max/Documents/MST/17_10_17/F2_WT_Alina_AM01-02_std.txt", "f2wt_al_am01-02"],
# ["/Users/Max/Documents/MST/17_10_17/F2_WT_Alina_AM01-38_std.txt", "f2wt_al_am01-38"],
# ["/Users/Max/Documents/MST/17_10_17/F2_WT_Max_AM01-02_std.txt", "f2wt_max_am01-02"],
# ["/Users/Max/Documents/MST/17_10_17/F2_WT_Max_AM01-38_std.txt", "f2wt_max_am01-38"],
["/Users/Max/Documents/MST/17_10_19/F2DM_Al_AM02-05.txt", "f2dm_am02-05"],
["/Users/Max/Documents/MST/17_10_19/F2WT_Al_AM02-05.txt", "f2wt_am02-05"],
]

for filename, name in jobs:
    mst = MST_CurveFit(filename, prot_conc)
    mst.fit_mst_curve(name)
