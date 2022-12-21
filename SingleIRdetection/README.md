# QTLab2223 - Single IR photon detection
Laboratory of Solid State and Quantum Technologies  
Laboratory classe for the Master's degree in Physic at the University of Milano-Bicocca.  

## Communication with the thermometer
In order to communicate with the thermometer we created the class "Fridge_handler"

```python
class Fridge_handler(pyvisa):
    def __init__(self, **kwargs):
        super().__init__()
        rm = self.ResourceManager()
        inst = rm.open_resource('ASRL1::INSTR')
```     
The first thing we defined after that is the simple method **Execute**.
```python
def Execute(self, cmd):
        self.write('$'+ str(cmd))
```
The reason for that is because the instrument, if we simply use the command **write(cmd)**, does not only excute the operation but also stores a trace of the command in its buffer, filling it with wrongful and useless information. As a solution **Execute** authomatically adds the character *$* before the command, wich instructs the thermometer not to write anything in the buffer. The other various methods of this class allow us to retrieve data from the instrument and change its configuration. For example, the method ScanT retrieves information about the temperature of the Mixing Chamber of the Cryostat.

```python
def ScanT(self, cmd, interval, time):           # cmd -> command that specifies which temperature,
                                                # interval -> time step to perform control
                                                # time -> total time of the scansion
        '''Temperature scansion that prints the values every "interval" seconds for a "time" time'''
        N = int(time/interval)
        Temps = np.zeros(N)
        for i in range(N):
            out = self.query_ascii_values(cmd, converter='s')
            out = str.rstrip(out[0])
            time.sleep(interval)
            out = (out.split('+'))[1]           # split the string where '+' is and gives back only the second part (1)
            Temps[i] = float(out)
            print('Temperature at step ' + i + ' is ' + out)
        return Temps
```

## Contributors
- Alessandro	Angeloni (mail: [a.angeloni3@campus.unimib.it](a.angeloni3@campus.unimib.it))
- Marcello	Faggionato (mail: [m.faggionato1@campus.unimib.it](m.faggionato1@campus.unimib.it))
- Leonardo	Mariani 	 (mail: [l.mariani48@campus.unimib.it](l.mariani48@campus.unimib.it))

All contributions are expected to be consistent with [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/).
