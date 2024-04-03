# LLM Discharge Summaries

This repo contains the experimental code for the paper ["Automated Generation of Hospital Discharge Summaries Using Clinical Guidelines and Large Language Models"](https://openreview.net/forum?id=1kDJJPppRG&trk=public_post_comment-text)

![Method Diagrame](figures/end_to_end.png)

In brief the method is:
1. Convert a set of [guidelines from the Royal College of Physcians London](https://www.rcplondon.ac.uk/guidelines-policy/improving-discharge-summaries-learning-resource-materials) (RCP) into a json schema
1. Convert an example also provided by RCP into a 1 shot prompt
1. De-duplicate a set of physician notes ([MIMIC-III](https://physionet.org/content/mimiciii/1.4/) used for experiments)
1. Use the above as a prompt to an LLM ([GPT-4-turbo](https://platform.openai.com/docs/models/gpt-4-and-gpt-4-turbo))

## Setup

Requirements
1. Installed [poetry](https://python-poetry.org/docs/) and to
1. Approval to access [MIMIC-III](https://physionet.org/content/mimiciii/1.4/)
1. Ability to deploy Azure OpenAI models

### Install required packages

```bash
poetry install
```

### Download and unzip MIMIC-III notes

```bash
wget -r -N -c -np --user simonellershawucl --ask-password -P ./mimic_experiments/inputs/ https://physionet.org/files/mimiciii/1.4/NOTEEVENTS.csv.gz
gzip -d mimic_experiments/inputs/physionet.org/files/mimiciii/1.4/NOTEEVENTS.csv.gz
```

### Deploy GPT-4-turbo through Azure
1. Deployment steps are set out [here](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource?pivots=web-portal)
1. To recreate results must be "gpt-4" version "1106-Preview"
1. IMPORTANT: Turn off content filter to follow [MIMIC's terms of use](https://physionet.org/news/post/415)

Note gpt-4-turbo is only available in certain regions ([see docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#gpt-4-and-gpt-4-turbo-preview-model-availability))

### Setup Azure OpenAI Credentials
Changing out the values for your personal credentials

```bash
echo "AZURE_OPENAI_KEY_1 = <YOUR_AZURE_OPENAI_KEY>" >> .env

echo "AZURE_OPENAI_ENDPOINT_1 = <YOUR_AZURE_OPENAI_ENDPOINT>" >> .env
```

## Running

As all experiments used MIMIC-III we cannot distribute the produced summaries and evaluation (conducted by a team of clinicians).

But the notebooks (from 1-4) in `mimic_experiments/` allows for recreation of all the discharge summaries evaluated in the paper including as an excel for human annotations.

Also the code used to generate the metrics (notebook 5) is given for transparency however cannot be run without access to the clinical annotation. If this is of interest and you are a credentialed MIMIC user please reach out.


## Future Work

- Simple Streamlit demo
- Some code decisions were suboptimal but are entrenched for reproducbility (e.g. dealing with empty json values when creating annotator excels rather than when saving to json)

## Citing

If using any of the code or ideas in this repo please cite us!
```
@inproceedings{ellershaw2024automated,
  title={Automated Generation of Hospital Discharge Summaries Using Clinical Guidelines and Large Language Models},
  author={Ellershaw, Simon and Tomlinson, Christopher and Burton, Oliver E and Frost, Thomas and Hanrahan, John Gerrard and Khan, Danyal Zaman and Horsfall, Hugo Layard and Little, Mollie and Malgapo, Evaleen and Starup-Hansen, Joachim and others},
  booktitle={AAAI 2024 Spring Symposium on Clinical Foundation Models},
  year={2024}
}
```

## Contact

Please contact <simon.ellershaw.20@ucl.ac.uk> with any questions
