import PySimpleGUI as psg

import paramiko
import time
from datetime import datetime
import glob
import os
import numpy as np
import matplotlib.pyplot as plt

# Test SSH Connection
def test_connection(ip_address):

    #
    ssh_server = str(ip_address)
    ssh_user_pass = "bevo"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ssh_server, username=ssh_user_pass, password=ssh_user_pass)
        ssh.exec_command("ls")
        return "Server Available!"
    except:
        return "Error: Server Not Available :("

# Record Raspberry Pi Data via SSH, save csv file to local directory
def record_data(ip_address):
    ssh_server = str(ip_address)
    ssh_user_pass = "bevo"

    # create ssh client
    # home wifi network raspberry pi IP: 192.168.1.158
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ssh_server, username=ssh_user_pass, password=ssh_user_pass)
    channel = ssh.invoke_shell()

    # execute commands
    cmds = ['cd Desktop/geo-project/\n', "ls\n", "source .venv/bin/activate\n", "python3 geo.py\n"]

    # using time.sleep to avoid errors
    channel.send(cmds[0])
    time.sleep(.1)
    channel.send(cmds[1])
    time.sleep(.1)
    channel.send(cmds[2])
    time.sleep(.1)
    channel.send(cmds[3])
    time.sleep(6)

    # download the CSV file that gets created to our computer directory
    # name it using year-mm-dd, hour-min-sec
    folder = "geophone_data/"
    geo_filename = str(datetime.today().strftime('%Y-%m-%d_%H-%M-%S_')) + "data.csv"
    save_filename = folder + geo_filename
    with ssh.open_sftp() as sftp: \
        sftp.get("/home/bevo/Desktop/geo-project/test.csv", save_filename)

    return geo_filename

# Plot geophone data
def plot_geophone_data():
    list_of_files = glob.glob('geophone_data/*.csv')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)

    plt.figure(figsize = (5,4))
    data = np.genfromtxt(latest_file, delimiter=',',names=['t', 'v'])
    plt.plot(data['t'], data['v'])
    plt.title(latest_file)
    plt.xlabel("time (ms)")
    plt.ylabel("voltage (v)", labelpad=0)
    plt.show(block=False)

# configure GUI
def create_gui():
    # psg settings
    psg.theme("Purple")
    psg.set_options(font=('Arial Bold', 12))


    # general layout
    gui_label = psg.Text(text='Soil Bearing Capacity GUI',font=('Arial Bold', 20), size=20,expand_x=True,justification='center')


    # pi configuration
    pi_label = psg.Text("Raspberry Pi", font = ('Arial Bold', 16))
    ip_prompt = psg.Text(text='Enter Raspberry Pi IP Address:', expand_x=True)
    ip_input = psg.Input(key = 'pi_ip_address', justification='left')
    test_pi_connection = psg.Button('Test Pi Connection')

    pi_connection = psg.Text(text = 'Pi Connection Status:')
    connection_status = psg.Text(text = '', text_color = 'grey')


    # geophone 1
    geo_label = psg.Text(text='Geophone #1', font = ('Arial Bold', 16))
    geo_record_data = psg.Button("Record Geophone Data (5s Test)", button_color = 'pale green')
    geo_graph_data = psg.Button("View Geophone Data Plot", button_color = 'light blue')
    geo_test_status = psg.Text('Test Status: Not Available', text_color = 'grey')

    # vibration source
    vibration_title = psg.Text(text='Vibration Source Toggle', font=('Arial Bold', 16))
    vibration_off = psg.Radio('Off', "vibration_source", default=True)
    vibration_on = psg.Radio('On', "vibration_source")

    # electro-magent config
    # mag_title = psg.Text(text='Electromagnet Toggle', font = ('Arial Bold', 16))
    # mag_off = psg.Radio('Off', "electromag", default=True)
    # mag_on = psg.Radio('On', "electromag")

    # just for fun
    longhorn = psg.Image('longhorn.png')

    # misc
    exit_label = psg.Text(text = 'Exit GUI', font = ('Arial Bold', 16))
    exit_button = psg.Exit(button_color = 'red')


    layout = [
            [gui_label],
            [psg.Column([[longhorn]], justification='center')],
            [pi_label],
            [ip_prompt, ip_input],
            [test_pi_connection],
            [pi_connection, connection_status],
            [psg.Text('', size = (1,1))], # blank line
            [geo_label],
            [geo_record_data],
            [geo_test_status],
            [geo_graph_data],
            [psg.Text('', size=(1, 1))], # blank line
            [vibration_title],
            [vibration_off],[vibration_on],
            [psg.Text('', size=(1, 1))], # blank line
            [exit_label],
            [exit_button],
            ]
    window = psg.Window('SBC GUI', layout)

    # event handling
    while True:
        event, values = window.read()
        print(event, values)
        if event in (None, 'Exit'):
            break
        # Test Pi Connection
        elif event == test_pi_connection.get_text():
            pi_status = test_connection(values['pi_ip_address'])
            connection_status.update(pi_status)
            if pi_status == 'Server Available!':
                connection_status.update(text_color = 'green')
            else:
                connection_status.update(text_color = 'dark red')

        # Record Geo Data
        elif event == geo_record_data.get_text():
            geo_test_status.update('Executing Test...', text_color = 'yellow')
            window.refresh()
            file_name = record_data(values['pi_ip_address'])
            time.sleep(5)
            status_string = 'Test Complete! Data Stored in ' + str(file_name)
            geo_test_status.update(status_string, text_color = 'green')

        # Plot Data
        elif event == geo_graph_data.get_text():
            plot_geophone_data()

        # Electromagnet Status
    window.close()

create_gui()