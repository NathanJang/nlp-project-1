# Project 1
Jonathan Chan (ycc4645), Yousef Issa (yii0104)

## Runtime Environment
Tested locally on Python 3.6 and 3.7.

Install dependencies:
1. `pip install -r requirements.txt`
2. `spacy download en_core_web_sm` or `python -m spacy download en_core_web_sm`

Tweet data should be stored in the project root with the filename `gg{year}.json`.

## Running
- `python gg_api.py {year}`

## Notes
It seems like our solution for `get_presenters` is incomplete and times out. However, the rest of the functions do not
time out.

We took a look at from https://github.com/brownrout/EECS-337-Golden-Globes, but the solution did not seem to fit our
needs.

We had another team member drop the class before we were able to complete the project, and are requesting the 48-hour
extension policy.
