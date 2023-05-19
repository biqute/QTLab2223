import numpy as np

import globvar

def FindIQCorrection(fw, iw, qw, xwin, f1, iqfileheader, ifplot):

    class Background:
        PAmp = 0
        PPhase = 0
        Df = 0
        FRef = 0
        I0 = 0
        Q0 = 0
        LoopRotation = 0
        OverallRotation = 0

    checkpath = globvar.checkpath
    nchan = globvar.nchan

    #Fit a wide range IQ scan for the purpose of removing background variations
    #of the microwave transmission
    #
    #How to:  [p_amp, p_phase, Df] = find_iq_correction( fw, iw, qw, xwin, f1)

    #Inputs:

    #   fw -        IQ scan frequency data
    #   iw -        I data
    #   qw -        Q data
    #   xwin -      two element vector of frequencies to exclude from the fit
    #               (because this is where the resonance is)
    #   f1 -        an arbitrary frequency offset - make this approximately the
    #               resonance frequency
    #Outputs:

    #   background  a structure containing the background fit info
    #       .p_amp -     polynomial fit to the magnitude
    #       .p_phase -   polynomial fit to the phase
    #       .Df -        total frequency scan used for scaling

    #measure frequency relative to f1
    fw = fw - f1
    xwin = xwin - f1
    xwinfact = 1
    xwin = np.multiply(xwin, xwinfact)
    bgpoldeg = 5

    #for fitting the background, take points outside the range of the narrow
    #range measurement
    ii = fw < xwin[0] or fw > xwin[1]
    df = fw[-1] - fw[0]

    #model for the background:  quadratic amplitude variation with frequency
    c = 3e8 #speed of light
    #mymodel = @(a, df) (a(1) + a(2)*df/Df + (a(3)*df/Df).^2) .* exp( -2i*pi * df * a(4) / c + a(5));

    #mychi2 = @(a) sum( abs( mymodel( a, fw(ii)) - complex( iw(ii), qw(ii))).^2);
    #mychi2 = @(a) sum( abs( real(mymodel( a, fw(ii))) - iw(ii)).^2) + ...
    #    sum( abs( imag(mymodel( a, fw(ii))) - qw(ii)).^2);
    #some initial guesses for the fit parameters
    #c1 = norm( [iw(1) qw(1)]);
    #c2 = 0;
    #c3 = 0;
    #c4 = 6;    #this is the electrical length of the cryostat cabling
    #c5 = 0;
    #c0 = [ c1 c2 c3 c4 c5];
    #a = fminsearch( mychi2, c0)


    #first determine the amplitude variation of the background with frequency
    
    p_amp = np.polyfit(fw[ii]/df, abs(iw[ii] + 1j*qw[ii]), bgpoldeg) #(?)Maybe polyfit gives different results?

    ref = [np.mean(abs(iw + 1j*qw)), np.mean(abs(iw +1j*qw))]

    #Now determine the phase variation with frequency

    p_phase = np.polyfit(fw[ii]/df, np.unwrap(np.angle(iw[ii], qw[ii])), 1)
  
    #mymodel = @(a, df) polyval(p, df/Df) .* exp( 2i*pi * df * a(1) / c + 1i*a(2));
    #mychi2 = @(a) sum( abs( mymodel( a, fw(ii)) - complex( iw(ii), qw(ii))).^2);
    #c0 = [10 0];
    #a = fminsearch( mychi2, c0)


    def mymodel(a, b, ddf):
        return np.multiply(np.polyval(a, ddf/df), np.exp(1j*np.polyval(b, ddf/df)))

    background = Background()
    background.PAmp = p_amp
    background.PPhase = p_phase
    background.Df = df
    background.FRef = f1

    return background