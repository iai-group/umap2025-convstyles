# ArXivDigest Assistant (ADA)

This repository contains the ArXivDigest Assistant (ADA), a scholarly conversational assistant developed as part of a study on the effect of conversational styles in conversational recommender systems. ADA is designed to manage dialogue, generate recommendations, and handle user interactions within the context of scientific literature discovery.

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

## Demo

<video width="640" height="360" controls>
  <source src="docs/assets/ada-demo.mp4" type="video/mp4">
  Your browser does not support the video tag. You can download the video [here](docs/assets/ada-demo.mp4).
</video>

## Installation

1. **Clone the repository:**

   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

3. **Set up configuration:**

    Create the configuration in config/config.yaml.


## Running the Application

Run the main module to start the server:

```sh
python ada.main -p <port>
```

Additional command-line options are available, as defined in `main.py`.

## Citation

TBD