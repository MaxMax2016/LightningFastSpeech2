import torch
import numpy as np
import torch.nn.functional as F


# clip_val 1e-7, log10=False
# todo: make configureable without discarding cache
def dynamic_range_compression(x, C=1, clip_val=1e-6, log10=True):
    if log10:
        return torch.log10(torch.clamp(x, min=clip_val) * C)
    else:
        return torch.log(torch.clamp(x, min=clip_val) * C)


def dynamic_range_decompression(x, C=1):
    return torch.exp(x) / C


def smooth(y, box_pts):
    box = np.ones(box_pts) / box_pts
    y_smooth = np.convolve(y, box, mode="same")
    return y_smooth


def remove_outliers(values):
    values = np.array(values)
    p25 = np.percentile(values, 25)
    p75 = np.percentile(values, 75)
    lower = p25 - 1.5 * (p75 - p25)
    upper = p75 + 1.5 * (p75 - p25)
    normal_indices = np.logical_and(values > lower, values < upper)
    values[~normal_indices] = 0
    return values


def get_alignment(tier, sampling_rate, hop_length):
    sil_phones = ["sil", "sp", "spn", ""]

    phones = []
    durations = []
    start_time = 0
    end_time = 0
    end_idx = 0
    counter = 0
    for t in tier._objects:
        s, e, p = t.start_time, t.end_time, t.text

        # add silence phone if timestamp gap occurs
        if s != end_time and len(phones) > 0:
            phones.append("sil")
            durations.append(
                int(
                    np.round(s * sampling_rate / hop_length)
                    - np.round(end_time * sampling_rate / hop_length)
                )
            )

        # Trim leading silences
        if phones == []:
            if p in sil_phones:
                continue
            else:
                start_time = s

        if p not in sil_phones:
            # For ordinary phones
            phones.append(p)
            end_time = e
            end_idx = len(phones)
        else:
            # For silent phones
            phones.append("sil")
            end_time = e

        durations.append(
            int(
                np.round(e * sampling_rate / hop_length)
                - np.round(s * sampling_rate / hop_length)
            )
        )

    # Trim tailing silences
    phones = phones[:end_idx]
    durations = durations[:end_idx]

    true_dur = int(np.ceil(((end_time - start_time) * sampling_rate - 1) / hop_length))
    pred_dur = sum(durations)
    if pred_dur != true_dur:
        durations[-1] += true_dur - pred_dur

    return phones, durations, start_time, end_time
