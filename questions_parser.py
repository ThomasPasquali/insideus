import yaml
import subprocess
import os
import tempfile
import argparse
from dataclasses import dataclass
from pathlib import Path
import random

@dataclass
class Card:
    key: str
    text: str
    options: list[str]
    correct: int | None
    curiosity: str | None

    def shuffle_options(self):
        if self.correct is not None:
            correct_text = self.options[self.correct]
        random.shuffle(self.options)
        if self.correct is not None:
            self.correct = self.options.index(correct_text)

def generate_tex(cards: list[Card]) -> str:
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

    \newcommand{\card}[3]{
        \begin{tikzpicture}[x=1mm,y=1mm]
            % Border node
            \draw[rounded corners=\cardroundingradius, fill=green!20] (0,0) rectangle (\cardwidth,\cardheight);
            % Text node
            \node[below right,fill=blue!20,
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
                {\optionfontsize #2}
            };
            % Curiosity node
            \node[
                    above right, fill=blue!10,
                    minimum width=(\cardwidth-2*\textpadding)*1mm,
                    text width=(\cardwidth-3*\textpadding)*1mm,
                    align=left,
                    execute at begin node=\setlength{\baselineskip}{0.5em}
                ] 
                at (\textpadding, \textpadding) {
                \curiosityfontsize\textit{#3}
            };
        \end{tikzpicture}
    }
    """

    for i, c in enumerate(cards):
        #FIXME c.shuffle_options()
        card_tex = r"""\card
            {QUESTION}
            {\begin{enumerate}[A),leftmargin=*]
                \setlength{\itemsep}{0pt}
                \setlength{\parskip}{0pt}
                \setlength{\parsep}{0pt}
                OPTIONS
            \end{enumerate}}
            {CURIOSITY}"""
        card_tex = card_tex.replace('QUESTION', c.text)
        card_tex = card_tex.replace('CURIOSITY', c.curiosity if c.curiosity is not None else '')
        if c.options is not None:
            options_tex = []
            for j, o in enumerate(c.options):
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

def generate_pdf(pdfname: str, cards: list[Card]):
    print(generate_tex(cards))
    
    with tempfile.NamedTemporaryFile(delete_on_close=False) as f:
        f.write(str.encode(generate_tex(cards)))
        f.close()
        proc = subprocess.Popen(['pdflatex', f.name])
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
                    cards.append(Card(key=q, text=question['text'], options=question['options'], correct=question['correct'], curiosity=question.get('curiosity')))
                case 'tf':
                    cards.append(Card(key=q, text=question['text'], options=['Vero', 'Falso'], correct=question['correct'], curiosity=question.get('curiosity')))
                case 'enum':
                    cards.append(Card(key=q, text=question['text'], options=question['options'], correct=None, curiosity=question.get('curiosity')))
                case _ as a:
                    raise Exception(f'kind {a} not found')
    return cards

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='')
    parser.add_argument('file', help='specify the questions yaml file.')
    args = parser.parse_args()

    generate_pdf(f'{Path(args.file).stem}.pdf', generate_cards_from_file(args.file))