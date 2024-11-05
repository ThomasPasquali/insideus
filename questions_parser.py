import yaml
import subprocess
import os
import tempfile
import shutil
import argparse
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Card:
    text: str
    options: list[str]
    correct: int | None
    curiosity: str | None

def generate_tex(cards: list[Card]) -> str:
    tex = r"""
    \documentclass[parskip]{scrartcl}
    \usepackage[margin=5mm]{geometry}
    \usepackage{tikz}
    \usepackage{graphicx}
    \usepackage[shortlabels]{enumitem}

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
                    minimum height=(\cardheight-2*\textpadding)*1mm,
                    minimum width=(\cardwidth-2*\textpadding)*1mm,
                    text width=(\cardwidth-3.5*\textpadding)*1mm,
                    align=left
                ] 
                at (\textpadding,\cardheight-\textpadding) {
                \begin{center}{\questionfontsize\textbf{\textit{#1}}}\end{center}
                % Separator line
                \tikz{\fill (0,0) rectangle (\cardwidth-4*\textpadding,\ruleheight);}\\[1mm]
                % Options text               
                \vspace{\fill}
                {\optionfontsize #2}
            };
            % Curiosity node
            \node[
                    above right, fill=blue!10,
                    minimum width=(\cardwidth-2*\textpadding)*1mm,
                    text width=(\cardwidth-3.5*\textpadding)*1mm,
                    align=left
                ] 
                at (\textpadding, \textpadding) {
                {\curiosityfontsize \textit{#3}}
            };
        \end{tikzpicture}
    }
    """

    for i, c in enumerate(cards):
        card_tex = r"""\card
            {QUESTION}
            {\begin{enumerate}[A)]
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
                options_tex.append(f'{"\\bfseries " if correct else ""}\\item {o}{"\\mdseries" if correct else ""}')
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='')
    parser.add_argument('file', help='specify the questions yaml file.')
    args = parser.parse_args()

    cards = []

    with open(args.file, 'r') as file:
        questions = yaml.safe_load(file)
        print(questions)
        for q in questions.keys():
            question = questions[q]
            print(q)
            print(question)
            match question['kind']:
                case 'mc':
                    cards.append(Card(text=question['text'], options=question['options'], correct=question['correct'], curiosity=question.get('curiosity')))
                case 'tf':
                    cards.append(Card(text=question['text'], options=['Vero', 'Falso'], correct=question['correct'], curiosity=question.get('curiosity')))
                case 'enum':
                    cards.append(Card(text=question['text'], options=question['options'], correct=None, curiosity=question.get('curiosity')))
                case _ as a:
                    raise Exception(f'kind {a} not found')
    
    generate_pdf(f'{Path(args.file).stem}.pdf', cards)