#Autho : amir masoud noohi
#Copyright : GPL

from multiprocessing import Process, cpu_count
import random
import time
import json
import sys
import re
import os


class ProgressBar(object):
    DEFAULT = 'Progress: %(bar)s %(current)d Bytes /%(total)d Bytes (%(percent)3d%%)'
    FULL = '%(bar)s %(current)d/%(total)d (%(percent)3d%%) %(remaining)d to go'

    def __init__(self, total, width=40, fmt=DEFAULT, symbol='=',
                 output=sys.stderr):
        assert len(symbol) == 1

        self.total = total
        self.width = width
        self.symbol = symbol
        self.output = output
        self.fmt = re.sub(r'(?P<name>%\(.+?\))d', r'\g<name>%dd' % len(str(total)), fmt)

        self.current = 0

    def __call__(self):
        percent = self.current / float(self.total)
        size = int(self.width * percent)
        remaining = self.total - self.current
        bar = '[' + self.symbol * size + ' ' * (self.width - size) + ']'

        args = {
            'total': self.total,
            'bar': bar,
            'current': self.current,
            'percent': percent * 100,
            'remaining': remaining
        }
        print('\r' + self.fmt % args, file=self.output, end='')

    def done(self):
        self.current = self.total
        self()
        print('', file=self.output)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def wait(length=0.1104):
    try:
        time.sleep(length)
    except KeyboardInterrupt:
        pass


def loading(text, speed):
    try:
        while True:
            print(bcolors.OKBLUE + "\r" + "[-] " + text + bcolors.ENDC)
            sys.stdout.write("\033[F")
            wait(speed)
            print(bcolors.OKBLUE + "\r" + "[\\] " + text + bcolors.ENDC)
            sys.stdout.write("\033[F")
            wait(speed)
            print(bcolors.OKBLUE + "\r" + "[|] " + text + bcolors.ENDC)
            sys.stdout.write("\033[F")
            wait(speed)
            print(bcolors.OKBLUE + "\r" + "[/] " + text + bcolors.ENDC)
            sys.stdout.write("\033[F")
            wait(speed)

    except KeyboardInterrupt:
        exit(0)


def pstart(text, speed):
    p = Process(target=loading, args=(text, speed,))
    p.daemon = True
    p.start()
    return p


def pstop(p, timeout=3):
    wait(timeout)
    sys.stdout.write("\r")
    p.terminate()


def clean():
    sys.stdout.write("\033[F")
    os.system("clear")


def check_progress(size):
    try:
        progress = ProgressBar(size * 2**20, width=40, fmt=ProgressBar.DEFAULT, symbol="#")
        while progress.current < progress.total:
            time.sleep(0.001)
            progress.current = os.path.getsize("output.txt")
            progress()
        progress.done()
    except:
        pass


def run(size, numberOfWords, file):
    try:
        i = 0
        while os.path.getsize("output.txt") < size * 2**20:
            string = json_data[random.randint(0, json_size - 1)]
            if os.path.getsize("output.txt") + len(string) > size * 2**20:
                break
            if i == numberOfWords:
                i = 0
                file.write("\n")
            i += 1
            file.write(string + " " if i != numberOfWords else "")
    except:
        pass


if __name__ == '__main__':
    try:
        clean()
        p = pstart("Loading Data...", 0.1)
        json_data = json.load(open('words.json'))
        json_size = len(json_data)
        pstop(p)
        os.system("clear")
        print(bcolors.OKGREEN + "[+] Data Loaded Successfully" + bcolors.ENDC)
        size = int(input("Enter Output Size(MByte) [Default : 64]: ") or 64)
        numberOfWords = int(input("Enter Number of Words Per Line [Default = 25] : ") or 25)
        file = open("output.txt", "w")
        pool = [Process(target=run, args=(size, numberOfWords, file,)) for x in
                range(cpu_count() - 1)] + [Process(target=check_progress, args=(size,))]
        for process in pool:
            process.start()
        for process in pool:
            process.join()
        file.close()
        clean()
        print(bcolors.OKGREEN + "[+] Data Loaded Successfully" + bcolors.ENDC)
        print(bcolors.OKGREEN + "[+] Data Generated Size : " + str(os.path.getsize("output.txt") / 2**20)
              + " MBytes " + bcolors.ENDC)
    except KeyboardInterrupt:
        print(bcolors.FAIL + "\n[-] Keyboard Interrupt Pressed" + bcolors.ENDC)
        print(bcolors.WARNING + "[+] Data Generated Size : " + str(os.path.getsize("output.txt") / 2**20)
              + " MBytes " + bcolors.ENDC)
    except:
        print(bcolors.FAIL + "\n[-] Generating Cancelled" + bcolors.ENDC)
        print(bcolors.WARNING + "[+] Data Generated Size : " + str(os.path.getsize("output.txt") / 2**20)
              + " MBytes " + bcolors.ENDC)
