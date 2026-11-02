"""Receive-only template adapted from Lab 00, p. 10. NOT the original session file.

No transmission is performed. Install pyadi-iio, numpy and matplotlib in the
hardware environment. This template has not been run against the lab device.
Optional new captures are saved as little-endian complex64 (.cf32); preserve
their JSON sidecar. Values in a new capture must never be attributed to the
earlier session. The FFT magnitude is uncalibrated, not dBm or a PSD estimate.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--save-dir', type=Path, help='Save a NEW I/Q capture here')
    parser.add_argument('--team', default='teamID', help='ASCII team identifier')
    args = parser.parse_args()
    if not args.team or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in args.team):
        parser.error('--team must contain ASCII letters, digits, - or _ only')

    import adi
    import numpy as np
    import matplotlib.pyplot as plt

    sdr = adi.Pluto('ip:192.168.1.10')
    try:
        sdr.sample_rate = int(2.6e6)
        sdr.rx_lo = int(945e6)
        sdr.rx_rf_bandwidth = int(2e6)
        sdr.gain_control_mode_chan0 = 'manual'
        sdr.rx_hardwaregain_chan0 = 20  # Receive with antenna; course maximum 30 dB
        sdr.rx_buffer_size = 4096
        x = np.asarray(sdr.rx())
        fs, fc = int(sdr.sample_rate), int(sdr.rx_lo)
        print('samples:', x.shape, ' sample_rate:', fs)
        if args.save_dir:
            args.save_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc)
            name = f'{args.team}_lab00_{fc}_{fs}_20_{stamp:%Y%m%dT%H%M%S%fZ}'
            path = args.save_dir / (name + '.cf32')
            with path.open('xb') as stream:
                np.asarray(x, dtype='<c8').tofile(stream)
            metadata = {
                'capture_utc': stamp.isoformat(), 'uri': 'ip:192.168.1.10',
                'fc_hz': fc, 'fs_hz': fs, 'rx_rf_bandwidth_hz': int(sdr.rx_rf_bandwidth),
                'gain_mode': 'manual', 'gain_db': float(sdr.rx_hardwaregain_chan0),
                'samples': int(x.size), 'datatype': 'complex64 little-endian',
                'session': 'NEW capture; not evidence of the earlier lab session',
            }
            path.with_suffix('.json').write_text(json.dumps(metadata, indent=2))
            print('Saved NEW capture:', path)
        spectrum = np.fft.fftshift(np.fft.fft(x * np.hanning(x.size)))
        f = (fc + np.fft.fftshift(np.fft.fftfreq(x.size, 1 / fs))) / 1e6
        plt.plot(f, 20 * np.log10(np.abs(spectrum) + 1e-9), linewidth=0.8)
        plt.xlabel('Frequency (MHz)')
        plt.ylabel('Uncalibrated FFT magnitude (dB)')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    finally:
        sdr.rx_destroy_buffer()


if __name__ == '__main__':
    main()
