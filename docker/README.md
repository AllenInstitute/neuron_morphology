docker
======
We use these images for our production pipeline. `Dockerfile.base` is a longstanding root image (separated to speed up builds). `Dockerfile.deploy` is the per-build image.

To build these, `cd` to the neuron_morphology root directory and run:
```
docker build . -f docker/Dockerfile.<something> -t neuron_morphology/<something>:<version>
```