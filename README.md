# Should We Tailor the Talk? Understanding the Impact of Conversational Styles on Preference Elicitation in Conversational Recommender Systems

This repository provides resources developed within the following article [[PDF](https://arxiv.org/abs/TODO_FIX_LINK)] (To be published in UMAP 2025):

> I. Kostric, K. Balog, U. Gadiraju. **Should We Tailor the Talk? Understanding the Impact of Conversational Styles on Preference Elicitation in Conversational Recommender Systems** In: Proceedings of the 33rd ACM Conference on User Modeling, Adaptation and Personalization (UMAP ’25), June 2025. [DOI: 10.1145/3699682.3728353](https://doi.org/10.1145/3699682.3728353)

## Summary

Conversational recommender systems (CRSs) provide users with an interactive means to express preferences and receive real-time personalized recommendations. The success of these systems is heavily influenced by the preference elicitation process.
While existing research mainly focuses on what questions to ask during preference elicitation, there is a notable gap in understanding what role broader interaction patterns---including tone, pacing, and level of proactiveness---play in supporting users in completing a given task. This study investigates the impact of different conversational styles on preference elicitation, task performance, and user satisfaction with CRSs.
We conducted a controlled experiment in the context of scientific literature recommendation, contrasting two distinct conversational styles---*high involvement* (fast-paced, direct, and proactive with frequent prompts) and *high considerateness* (polite and accommodating, prioritizing clarity and user comfort)---alongside a flexible experimental condition where users could switch between the two.
Our results indicate that adapting conversational strategies based on user expertise and allowing flexibility between styles can enhance both user satisfaction and the effectiveness of recommendations in CRSs. Overall, our findings hold important implications for the design of future CRSs.

## Overview

The code is split into 2 parts: server and client, which are adapted from [ArxivDigest Assistant](https://github.com/iai-group/arxivdigest-assistant) and [ChatWidget](https://github.com/iai-group/ChatWidget). Server code includes the following components:

  - **Agent & Dialogue Management:** Implemented in [agent](code/server/ada/agent/agent.py) and [dialogue_manager](ada/agent/dialogue_manager/dialogue_manager.py).
  - **User Model:** Managed in [user model](code/server/ada/external/user_model/ada_user_model.py).
  - **Configuration:** Defined in [config](code/server/config/config.yaml).
  - **Main Entry Point:** Located [here](code/server/ada/main.py).

Client code is based on react and should be built using npm. The client code is located in the `code/client` directory.

## Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/iai-group/umap2025-convstyles
   cd umap2025-convstyles
   ```

3. **Set up configuration:**

    Create the configuration in code/server/config/config.yaml.

4. **build the client:**

   ```sh
   cd code/client
   npm install
   npm run build
   ```

## Running the Application

Run the main module to start the server:

```sh
python -m code.server -p <port>
```

This will start a local server on `http://localhost:5000`.

Run the client:

```sh
cd code/client
npm start
```

This will start a local server on `http://localhost:3000`. You can access the application by navigating to this URL in your web browser.

## Citation

If you use the resources presented in this repository, please cite:

TBD

## Contact

Should you have any questions, please contact Ivica Kostric at [ivica.kostric@uis.no](mailto:ivica.kostric@uis.no).
