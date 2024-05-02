import yaml
import subprocess
import os
import tempfile
import shutil

def generate_pdf(pdfname, tex):
    """
    Genertates the pdf from string
    """

    current = os.getcwd()
    temp = tempfile.mkdtemp()
    os.chdir(temp)

    f = open('card.tex','w')
    f.write(tex)
    f.close()

    proc=subprocess.Popen(['pdflatex', 'card.tex'])
    subprocess.Popen(['pdflatex',tex])
    proc.communicate()

    os.rename('card.pdf',pdfname)
    shutil.copy(pdfname,current)
    shutil.rmtree(temp)

if __name__ == '__main__':
    with open('questions.yaml', 'r') as file:
        questions = yaml.load(file)
        # print(questions)
        for q in questions.keys():
            question = questions[q]
            print(q)
            print(question)
            print(f'Corretta: <<< {question.get("options")[question["correct"]]} >>>')


    tex = r"""\documentclass[parskip]{scrartcl}
    \usepackage[margin=15mm]{geometry}
    \usepackage{tikz}
    \usepackage{pifont}

    \begin{document}

    \pgfmathsetmacro{\cardwidth}{5}
    \pgfmathsetmacro{\cardheight}{8}
    \newcommand{\stripcolor}{lime}
    \pgfmathsetmacro{\stripwidth}{0.7}
    \pgfmathsetmacro{\strippadding}{0.1}
    \newcommand{\striptext}{INTER ARMA \ding{74}}
    \pgfmathsetmacro{\textpadding}{0.3}
    \newcommand{\topcaption}{LATIN}
    \newcommand{\topcontent}{\textit{''Inter Arma Enim Silent Leges''}}
    \newcommand{\bottomcaption}{Inter Arma}
    \newcommand{\bottomcontent}{In times of war, the law falls silent.\\ \tikz{\fill[even odd rule] (0,0) circle (0.3) (-0.2,-0.2) rectangle (0.2,0.2);}}
    \pgfmathsetmacro{\ruleheight}{0.3}

    \begin{tikzpicture}
        \draw[rounded corners=0.2cm] (0,0) rectangle (\cardwidth,\cardheight);
        \fill[\stripcolor,rounded corners=0.1cm] (\strippadding,\strippadding) rectangle (\strippadding+\stripwidth,\cardheight-\strippadding) node[rotate=90,above left,black,font=\LARGE] {\striptext};
        \node[text width=(\cardwidth-\strippadding-\stripwidth-2*\textpadding)*1cm,below right] at (\strippadding+\stripwidth+\textpadding,\cardheight-\textpadding) 
            {\LARGE \topcaption}\\ 
            \topcontent\\
            \tikz{\fill (0,0) rectangle (\cardwidth-\strippadding-\stripwidth-2*\textpadding,\ruleheight);}\\
            {\LARGE \bottomcaption}\\ 
            \bottomcontent\\
        };
    \end{tikzpicture}
    \end{document}"""

    generate_pdf('card.pdf', str(tex))