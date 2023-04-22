import numpy as np
import scipy
import scipy.optimize
from scipy.interpolate import interp1d

import ellipsefit as ef
import loadiq as liq
import comparevector as cv
import correctiq as ciq
import correctiqbackground as ciqb
import findiqcorrection as fiqc
import qcalc

def BackgroundCalibration(iqfileheader, mixer, fmeas):
    global checkpath
    global ifplot
    global nchan
    global adcconv

    #Load the IQ loop data and subtract the offset from the separate offset
    #measurement

    [f, idata, qdata] = liq.LoadIQ(iqfileheader + '_')

    if fmeas > np.min(f):
        print('Correct Frequency range')
    else:
        print('Error')
        return
    
    [f0, i0, q0] = liq.LoadIQ(iqfileheader + 'off_')
    cv.CompareVector(f, f0)
    idata = idata - i0
    qdata = qdata - q0

    #Correct for the mixer imperfection
    [idata, qdata] = ciq.CorrectIQ(idata, qdata, mixer)

    #Same for the wide IQ scan
    #Note that the "strcat" function concatenates its arguments in a unique
    #character array

    [fw, iw, qw] = liq.LoadIQ(iqfileheader + 'w_')
    [f0w, i0w, q0w] = liq.LoadIQ(iqfileheader + 'offw_')
    iw = iw - i0w
    qw = qw - q0w
    [iw, qw] = ciq.CorrectIQ(iw, qw, mixer)

    #Crudely estimate of the resonance frequency, by observing S21 slightly
    #corrected data (we put the origin in the right place, nothing else)

    [rmin, imin] = np.min(np.square(idata) + np.square(qdata))
    f1 = f[imin]

    background = fiqc.FindIQCorrection(fw, iw, qw, [np.min(f), np.max(f)], f1, iqfileheader)

    s21corr = ciqb.CorrectIQBackground(f, (idata + 1j*qdata), background)

    #find the mixer offset at the pulse measurement frequency for use later
    background.I0 = interp1d(f0, i0, fmeas) #(?) I'll leave a question mark here but i'm pretty sure this reproduces the matlab result
    background.Q0 = interp1d(f0, q0, fmeas) #(?) I'll leave a question mark here but i'm pretty sure this reproduces the matlab result

    #the IQ loop should be a circle now, but may be
    #rotated so that it does not point toward the origin.
    #First fit to a circle (actually an ellipse)

    [r1, r2, x0, y0, phi] = ef.EllipseFit(np.real(s21corr), np.imag(s21corr))

    #This is the equation describing the ellipse - just plot this to check
    #that the fit figured out the right parameters.
    #

    def ellipse_param(x):
        return x0 + r1*np.cos(x)*np.cos(phi)-r2*np.sin(x)*np.sin(phi) + 1j*(y0 + r1*np.cos(x)*np.sin(phi) + r2*np.sin(x)*np.cos(phi))
    
    t = np.linspace(0, 2*scipy.pi, 500)

    #now we fit for the rotation and the Q, while constraining the model to stay
    #on the circle from the previous fit

    r = np.mean([r1, r2])

    def mymodel(c, x):
        return x0 + 1j*y0 - r*np.exp(1j*(2*np.arctan(2*(x-f1-c[2]*1e3)*c[1]*1e-6) + c[0]))
    
    def mychi2(c):
        return np.sum(np.square(abs(s21corr - mymodel(c, f))))
    
    a0 = [0, 10, 0]

    #find out if the points are going clockwise or counterclockwise around
    #the center of the circle and adjust the initial guess accordingly -
    #we make the 'Q' parameter initial guess negative if the slope of the
    #phase is negative  

    p = np.polyfit(f-f[0], np.unwrap(np.angle(s21corr - x0 + 1j*y0)), 1)
    a0[1] = np.sign(p[0]) * a0[1]
    a = scipy.optimize.fmin(mychi2, a0)
    #figure
    #plot( f, angle( S21_corr), f, angle( mymodel( a, f)))

    #rotation of loop away from the origin
    #background.loop_rotation = a(1);
    #get this instead from the angle between the off resonance point and
    #the center of the circle

    off_res_point = mymodel(a, 0)   #(take point far away from resoance ie. f = 0Hz)
    background.LoopRotation = np.angle(-off_res_point)

    #overall rotation
    background.OverallRotation = np.angle(off_res_point)

    #keyboard
    s210 = s21corr
    s21corr = np.multiply(s21corr, np.exp(-1j*background.OverallRotation))

    #if ifplot
    #figure(HH)
    #plot(real( S21_corr), imag( S21_corr),'m');
    #hold on
    #plot(real( S21_corr(1)), imag( S21_corr(1)),'--rs',...
    #    'MarkerEdgeColor','y',...
    #    'MarkerFaceColor','r',...
    #    'MarkerSize',2);
    #hold on

    #then rotate aournd (1,0) by the angle by which the IQ loop is tilted
    #note:  following the analysis of Khalil et al, arXiv:1108.3117v3, we
    #also scale the loop by the cos of the rotation angle

    s21corr = 1 - np.cos(background.LoopRotation)*np.multiply(np.exp(-1j*background.LoopRotation), (1 - s21corr))
    
    '''if ifplot
    figure(HH);
    plot(real( S21_corr), imag( S21_corr),'b');
    hold on
    plot(real( S21_corr(1)), imag( S21_corr(1)),'--rs',...
        'MarkerEdgeColor','y',...
        'MarkerFaceColor','r',...
        'MarkerSize',2);
    plot([0,1],[0,0],'--rs',...
        'MarkerEdgeColor','k',...
        'MarkerFaceColor','g',...
        'MarkerSize',2);
    legend('1 Original IQ','1 fstart','2 line correction','2 fstart','3 mixer corr','3 fstart',...
        '4 background corr','4 fstart','5 bg rotation','5 bg start','6 (0,1) rotation','6 fmin')
    xlabel('I');
    ylabel('Q');
    axis([-ADCconv ADCconv -ADCconv ADCconv]);
    '''
    if nchan == 1:
        iqname = iqfileheader[-3:-1]
    else:
        iqname = iqfileheader[-6: -1]
    '''  
    title([IQname, ' Corrections']);
    grid on

    print(HH,'-dpdf',[checkpath,'/ResonanceEvo',IQname,'.pdf']);
    hgsave(HH,[checkpath,'/ResonanceEvo',IQname,]);
    
    end
    '''

    outx = np.real(s21corr)
    outy = np.imag(s21corr)

    resonance = outx + outy
    x0 = [r, 100000, fmeas]

    [qtot, f0, qi, qc] = qcalc.QCalc(f, outx, outy, ifplot, iqname)
    resdata = [qtot, f0, qi, qc]


    '''
    if ifplot
    %     GR=figure;
    %     plot(f,resonance);
    %     hold on
    %     plot(curve2,'r');
    %     title( 'Fit IQ quadrature')
    %     legend('data','fit')
    %     xlabel('Frequency');
    %     ylabel('sqrt(I^2 +Q^2)');
    %  
    %     print(GR,'-dpdf',[checkpath,'/ResonanceFit', iqname, '.pdf'])
    %     
    %     
        if 0
            phase=-angle(S21_corr);
            
            
            fo = fitoptions('Method','NonlinearLeastSquares',...    #(?)
                'Lower',[0,0,curve2.c-curve2.c*0.000001],...
                'Upper',[1,900000000,curve2.c+curve2.c*0.000001],...
                'StartPoint',[curve2.a*1.3,curve2.b,curve2.c]);
            ft = fittype('2*a*b*((x-c)/c)./(1+(2*b*((x-c)/c)).^2)','options',fo);
            coeffnames(ft)
            [curve1]=fit(f,resonance,ft);
            G = @(x,xdata) 2*x(1)*x(2)*((xdata-x(3))/x(3))./(1+(2*x(2)*((xdata-x(3))/x(3))).^2);
            t0 = [curve2.a curve2.b curve2.c];
            
            figure
            
            plot(f,phase);
            hold on
            plot(curve1,'r');
            hold on
            plot(f,G(t0,f),'y');
        end
        
        figure( iqfig)
        plot( S21_corr, 'm')
        title( 'S21 Callibration')
        legend('S21 corr','ellipse','mymodel','Rotated S21')
        xlabel('I normalized units');
        ylabel('Q normalized units');
        
        print(iqfig,'-dpdf',[checkpath,'/',IQname,'.pdf'])
    end
    '''

    return [background, outx, outy, f, resdata]