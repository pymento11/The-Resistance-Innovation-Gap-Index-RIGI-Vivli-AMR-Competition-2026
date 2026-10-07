# The Resistance-Innovation Gap Index (RIGI): A Two-Tier Framework for Comparing Resistance Trends with Global AMR R&D Funding

**Jiahui Zuo¹†, Archchana Arulananthan²†, Justin Pymento³†, Shahila Christie⁴**  
¹ University of Georgia; ² McMaster University; ³ University of Toronto; ⁴ Future Ethos, LLC  
† Jiahui Zuo, Archchana Arulananthan, and Justin Pymento contributed equally to this work and share first authorship.


## About this repository

This repository contains the data preparation, harmonization, funding-classification, and statistical analysis code developed for our **2026 Vivli AMR Surveillance Data Challenge** project.

## Letter of Intent

**The Resistance-Innovation Gap Index (RIGI): A Two-Tier Framework for Comparing Resistance Trends with Global AMR R&D Funding**

Despite the approval of multiple new antibiotics since 2016, mortality from difficult-to-treat (DTR) Gram-negative infections has not improved, with predicted-ineffective initial therapy reaching 84% in 2023 (Walker et al., 2026). This clinical failure reflects a fundamental misalignment between where resistance is accelerating most rapidly and where innovation capital is deployed. No existing framework integrates real-world resistance acceleration with pipeline investment volume at a pathogen-drug level to produce actionable prioritization signals.

We will develop the Resistance-Innovation Gap Index (RIGI), an interpretable prioritization framework identifying potential gaps between resistance trends and therapeutic innovation. We will integrate MIC trend data from the Pfizer ATLAS, Paratek KEYSTONE, and Innoviva *Acinetobacter baumannii* datasets with the Global AMR R&D Funding Hub, focusing on three WHO-priority Gram-negative pathogen categories: Enterobacteriaceae, *Acinetobacter baumannii*, and *Pseudomonas aeruginosa*.

Censoring-aware Gaussian mixture models will be applied to raw MIC distributions to estimate resistant-cluster membership, with classifications validated against source CLSI susceptibility interpretations. Mixed-effects models will then estimate longitudinal resistance trends, including continent-specific trends. A text-mining pipeline will be developed to classify Funding Hub projects by target organism to estimate documented public and philanthropic funding shares. These outputs form the RIGI: a two-tier framework comparing organism-level resistance trends with funding share and characterizing geographic variation. As the Funding Hub does not capture private-sector investment, RIGI reflects the publicly visible innovation landscape; private R&D remains a limitation and direction for future expansion.

RIGI will produce a transparent framework highlighting potential resistance-innovation gaps while preserving uncertainty and regional coverage. By translating surveillance data into actionable prioritization signals, RIGI can directly inform funders, product developers, WHO priority-setting processes, and national AMR action plans in guiding resources toward unmet antibacterial needs.

## Repository contents

The analysis code is organized according to the project workflow.

### `data_preparation/`

Contains the five sequential Python files used for cleaning, harmonization, and preparation of the antimicrobial resistance surveillance datasets:

- `01_clean_atlas.py`
- `02_clean_acinetobacter.py`
- `03_clean_keystone.py`
- `04_initial_combination.py`
- `05_additional_cleaning_and_harmonization.py`

These scripts process the Pfizer ATLAS, Paratek KEYSTONE, and Innoviva *Acinetobacter* datasets and prepare the harmonized surveillance dataset used in the main analysis.

### `06_Global_funding_hub_extraction.py`

Python text-mining pipeline used to classify Global AMR R&D Funding Hub projects by target organism and derive the funding data used in RIGI.

### `07_RIGI_main_analysis.Rmd`

Main R analysis file integrating the harmonized surveillance and funding data and conducting the MIC classification, validation, longitudinal resistance modelling, and RIGI analyses.

## Data availability

The underlying antimicrobial resistance surveillance datasets are **not redistributed through this repository**. Surveillance data were accessed and was made possible through the Vivli AMR Register.

## Use of Generative AI Statement

Generative AI tools, including OpenAI ChatGPT (GPT-5.6) and Anthropic Claude, were used. They provided moderate assistance with drafting analytical Python and R code under the specific direction of the research team, as well as minor assistance with grammar, punctuation, and writing style. The tools were not provided access to the underlying AMR datasets. All AI-assisted outputs and code were independently reviewed, tested, interpreted, and revised by the research team. All aspects of the research study, including research questions, major methodological decisions, interpretation, and conclusions were developed by the research team.
