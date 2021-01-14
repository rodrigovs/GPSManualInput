import sys
import glob
import serial
import time


import threading


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


def exec_coordenadas(ser_obj):
    print('Inicializando')
    time.sleep(10)
    print('enviando set manual mode')
    ser_obj.write(b'SET_GPS_MANUAL_MODE\n')
    time.sleep(10)
    lines = tuple(open('coordenadas.txt', 'r'))
    for line in lines:
        ser_obj.write(b'GPS\n')
        print('enviando: ' + line)
        ser_obj.write(bytes(line,'ascii'))
        time.sleep(10)
    
    

def read_serial_line(ser_obj):
    print(ser_obj.readline())
    
    
 



    
    




#app = QApplication(sys.argv)
#gallery = WidgetGallery()
#gallery.show()
#sys.exit(app.exec_())


    
lista_available_coms = serial_ports()
filename = 'coordenadas.txt'
device_serial_port = "COM3"
device_baudrate = 115200

if(not(device_serial_port in lista_available_coms)):
    print(device_serial_port + ' nao exibida na lista, tente outro nome')
    print(lista_available_coms)
    sys.exit()



serial_connection = serial.Serial(port=device_serial_port, baudrate=device_baudrate)

thread_input_data = threading.Thread(target=exec_coordenadas, args=(serial_connection,))
thread_input_data.start()


try:
    while True:
        #print(serial_connection.readline())
        read_serial_line(serial_connection)
        # if(clear_output):
        #     output = ''
        # output += serial_connection.read_all()
        # #linhas = output.split('\n')
        # clear_output = True
        # if(len(output) > 0):
        #     print(output)
            
except KeyboardInterrupt:
    serial_connection.close()
    print("Conexao encerrada")


# coordenadas_txt = open('coordenadas.txt')

# a.readline()
# a.close()
# #while(1):
# #    ser.available
# #    ser.readall()
    
# 


# import view
# app = view.QApplication(sys.argv)
# gallery = view.WidgetGallery()
# gallery.show()
# sys.exit(app.exec_())


# from PIL import Image

# image = Image.open('imagem_teste.png')

# image


# from io import StringIO
# from PIL import Image
# import urllib

# url = "http://maps.googleapis.com/maps/api/staticmap?center=-30.027489,-51.229248&size=800x800&zoom=14&sensor=false"
# buffer = StringIO(urllib.urlopen(url).read())
# image = Image.open(buffer)
