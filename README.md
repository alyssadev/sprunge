Command line pastebin for google app-engine, in use at [pb.aly.pet](https://pb.aly.pet). Based on work by [beledouxdenis](https://github.com/beledouxdenis) and [mxroute](https://github.com/mxroute).

### Install

- [Install the gcloud CLI](https://cloud.google.com/sdk/docs/install).
  - `sudo apt install google-cloud-cli google-cloud-cli-app-engine-python`
- Run gcloud init to get started
  - `gcloud init`
- Configure sprunge
  - `git clone https://github.com/alyssadev/sprunge && cd sprunge`
  - `vim main.py` to update PROJECT\_ID and URL
  - `export SPRUNGE_TOKEN="Bearer $(openssl rand -hex 16)" && echo $SPRUNGE_TOKEN`
  - `gcloud secrets create sprunge-token --data-file=- --replication-policy=automatic <<<$SPRUNGE_TOKEN`
- Run locally
  - `gcloud auth application-default login`
  - `virtualenv .env`
  - `source .env/bin/activate`
  - `pip3 install -r requirements.txt`
  - `flask --app main run`
- Deploy for testing
  - `gcloud app deploy --no-promote`
- Deploy for production
  - `gcloud app deploy`
