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

from subprocess import Popen, STDOUT, PIPE,TimeoutExpired
from time import time
from signal import SIGTERM
from hashlib import sha1
from os import sep

from os import name as os_name
from sys import getsizeof

from psutil import Process

windows = bool(os_name=='nt')
PARAM_INDICATOR_SIGN = '%'

def get_command_list(executable,parameters,full_file_path,shell=False):
    if windows:
        full_file_path = full_file_path.replace('/',sep)

    if shell:
        executable=f'"{executable}"'
        full_file_path = f'"{full_file_path}"'

    if parameters:
        if PARAM_INDICATOR_SIGN not in parameters:
            return None
        parameters = parameters.replace(f'"{PARAM_INDICATOR_SIGN}"',PARAM_INDICATOR_SIGN)
    else:
        parameters=PARAM_INDICATOR_SIGN

    parameters_list = [p_elem.replace(PARAM_INDICATOR_SIGN,full_file_path) for p_elem in parameters.split() if p_elem]

    single_command_list = [executable] + parameters_list

    return single_command_list

class Executor :
    def __init__(self,io_list,callback):
        self.io_list=io_list
        self.callback=callback

        self.keep_running=True
        self.timeout=None
        self.info = ''

        self.files_cde_errors_quant = 0

        self.files_cde_quant = 0
        self.files_cde_size = 0
        self.files_cde_size_extracted = 0

    def calc_crc(self,fullpath,size):
        CRC_BUFFER_SIZE=4*1024*1024
        buf = bytearray(CRC_BUFFER_SIZE)
        view = memoryview(buf)

        #self.crc_progress_info=0

        try:
            file_handle=open(fullpath,'rb')
            file_handle_readinto=file_handle.readinto
        except Exception as e:
            #self.log.error(e)
            print(e)
            return None

        hasher = sha1()
        hasher_update=hasher.update

        #faster for smaller files
        if size<CRC_BUFFER_SIZE:
            hasher_update(view[:file_handle_readinto(buf)])
        else:
            while rsize := file_handle_readinto(buf):
                hasher_update(view[:rsize])

                #if rsize==CRC_BUFFER_SIZE:
                    #still reading
                    #self.crc_progress_info+=rsize

                if not self.keep_running:
                    break

            #self.crc_progress_info=0

        file_handle.close()

        if not self.keep_running:
            return None

        #only complete result
        #return hasher.hexdigest()
        return hasher.digest()

    def abort_now(self):
        self.keep_running=False
        self.timeout=time()

    def run(self):
        for single_command_combo in self.io_list:
            self_results_list_append = single_command_combo.append
            executable,parameters,full_file_path,timeout,shell,do_crc,size = single_command_combo[0:7]
            #do_crc = False #TODO hidden option

            single_command_list = get_command_list(executable,parameters,full_file_path,shell)

            if self.keep_running:
                killed=False
                returncode=200

                try:
                    self.timeout=time()+timeout if timeout else None

                    #####################################
                    single_command_list_joined = ' '.join(single_command_list)
                    self.info = single_command_list_joined

                    command = single_command_list_joined if shell else single_command_list
                    with Popen(command, stdout=PIPE, stderr=STDOUT,shell=shell) as proc:
                        while True:
                            try:
                                output, errs = proc.communicate(timeout=0.001)
                                #output = output + errs  # errs should be empty
                            except TimeoutExpired:
                                self.callback()
                                if self.timeout:
                                    if pid:=proc.pid:
                                        if time()>self.timeout:
                                            self.kill(pid)
                                            killed=True
                            except Exception as e:
                                print('run disaster:',e)

                            else:
                                break

                        try:
                            output = output.decode()
                        except Exception as de:
                            output = str(de)
                            #pass

                        returncode=proc.returncode
                    #####################################

                except Exception as e:
                    output = str(e)
                    print('run_error:',e)
                    returncode=100 if killed else 101

                if killed:
                    returncode = 102
                    output = output + '\nKilled.'

                #if do_crc:
                #    crc=self.calc_crc(full_file_path,size)
                #    self_results_list_append(tuple([returncode,output,crc]))
                #else:
                #    self_results_list_append(tuple([returncode,output]))

            else:
                returncode = 300
                output = 'CDE aborted'
                #if do_crc:
                #    self_results_list_append((300,'CDE aborted',0))
                #else:
                #    self_results_list_append((300,'CDE aborted'))

            self_results_list_append(tuple([returncode,output]))

            if returncode:
                self.files_cde_errors_quant+=1

            self.files_cde_quant += 1
            self.files_cde_size += size
            self.files_cde_size_extracted += getsizeof(output)


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
            print('kill',e)
