#!/bin/bash

echo "Updating system and installing Python packages..."

sudo apt update && sudo apt install -y python3-pip
python3 -m venv myenv
source myenv/bin/activate

pip install --upgrade pip
pip install datasets pandas matplotlib seaborn scikit-learn nltk gensim transformers joblib

echo "Setup complete."

