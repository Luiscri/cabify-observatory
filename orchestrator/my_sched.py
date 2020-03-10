import sched, time
import sys
import subprocess

s = sched.scheduler(time.time, time.sleep)

def cron():
    s.enter(24*60*60, 1, cron, []) # Se ejecuta una vez al dia
    command = '{} -m luigi --module tasks MainTask'.format(sys.executable)
    # Use the following command in case you do not use a central scheduler on your docker-compose
    #command = '{} -m luigi --local-scheduler --module tasks Main'.format(sys.executable)
    output = subprocess.check_output(command.split(), shell= False)

s.enter(5, 1, cron, [])
s.run()