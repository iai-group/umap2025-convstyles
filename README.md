# Should We Tailor the Talk? Understanding the Impact of Conversational Styles on Preference Elicitation in Conversational Recommender Systems


This repository provides resources developed within the following article [[PDF](https://arxiv.org/abs/TODO_FIX_LINK)]:

> I. Kostric, K. Balog, U. Gadiraju. **Should We Tailor the Talk? Understanding the Impact of Conversational Styles on Preference Elicitation in Conversational Recommender Systems** In: 33rd ACM Conference on User Modeling, Adaptation and Personalization (UMAP ’25), June 16–19, 2025, New York City, NY, USA. ACM, New York, NY, USA, 10 pages. [DOI: 10.1145/3699682.3728353](https://doi.org/10.1145/3699682.3728353)


## Summary

Conversational recommender systems (CRSs) provide users with an interactive means to express preferences and receive real-time personalized recommendations. The success of these systems is heavily influenced by the preference elicitation process.
While existing research mainly focuses on what questions to ask during preference elicitation, there is a notable gap in understanding what role broader interaction patterns---including tone, pacing, and level of proactiveness---play in supporting users in completing a given task. This study investigates the impact of different conversational styles on preference elicitation, task performance, and user satisfaction with CRSs.
We conducted a controlled experiment in the context of scientific literature recommendation, contrasting two distinct conversational styles---*high involvement* (fast-paced, direct, and proactive with frequent prompts) and *high considerateness* (polite and accommodating, prioritizing clarity and user comfort)---alongside a flexible experimental condition where users could switch between the two.
Our results indicate that adapting conversational strategies based on user expertise and allowing flexibility between styles can enhance both user satisfaction and the effectiveness of recommendations in CRSs. Overall, our findings hold important implications for the design of future CRSs.

## Overview

ADA includes the following components:

  - **Agent & Dialogue Management:** Implemented in [ada/agent/agent.py](ada/agent/agent.py) and [ada/agent/dialogue_manager/dialogue_manager.py](ada/agent/dialogue_manager/dialogue_manager.py).
  - **User Model:** Managed in [ada/external/user_model/ada_user_model.py](ada/external/user_model/ada_user_model.py).
  - **Configuration:** Defined in [config/config.yaml](config/config.yaml).
  - **Main Entry Point:** Located in [ada/main.py](ada/main.py).

## Features

  - Conversational preference elicitation with support for multiple dialogue styles.
  - Recommendation module for retrieving scientific literature.
  - Configurable dialogue management and user interaction flow.

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/iai-group/umap2025-convstyles
   cd umap2025-convstyles
   ```

3. **Set up configuration:**

    Create the configuration in config/config.yaml.

## Running the Application

Run the main module to start the server:

```sh
python -m ada.main -p <port>
```

Additional command-line options are available, as defined in `main.py`.

## Citation

If you use the resources presented in this repository, please cite:

```
@inproceedings{Kostric:2025:UMAP,
  author =    {Ivica Kostric, Krisztian Balog, Ujwal Gadiraju},
  title =     {Should We Tailor the Talk? Understanding the Impact of Conversational Styles on Preference Elicitation in Conversational Recommender Systems},
  booktitle = {33rd ACM Conference on User Modeling, Adaptation and Personalization (UMAP ’25)},
  series =    {UMAP '25},
  year =      {2025},
  doi =       {10.1145/3699682.3728353},
  publisher = {ACM}
}
```

## Contact

Should you have any questions, please contact Ivica Kostric at [ivica.kostric@uis.no](mailto:ivica.kostric@uis.no).
