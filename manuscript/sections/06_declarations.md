## Declarations

**Funding.** No funding was received for conducting this study.

**Competing interests.** The author declares no competing interests.

**Ethics approval, consent to participate, consent for publication.** Not applicable: this is a purely computational study involving no human participants, animals, or personal data.

**Data availability.** All simulation outputs underlying the figures and tables (`results/data/*.csv`, with the parameter set of each experiment in the accompanying `.meta.json` files) are provided as Supplementary Information and archived in the code repository. No restrictions apply.

**Code availability.** The model, all experiment, figure and table scripts, and the regression tests are available at https://github.com/MinaSaied23/ephaptic-crosstalk. `python run_all.py` regenerates every result, figure and table, and `python -m pytest` runs the tests. The code is written in Python 3.11 (RRID:SCR_008394) with NumPy 1.26.4 (RRID:SCR_008633), SciPy 1.13.0 (RRID:SCR_008058), pandas 2.2.2 (RRID:SCR_018214) and Matplotlib 3.8.4 (RRID:SCR_008624). The banded solves use the LAPACK routines `dgbtrf` and `dgbtrs` through SciPy. No biological resources were used in this study.

**Use of AI tools.** [Author to confirm or edit before submission.] An AI assistant (Claude, Anthropic) was used to help re-implement the numerical solver, run the re-analysis, and draft and edit the revised text. The author checked all code, results and text and takes full responsibility for the content.

**Author contributions.** Mina Saied Attia Rizk: conceptualization, methodology, software, validation, formal analysis, investigation, data curation, writing (original draft, review and editing), visualization.
