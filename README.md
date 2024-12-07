# InsideUS cards generator

## Cards content
To generate a `pdf` file containing the cards (9 each A4 page), run:

```bash
python3 questions_parser.py <questions>.yaml
```
> The file `questions_template.yaml` provides the yaml format for the questions.

## Cards back
To generate a `pdf` file containing 9 cards back image, run:

```bash
python3 cards_back.py <back_image_file>
```