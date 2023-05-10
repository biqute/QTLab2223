import numpy as np
import globvar

from loadiq import LoadIQ
from corrsynt import CorrSynt
from matplotlib import pyplot as plt

def Shift2Pos(idata1, qdata1, iqfileheader, recnum, pulsenum, channel, pos, ifplot):
    
    checkpath = globvar.checkpath
    [f, idata, qdata] = LoadIQ(iqfileheader + '_')

    [corri, corrq, a] = CorrSynt(iqfileheader, idata1, qdata1, 2, 1, channel, pos)

    exts = ['.pdf', '.png']
    cmds = ['-dpdf', '-dpng']

    if (ifplot == 1 and pulsenum % 1000 == 1):
        for i in range(len(exts)):
            plt.plot(idata, qdata,'r')
            plt.plot(idata1, corrq, 'k')
            plt.plot(corri, corrq, 'g')
            plt.plot(idata[0], qdata[0], 'o')
            
            plt.xlabel('I adc units')
            plt.ylabel('Q adc units')
            plt.legend('Resonance scan','Data','Corrected Data','Low frequency')
            plt.savefig(checkpath + '\\SyntCorrectionCh' + str(channel) + '_' + str(recnum) + str(pulsenum) + exts[i])