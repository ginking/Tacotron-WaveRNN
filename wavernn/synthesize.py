import os

import numpy as np
import torch
from datasets.audio import save_wavernn_wav
from infolog import log
from tqdm import tqdm
from wavernn.model import WaveRNN


def synthesize(args, input_dir, output_dir, checkpoint_path, hparams):
    # device
    device = torch.device('cuda' if args.use_cuda else 'cpu')

    # Initialize Model
    model = WaveRNN(hparams.wavernn_bits, hparams.hop_size, hparams.num_mels, device).to(device)

    # Load Model
    if args.use_cuda:
        checkpoint = torch.load(checkpoint_path)
    else:
        checkpoint = torch.load(checkpoint_path, map_location=lambda storage, loc: storage)

    log('Loading model from {}'.format(checkpoint_path))
    model.load_state_dict(checkpoint['state_dict'])

    # Synth from Mels to Wave
    filenames = [f for f in sorted(os.listdir(input_dir)) if f.endswith('.npy')]
    for i, filename in tqdm(enumerate(filenames)):
        mel = np.load(os.path.join(input_dir, filename)).T
        save_wavernn_wav(model.generate(mel), f'{output_dir}/{i}_generated.wav', hparams.sample_rate)


def wavernn_synthesize(args, hparams, checkpoint_path):
    input_dir = os.path.join(args.base_dir, 'tacotron_output', 'eval')
    output_dir = os.path.join(args.base_dir, 'wavernn_output')
    os.makedirs(output_dir, exist_ok=True)

    synthesize(args, input_dir, output_dir, checkpoint_path, hparams)
