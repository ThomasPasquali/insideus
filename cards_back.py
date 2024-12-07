import yaml
import subprocess
import os
import re
import tempfile
import argparse
from pathlib import Path

def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    conv = {
        # '&': r'\&',
        '%': r'\%',
        # '$': r'\$',
        # '#': r'\#',
        # '_': r'\_',
        # '{': r'\{',
        # '}': r'\}',
        # '~': r'\textasciitilde{}',
        # '^': r'\^{}',
        # '\\': r'\textbackslash{}',
        # '<': r'\textless{}',
        # '>': r'\textgreater{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key = lambda item: - len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

def generate_tex(filename: str) -> str:
    tex = r"""
    \documentclass[parskip]{scrartcl}
    \usepackage[margin=5mm]{geometry}
    \usepackage{tikz}
    \usepackage{graphicx}
    \usepackage[shortlabels]{enumitem}
    \usepackage{setspace}

    \begin{document}
        \pgfmathsetmacro{\cardroundingradius}{2}
        \pgfmathsetmacro{\cardwidth}{64}
        \pgfmathsetmacro{\cardheight}{89}
        \pgfmathsetmacro{\textpadding}{2}
        \pgfmathsetmacro{\ruleheight}{0.2}

        \newcommand{\questionfontsize}{\large}
        \newcommand{\optionfontsize}{\normalsize}
        \newcommand{\curiosityfontsize}{\small}

        \newcommand{\card}{
            \begin{tikzpicture}[x=1mm,y=1mm]
                % Border node
                % \draw[rounded corners=\cardroundingradius] (0,0) rectangle (\cardwidth,\cardheight);
                % Text node
                \node[below right,
                        % minimum height=(\cardheight-2*\textpadding)*1mm,
                        minimum width=(\cardwidth)*1mm,
                        text width=(\cardwidth-1mm)*1mm,
                        align=left
                    ] 
                    at (0,\cardheight - 0.5) {\includegraphics[width=\textwidth]{FILE}};

            \end{tikzpicture}
        }
        \card
        \card
        \card\\[5mm]
        \card
        \card
        \card\\[5mm]
        \card
        \card
        \card

    \end{document}
    """

    tex = tex.replace('FILE', tex_escape(filename))
    return tex

def generate_pdf(pdfname: str, filename: str):
    tex = generate_tex(filename)
    print(tex)

    f = open("tmp.tex", "w+")
    f.write(tex)
    f.close()
    
    with tempfile.NamedTemporaryFile(delete_on_close=False) as f:
        f.write(str.encode(tex))
        f.close()
        proc = subprocess.Popen(['pdflatex', f.name])
        # proc = subprocess.Popen(['xelatex', f.name])
        proc.communicate()
        f_stem = Path(f.name).stem
        os.rename(f'{f_stem}.pdf', pdfname)
        os.remove(f'{f_stem}.aux')
        os.remove(f'{f_stem}.log')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='')
    parser.add_argument('file', help='specify the back image file.')
    args = parser.parse_args()

    path = Path(args.file)
    generate_pdf(f'{path.stem}.pdf', str(path.resolve()))