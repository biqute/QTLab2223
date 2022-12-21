class Fridge_handler(pyvisa):
    def __init__(self, **kwargs):
        super().__init__("name", 'ASRL1::INSTR' , **kwargs)
        rm = pyvisa.ResourceManager()
        self.inst = rm.open_resource('ASRL1::INSTR')

    def execute(self, mes):
        self.visa_handle.write(mes+'\r')
        sleep(20e-2)
        bytes_in_buffer = self.visa_handle.bytes_in_buffer
        return self.visa_handle.read(str(bytes_in_buffer)+'\r')

    def set_T(self, T):
        n='E'
        if T<=35:
            n+='1'
        elif T<=55:
            n+='2'
        elif T<=140:
            n+='3'
        elif T<=400:
            n+='4'
        else:
            n+='5'

        res = self.execute(n)
        res = self.execute('A2')
        res = self.execute('T'+str(10*T))

    def get_sens(self, sensor = 3):
        res = self.execute('R'+str(sensor))
        res = res.replace("\r", "")
        res = res.replace("\n", "")
        res = res.replace("R", "")
        return int(float(res))

    def send_alert_mail(self):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, email_1, message)
            server.sendmail(sender_email, email_2, message)
            server.sendmail(sender_email, email_3, message)

    def check_press(self):
        res = self.get_sens(14) < 2800 and self.get_sens(15) < 2880
        if(not res):
            print("PRESSIONE ALTA!")
            self.send_alert_mail()
            sleep(60*10)
        return res

    def wait_for_T(self, T, tol=2):
        self.set_T(T)
        check=0
        while check<20 and self.check_press():
            T_now = self.get_T(3)
            os.system('cls')
            print(T_now)
            if T_now not in range(T-tol, T+tol):
                check=0
            else:
                check+=1
            sleep(3)
        print("Fridge is ready!")