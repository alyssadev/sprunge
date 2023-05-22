Command line pastebin for google app-engine, in use at [pastesha.re](https://mxbin.io).

### Install

- [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install).
  - `sudo apt install google-cloud-cli google-cloud-cli-app-engine-python`
- Run gcloud init to get started
  - `gcloud init`
- Run locally
  - `gcloud auth application-default login`
  - `flask --app main run`
- Deploy for testing
  - `gcloud app deploy --no-promote`
- Deploy for production
  - `gcloud app deploy`
