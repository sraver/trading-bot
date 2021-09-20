wget -O inst_conda.sh "https://repo.anaconda.com/archive/Anaconda3-2020.11-Linux-x86_64.sh" \
  && /bin/bash inst_conda.sh -b \
  && rm inst_conda.sh \
  && ~/anaconda3/bin/conda init \
  && source ~/.bashrc \
  && conda create -n quantra python=3.6.8 -y \
  && conda activate quantra
