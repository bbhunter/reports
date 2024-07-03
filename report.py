import re
import subprocess
import random
import os
import argparse
import platform

def run_pipe_subprocess(cmd):
    commands = cmd.split("|")
    ps = None
    for command in commands:
        command = command.strip()
        c_pieces = command.split(" ")
        for i in range(len(c_pieces)):
            if len(c_pieces[i]) > 1 and c_pieces[i][0] == '"' and c_pieces[i][-1] == '"':
                c_pieces[i] = c_pieces[i].strip('"')

        if ps:
            ps = subprocess.Popen(c_pieces, stdout=subprocess.PIPE, stdin=ps.stdout)
        else:
            ps = subprocess.Popen(c_pieces, stdout=subprocess.PIPE)
    return ps.communicate()[0].strip().decode('utf-8')

def main():
    parser = argparse.ArgumentParser(description='Generate a report from a template.')
    parser.add_argument('template', type=str, help='Template file')
    parser.add_argument('arguments', nargs=argparse.REMAINDER, help='Arguments to replace in the template')
    parser.add_argument('--code', action='store_true', help='Open the report with VSCode')
    args = parser.parse_args()

    with open(args.template, 'r') as f:
        lt = f.read()

    for i in range(len(args.arguments)):
        lt = lt.replace(f"${i}", args.arguments[i])

    commands = re.findall(r"(\{\$(.+?)\})", lt)
    for rcmd, cmd in commands:
        cmd = cmd.strip()
        output = run_pipe_subprocess(cmd)
        if "\n" in output.strip():
            result = "$> " + cmd + "\n" + output
        else:
            result = output
        lt = lt.replace(rcmd, result)

    output_dir = "/tmp" if platform.system() == "Linux" else os.getenv('TEMP')
    ofn = os.path.join(output_dir, f"{random.randint(0, 10000000)}-report.md")

    with open(ofn, 'w') as of:
        of.write(lt)

    if args.code:
        os.system(f"code {ofn}")
    else:
        if platform.system() == "Linux":
            os.system(f"xdg-open {ofn}")
        elif platform.system() == "Windows":
            os.startfile(ofn)

if __name__ == "__main__":
    main()
