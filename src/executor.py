#!/usr/bin/python3

####################################################################################
#
#  Copyright (c) 2023 Piotr Jochymek
#
#  MIT License
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
####################################################################################

from subprocess import Popen, STDOUT, PIPE
from threading import Thread
from time import time
from time import sleep
from psutil import Process
from signal import SIGTERM

class Executor :
    def __init__(self):
        self.command_list_to_execute = None
        self.output=''
        self.keep_running = True

        self.run_thread=Thread(target=self.run_in_thread,daemon=True)
        self.run_thread.start()

    def run(self,command_list_to_execute,timeout=None):
        #print('run',command_list_to_execute,timeout)

        self.output = ''
        self.pid = None

        self.running = True
        self.res_ok = True
        self.killed = False
        start = time()

        self.command_list_to_execute = command_list_to_execute
        error_message = ''

        while self.running:
            if timeout:
                if time()-start>timeout:
                    self.kill(self.pid)
                    if not self.killed:
                        error_message += '\nKilled after timeout.'
                        self.killed = True

            sleep(0.001)

        return self.res_ok and not self.killed,(self.output if self.output else '') + error_message

    def kill(self,pid):

        proc = Process(pid)

        #proc.send_signal(SIGSTOP)
        #proc.send_signal(SIGINT)

        for child in proc.children():
            self.kill(child.pid)

        try:
            proc.send_signal(SIGTERM)
            #print('SIGTERM send to',pid)

        except Exception as e:
            print(e)

    def run_in_thread(self):
        while self.keep_running:
            if self.command_list_to_execute:
                self.output = ''
                output_list = []
                output_list_append =  output_list.append

                try:
                    proc = Popen(self.command_list_to_execute, stdout=PIPE, stderr=STDOUT)
                    self.pid = proc.pid

                    proc_stdout_readline = proc.stdout.readline
                    proc_poll = proc.poll
                    while True:
                        output=proc_stdout_readline().decode("ISO-8859-1")
                        output_list_append(output)
                        if not output and proc_poll() is not None:
                            break

                except Exception as e:
                    self.res_ok = False
                    output_list_append(str(e))
                    print(e)

                self.output = ''.join(output_list)
                self.command_list_to_execute=None
                self.running = False
            else:
                sleep(0.001)

    def end(self):
        self.keep_running=False
        self.run_thread.join()


