import librosa
import numpy as np

np.random.seed(0)


def load_wav(audio_filepath, sr, min_dur_sec=5):
    audio_data, fs = librosa.load(audio_filepath, sr=16000)
    len_file = len(audio_data)

    if len_file <= int(min_dur_sec * sr):
        dummy = np.zeros((1, int(min_dur_sec * sr) - len_file))
        extened_wav = np.concatenate((audio_data, dummy[0]))
    else:
        extened_wav = audio_data
    return extened_wav


def lin_mel_from_wav(wav, hop_length, win_length, n_mels):
    linear = librosa.feature.melspectrogram(
        wav, n_mels=n_mels, win_length=win_length, hop_length=hop_length
    )  # linear spectrogram
    return linear.T


def lin_spectogram_from_wav(wav, hop_length, win_length, n_fft=512):
    linear = librosa.stft(
        wav, n_fft=n_fft, win_length=win_length, hop_length=hop_length
    )  # linear spectrogram
    return linear.T


def feature_extraction(
    filepath,
    sr=16000,
    min_dur_sec=4,
    win_length=400,
    hop_length=160,
    n_mels=40,  # W0613: Unused argument 'n_mels' (unused-argument)
    spec_len=400,  # W0613: Unused argument 'spec_len' (unused-argument)
    mode="train",  # W0613: Unused argument 'mode' (unused-argument)
):
    audio_data = load_wav(filepath, sr=sr, min_dur_sec=min_dur_sec)
    linear_spect = lin_spectogram_from_wav(
        audio_data, hop_length, win_length, n_fft=512
    )
    mag, _ = librosa.magphase(linear_spect)  # magnitude
    mag_T = mag.T
    mu = np.mean(mag_T, 0, keepdims=True)
    std = np.std(mag_T, 0, keepdims=True)
    return (mag_T - mu) / (std + 1e-5)


def load_data(
    filepath,
    sr=16000,
    min_dur_sec=5,
    win_length=400,
    hop_length=160,
    n_mels=40,
    spec_len=400,
    mode="train",
):
    audio_data = load_wav(filepath, sr=sr, min_dur_sec=min_dur_sec)
    linear_spect = lin_spectogram_from_wav(
        audio_data, hop_length, win_length, n_fft=512
    )
    mag, _ = librosa.magphase(linear_spect)  # magnitude
    mag = np.log1p(mag)
    mag_T = mag.T

    if mode == "train":
        randtime = np.random.randint(0, mag_T.shape[1] - spec_len)
        spec_mag = mag_T[:, randtime : randtime + spec_len]
    else:
        spec_mag = mag_T

    # preprocessing, subtract mean, divided by time-wise var
    mu = np.mean(spec_mag, 0, keepdims=True)
    std = np.std(spec_mag, 0, keepdims=True)
    return (spec_mag - mu) / (std + 1e-5)
