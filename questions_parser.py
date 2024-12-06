import yaml
import subprocess
import os
import re
import tempfile
import argparse
from dataclasses import dataclass
from pathlib import Path
import random

@dataclass
class Card:
    kind: str
    key: str
    text: str
    options: list[str]
    correct: int | None
    curiosity: str | None
    difficulty: int

    def shuffle_options(self):
        if self.kind == 'mc':
            if self.correct is not None:
                correct_text = self.options[self.correct]
            random.shuffle(self.options)
            if self.correct is not None:
                self.correct = self.options.index(correct_text)

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

def generate_tex(args: argparse.Namespace, cards: list[Card]) -> str:
    tex = r"""
    \documentclass[parskip]{scrartcl}
    \usepackage[margin=5mm]{geometry}
    \usepackage{tikz}
    \usepackage{graphicx}
    \usepackage[shortlabels]{enumitem}
    \usepackage{setspace}
    \usepackage[condensed,math]{anttor}
    \usepackage[T1]{fontenc}

    \begin{document}

    \pgfmathsetmacro{\cardroundingradius}{2}
    \pgfmathsetmacro{\cardwidth}{64}
    \pgfmathsetmacro{\cardheight}{89}
    \pgfmathsetmacro{\textpadding}{2}
    \pgfmathsetmacro{\ruleheight}{0.2}

    \newcommand{\questionfontsize}{\large}
    \newcommand{\optionfontsize}{\normalsize}
    \newcommand{\curiosityfontsize}{\small}

    \newcommand{\card}[4]{
        \begin{tikzpicture}[x=1mm,y=1mm]
            % Border node
            \draw[rounded corners=\cardroundingradius] (0,0) rectangle (\cardwidth,\cardheight);
            % Text node
            \node[below right,
                    % minimum height=(\cardheight-2*\textpadding)*1mm,
                    minimum width=(\cardwidth-2*\textpadding)*1mm,
                    text width=(\cardwidth-3*\textpadding)*1mm,
                    align=left
                ] 
                at (\textpadding,\cardheight-\textpadding) {
                {\questionfontsize\textbf{\textit{#1}}}\\[-2mm]
                % Separator line
                \tikz{\fill (0,0) rectangle (\cardwidth-4*\textpadding,\ruleheight);}\\[0mm]
                % Options text
                \vspace{-3mm}
                {\optionfontsize\textsc{#2}}
            };
            % Curiosity node
            \node[
                    above right,
                    minimum width=(\cardwidth-2*\textpadding)*1mm,
                    text width=(\cardwidth-3*\textpadding)*1mm,
                    align=left,
                    execute at begin node=\setlength{\baselineskip}{0.5em}
                ] 
                at (\textpadding, \textpadding) {
                \curiosityfontsize\textit{#3}
            };
            % Difficulty node
            \node[
                    above right,
                    minimum width=(\cardwidth-2*\textpadding)*1mm,
                    text width=(\cardwidth-3*\textpadding)*1mm,
                    align=right,
                    execute at begin node=\setlength{\baselineskip}{0.5em}
                ] 
                at (\textpadding, \textpadding) {
                \curiosityfontsize\textit{#4}
            };
        \end{tikzpicture}
    }
    """

    for i, c in enumerate(cards):
        c.shuffle_options()
        itemize = c.kind in ['tf', 'enum']
        card_tex = r"""\card
            {QUESTION}
        """ + (r'{\begin{itemize}[leftmargin=*]' if itemize else r'{\begin{enumerate}[A),leftmargin=*]') + r"""\setlength{\itemsep}{0pt}
                \setlength{\parskip}{0pt}
                \setlength{\parsep}{0pt}
                OPTIONS
        """ + (r'\end{itemize}}' if itemize else r'\end{enumerate}}') + r'{CURIOSITY}{DIFFICULTY}'

        card_tex = card_tex.replace('QUESTION', tex_escape(c.text))

        curiosity = ''
        if c.curiosity is not None and args.include_curiosity:
            curiosity = tex_escape(c.curiosity)
        card_tex = card_tex.replace('CURIOSITY', curiosity)

        difficulty = r'$\star$' if c.difficulty == 1 else ''
        card_tex = card_tex.replace('DIFFICULTY', difficulty)

        if c.options is not None:
            options_tex = []
            for j, o in enumerate(c.options):
                o = tex_escape(str(o))
                correct = c.correct is not None and c.correct == j
                # options_tex.append(f'\\item {"\\textbf{" if correct else ""}{o}{"}" if correct else ""}')
                options_tex.append(('\\bfseries ' if correct else '') + '\\item ' + str(o) + ('\\mdseries' if correct else ''))
            card_tex = card_tex.replace('OPTIONS', '\n'.join(options_tex))

        tex += card_tex
        if (i+1)%3 == 0:
            tex += r'\\[5mm]'
        tex += '\n'

    tex += r'\end{document}'
    return tex

def generate_pdf(args: argparse.Namespace, pdfname: str, cards: list[Card]):
    tex = generate_tex(args, cards)
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

def generate_cards_from_file(filename: str) -> list[Card]:
    cards = []
    with open(filename, 'r') as file:
        questions = yaml.safe_load(file)
        #print(questions)
        for q in questions.keys():
            question = questions[q]
            #print(q)
            #print(question)
            match question['kind']:
                case 'mc':
                    cards.append(Card(kind=question['kind'], key=q, text=question['text'], options=question['options'], correct=question['correct'], curiosity=question.get('curiosity'), difficulty=question['difficulty']))
                case 'tf':
                    cards.append(Card(kind=question['kind'], key=q, text=question['text'], options=['Vero', 'Falso'], correct=question['correct'], curiosity=question.get('curiosity'), difficulty=question['difficulty']))
                case 'enum':
                    cards.append(Card(kind=question['kind'], key=q, text=question['text'], options=question['options'], correct=None, curiosity=question.get('curiosity'), difficulty=question['difficulty']))
                case _ as a:
                    raise Exception(f'kind {a} not found')
    return cards

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='')
    parser.add_argument('file', help='specify the questions yaml file.')
    parser.add_argument('--include_curiosity', '-c', action='store_true', default=False)
    args = parser.parse_args()

    generate_pdf(args, f'{Path(args.file).stem}.pdf', generate_cards_from_file(args.file))