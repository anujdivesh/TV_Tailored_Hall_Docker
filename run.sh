#!/bin/bash

#docker run -v /mnt/DATA/QuickSurge-docker/QuickSurge:/QuickSurge --rm --cpuset-cpus="0-19" quick-surge /bin/bash -c ". /opt/miniconda/bin/activate; cd /QuickSurge/Python_Codes; python main_IDA_PDNA_StormSurge.py"


docker run -v /mnt/DATA/TUV/tailored-report-tv:/Tailored --rm --cpuset-cpus="17-32" tailored-report-v1 /bin/bash -c ". /opt/miniconda/bin/activate; cd /Tailored/codes; python main_run_operational.py"

echo "Model run Successful!"
