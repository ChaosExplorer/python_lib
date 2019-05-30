import subprocess
import traceback
import logging
import logging.handlers
import configparser
import os
import csv
import pickle
import configparser
import simplejson
import sys
import numpy as np

BIN = os.path.dirname(os.path.abspath(__file__))
INI = os.sep.join([BIN, 'nifty.ini'])
RESOLVE = os.sep.join([BIN, 'resolve.py'])

class Task:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.cmd = kwargs['cmd']

    def __run__(self, **kwargs):
        cmd = self.get_cmd(**kwargs)
        e = ''
        try:
            pipe = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr=subprocess.PIPE, shell = True)
            out, err = pipe.communicate()
        except:
            e = traceback.format_exc().strip().replace('\n', ';')
        else:
            if not e:
                e = err.decode().strip().replace('\n', ';')
        if not pipe.returncode == 0:
            if e:
                raise RuntimeError(e)
            else:
                raise SystemError(pipe.returncode)

    def Run(self, **kwargs):
        try:
            self.__run__(**kwargs)
        except:
            raise

    def get_cmd(self, **kwargs):
        return self.cmd.format(**kwargs)


class NiftyPipeline:
    def __init__(self, **kwargs):
        self.wd = kwargs['working_index']

    def Check(self):
        wd = self.wd
        info_txt = os.sep.join([wd, 'input', 'info.txt'])
        history_result = os.sep.join([wd, 'input', 'nifty.history.result'])
        history_nifty1 = os.sep.join([wd, 'input', 'nifty1.history.info'])
        history_nifty2 = os.sep.join([wd, 'input', 'nifty2.history.info'])
        for d in [wd, info_txt, history_result, history_nifty1, history_nifty2]:
            if not os.path.exists(d):
                e = '%s NOT FOUND!' % d
                raise RuntimeError(e)

    def LoadInfo(self):
        info_txt = os.sep.join([self.wd, 'input', 'info.txt'])
        with open(info_txt) as f:
            reader = csv.reader(f, delimiter = '\t')
            headers = next(reader)
            contents = np.array([c for c in reader])
        return headers, contents
    def CreateUniqueIDs(self):
        headers, contents = self.LoadInfo()
        slide, lane, barcode, tube, fq, run, sam, pooling, date, fqstat, barcodestat, summary, bscan = [headers.index(i) for i in ['Slide', 'Lane', 'Barcode', 'Tube', 'FastQ', 'RunID', 'SampleID', 'Pooling', 'Date', 'Fq_Stat', 'Barcode_Txt', 'Summary', 'Bscan']]
        ids = np.array([(self.wd, '_'.join((sl, la, ba)), tu, f, sa, ru, po, da, fs, bcs, su, bsc) for (sl, la, ba, tu, f, ru, sa, po, da, fs, bcs, su, bsc) in contents[:,(slide, lane, barcode, tube, fq, run, sam, pooling, date, fqstat, barcodestat, summary, bscan)]])
        headers = ['path', 'id', 'tube', 'fq', 'sample_name', 'run_id', 'pooling', 'date', 'fq_stat', 'barcode_stat', 'summary', 'bscan']
        s = {'headers': headers, 'ids': ids}
        return s

    def DumpData(self, data, file):
        with open(file, 'wb') as f:
            pickle.dump(data, f)

    def LoadData(self, file):
        with open(file, 'rb') as f:
            return pickle.load(f)

    def LoadIni(self, ini):
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(ini)
        allsteps = {}
        for step in config:
            if step == 'paths':
                continue
            elif step == 'DEFAULT':
                continue
            else:
                cmd = config[step]['cmd']
                pre_indices = [i for i in config[step]['pre_indices'].strip().split(',') if not i == '']
                pre_files = [i for i in config[step]['pre_files'].strip().split(',') if not i == '']
                script = config[step]['script']
                mem = config[step]['mem']
                variables = [i for i in config[step]['variables'].strip().split(',') if not i == '']
                priors = [i for i in config[step]['priors'].strip().split(',') if not i == '']
                posts = [i for i in config[step]['posts'].strip().split(',') if not i == '']
                allsteps[step] = (cmd, pre_indices, pre_files, script, mem, variables, priors, posts)
        return allsteps

    def FindFirst(self, allsteps):
        for step in allsteps:
            if allsteps[step][-2] == []:
                return step

    def WriteAllstepsJson(self, allsteps):
        first = self.FindFirst(allsteps)
        running_info_file = os.sep.join([self.wd, 'running.info'])
        running_info = self.LoadData(running_info_file)
        allsteps = self.LoadIni(INI)
        allsteps_json = []
        for step in allsteps:
            cmd, pre_indices, pre_files, script, mem, variables, priors, posts = allsteps[step]
            variables_indices = [running_info['headers'].index(i) for i in variables]
            variables_datas = running_info['ids'][:,variables_indices]
            variables_datas = np.unique(variables_datas, axis = 0)
            allsteps_json.append({})
            allsteps_json[-1]['name'] = step
            allsteps_json[-1]['nextStep'] = posts
            allsteps_json[-1]['priorStep'] = priors
            if first == step:
                allsteps_json[-1]['first'] = 1
            allsteps_json[-1]["jobSh"] = []
            for v in variables_datas:
                s = script.format(**{variables[i]: v[i] for i in range(len(variables))})
                allsteps_json[-1]["jobSh"].append({'sh': s, 'mem': int(mem)})
                with open(s, 'w') as f:
                    print('#!/bin/bash\npython3', RESOLVE, step, *v, sep = ' ',file = f)
        allsteps_json_file = os.sep.join([self.wd, 'allSteps.json'])
        with open(allsteps_json_file, 'w') as f:
            f.write(simplejson.dumps(allsteps_json, indent=2))

    def LocateError(self):
        log_file = os.sep.join([self.wd, 'log'])
        running_info = os.sep.join([self.wd, 'running.info'])
        time = self.LoadData(running_info)['time']
        with open(log_file) as f:
            for line in f:
                try:
                    asctime, name, levelname, cmd, info, t = line.strip().split(' - ')
                except:
                    continue
                if levelname == 'ERROR' and t == time:
                    return name, cmd, info
        return None, None, None

    def HasError(self):
        log_file = os.sep.join([self.wd, 'log'])
        if not os.path.exists(log_file):
            return False
        elif self.LocateError()[0] == None:
            return False
        return True

    def Run(self, name, *args):
        running_info_file = os.sep.join([self.wd, 'running.info'])
        running_info = self.LoadData(running_info_file)
        time = running_info['time']
        ids = running_info['ids']
        allsteps = self.LoadIni(INI)
        cmd, pre_indices, pre_files, script, mem, variables, priors, posts = allsteps[name]
        variables_indices = [running_info['headers'].index(i) for i in variables]
        variables_datas = running_info['ids'][:,variables_indices]
        variables_datas = np.unique(variables_datas, axis = 0)
        log_file = os.sep.join([self.wd, 'log'])
        Logger = logging.getLogger('')
        Logger.setLevel(logging.INFO)
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        config.read(INI)
        host = config['paths']['master']
        socketHandler = logging.handlers.SocketHandler(host, logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        Logger.addHandler(socketHandler)
        t = Task(cmd = cmd, name = name)
        cmd = cmd.format(**{variables[i]: args[i] for i in range(len(variables))})
        pre_indices = [pre_index.format(**{variables[i]: args[i] for i in range(len(variables))}) for pre_index in pre_indices]
        pre_files = [pre_file.format(**{variables[i]: args[i] for i in range(len(variables))}) for pre_file in pre_files]
        m = ' - '.join([log_file, cmd, 'calling', time])
        #Logger.info(m)
        logging.info(m)
        variables_datas = tuple(tuple(variables_datas[i]) for i in range(len(variables_datas)))
        for pre_index in pre_indices:
            if not os.path.exists(pre_index):
                os.makedirs(pre_index)
        if self.HasError():
            info = 'an error is found'
            m = ' - '.join([log_file, cmd, info, time])
            Logger.error(m)
        elif not args in variables_datas:
            info = 'not runned'
            m = ' - '.join([log_file, cmd, info, time])
            Logger.warn(m)
        else:
            try:
                for pre_file in pre_files:
                    if not os.path.exists(pre_file):
                        e = '%s NOT FOUND' % pre_file
                        raise RuntimeError(e)
                t.Run(**{variables[i]: args[i] for i in range(len(variables))})
            except:
                e = traceback.format_exc().strip().replace('\n', ';')
                m = ' - '.join([log_file, cmd, e, time])
                Logger.error(m)
            else:
                m = ' - '.join([log_file, cmd, 'finished', time])
                Logger.info(m)

    def InitializeFlow(self):
        self.Check()
        s = self.CreateUniqueIDs()
        s['time'] = '1'
        running_info_file = os.sep.join([self.wd, 'running.info'])
        with open(running_info_file, 'wb') as f:
            pickle.dump(s, f)
        total_info_file = os.sep.join([self.wd, 'total.info'])
        with open(total_info_file, 'wb') as f:
            pickle.dump(s, f)
        allsteps = self.LoadIni(INI)
        scripts = os.sep.join([self.wd, 'scripts'])
        if not os.path.exists(scripts):
            os.mkdir(scripts)
        for step in allsteps:
            step_dir = os.sep.join([self.wd, 'scripts', step])
            if not os.path.exists(step_dir):
                os.mkdir(step_dir)
        self.WriteAllstepsJson(allsteps)

    def StartNewFlow(self):
        self.Check()
        running_info_file = os.sep.join([self.wd, 'running.info'])
        s = self.LoadData(running_info_file)
        time = str(int(s['time']) + 1)
        s = self.CreateUniqueIDs()
        s['time'] = time
        with open(running_info_file, 'wb') as f:
            pickle.dump(s, f)

def main(path):
    T = NiftyPipeline(working_index = path)
    if os.path.exists(os.sep.join([T.wd, 'running.info'])):
        T.StartNewFlow()
    else:
        T.InitializeFlow()

if __name__ == '__main__':
    if not len(sys.argv) == 2:
        sys.exit('python3 nflow.py [path]')
    Result = os.sep.join([sys.argv[1], 'Result'])
    if os.path.exists(Result):
        result_suffix = os.sep.join([Result, '*.result'])
        info_suffix = os.sep.join([Result, '*.info'])
        qc_suffix = os.sep.join([Result, '*.qc'])
        all_files = ' '.join([result_suffix, info_suffix, qc_suffix])
        os.system('rm %s' % all_files)
    main(sys.argv[1])
