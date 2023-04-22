import numpy as np

import loadiq as liq
import corrsynt as cs

def Shift2Pos(idata1, qdata1, iqfileheader, recnum, channel, pos):
    global ifplot
    global checkpath
    [f, idata, qdata] = liq.LoadIQ(iqfileheader + '_')

    [corri, corrq, a] = cs.CorrSynt(iqfileheader, idata1, qdata1, 2, 1, channel, pos)

    exts = ['.pdf', '.png']
    cmds = ['-dpdf', '-dpng']

    '''if ifplot && mod(pulsenum,1000)==1
    for i=1:length(exts);
         kp=figure;
        
         plot( idata ,qdata,'r')
        hold on

   plot( Idata1 ,Qdata1,'k')
   hold on
   plot(corrI,corrQ,'g');
   hold on
    plot( idata(1) ,qdata(1),'o')
        
        legend('Resonance scan','Data','Corrected Data','Low frequency')
        xlabel('I adc units');
        ylabel('Q adc units');
        print(kp,cmds{i},[checkpath,'\SyntCorrectionCh',num2str(Channel),'_',num2str(recnum),num2str(pulsenum),exts{i}])
    end
end'''