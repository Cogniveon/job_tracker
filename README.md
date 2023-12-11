# Job Tracker for Cambridge Digital Twins Project

A simple application that runs inference on images to detect lab samples at the Cambridge University Hospitals 
histopathology lab.

# Setup - Local

For training models:
- `cd job_tracker`
- Check the dataset folder structure:

```
./job_tracker/dataset
├── train/
│   ├── images/...
│   └── labels/...
├── val/
│   ├── images/...
│   └── labels/...
```
- Run `python train.py` (see train.py for editing any hyperparams)

# Setup - Docker

- Run `docker compose up -d` to start the CherryPy application and the caddy server.
- Visit https://localhost
