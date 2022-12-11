# QTLab2223 - Characterization of a Parametric Amplifier and Qubit
Laboratory of Solid State and Quantum Technologies  
Laboratory classe for the Master's degree in Physic at the University of Milano-Bicocca.

##### Table of Contents  
- [How we comunicate with the VNA device](#how-we-comunicate-with-the-VNA-device)  
    - [A brief _operative_ guide on how the VNA works](#a-brief-operative-guide-on-how-the-VNA-works)
    - [The _ManageInstrument_ class](#the-ManageInstrument-class)
        - [Example: extablish a connection with the device and perform a measure](#example-extablish-a-connection-with-the-device-and-perform-a-measure)

## How we comunicate with the VNA device
Here we provide a class **ManageInstrument** that allows sending queries to a VNA device in LAN. By sending queries to the device, we can send instructions to the device and read the displayed data into arrays. 
### A brief _operative_ guide on how the VNA works
The device can work in two modes: "**Continuos** Scan" and "**Single** Scan".
* In **Continuos scan** mode, the instrument makes consecutive scans as time passes. At each scan, it measures an entry of the S matrix (e.g. S21) for a certain number of equally spaced frequencies in the interval displayed on the device screen. Those measurements are stored in the memory of the instrument, where the device mantains _only the last_ "AVE" measurements (where "AVE" is a parameter _of the device_ that we can set). Once it performs a new scan, the oldest measurement in the memory is replaced by the new scan measurement.
* Instead in **Single scan** mode we have to query the instrument each time we want to make a scan; this mode provides a better control of the measurement procedure, so we'll _always_ set the device on this mode.

The value displayed on the screen for each frequency its an **average** of all the measurements stored in the device memory; as a consequence, before performing a measurement, you have to _clear_ the memory of the instrument.
set the value of the _device parameter_ "AVE" and then perform "AVE" scans in order to fill the memory of the instrument. At last we read the values displayed on the screen, which are an average of the measurements performed.
    
**Schematically** when we use the device, we have to follow this procedure:
* Clear the device memory and set the number of measurements the device stores (those are the values whose average will be displayed on the screen);
* Set the displayed frequency interval (any scan is performed only along the interval [fmin,fmax] displayed on the screen);
* Make as many scans as the number of measurements the device stores (we set this parametere before) and **then** read the data displayed on the screen.

The "single_scan(...)" method in the "ManageInstrument" class makes the device follow this procedure.
 
## The _ManageInstrument_ class
With this class you can create an object that allows you to communicate with the instrument.
```bash
ManageInstrument
│  
├── instr              # pyvisa.Resource object that contains a reference to the
|                      # device and allows sending queries with the method instr.query()
├── single_scan()      # A method that sets the desired device parameters, performs
                       # the desired number of scans and returns the values displayed on
                       # the device screen into arrays
```
### Example: extablish a connection with the device and perform a measure 
```python
"""ESTABLISH A CONNECTION WITH THE DEVICE"""
import vna
import matplotlib.pyplot as plt
IP = "<device_address>"
instrument = vna.ManageInstrument(IP)

"""SET THE DESIRED PARAMETER BEFORE PERFORMING THE MEASUREMENTS"""
# Set [fmin,fmax] that is the frequency interval along which the scans are performed
fmin = 1e9
fmax = 3e9
# Set the power of the monotone waves sent into the port 1 to measure the selected matrix element (e.g. S21)
powerdBm = -15 #dBm
# Set the number of equally spaced frequencies in the interval [fmin,fmax] sampled at each scan
npoints = 10
# Set the number of scans performed (that is the number of measurements whose average is returned)
navgs = 2

"""
PERFORM THE MEASURE
We call the single_scan() method with the above parameters.
The method returns:
-freq: an array containing the sampled equally spaced frequencies.
-I and Q: respectively the real and the imaginary part of the matrix element values corresponding to the frequencies in "freq".
"""
freq, I, Q = instrument.single_scan(fmin,fmax,powerdBm,npoints,navgs)
# Here we calculate the matrix element in dB, form its real and imaginary parts
S21 = vna.IQ_to_S21(I,Q)

plt.plot(freq,S21)
plt.show()
```


## Contributors

- MatteoOrlandoni	(mail: [m.orlandoni@campus.unimib.it](m.orlandoni@campus.unimib.it))
- Rocco	Suanno	    (mail: [r.suanno@campus.unimib.it](r.suanno@campus.unimib.it))
- Davide	Villa	    (mail: [d.villa32@campus.unimib.it](d.villa32@campus.unimib.it))

All contributions are expected to be consistent with [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).

