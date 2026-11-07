import math
import os
import time

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):
    """Record raw complex64 IQ samples on a record-checkbox rising edge."""

    def __init__(self, team='Team-00', lab=1, fc=100e6, fs=2.6e6,
                 gain=0.0, record=False, max_seconds=5.0, folder='.'):
        gr.sync_block.__init__(
            self,
            name='SDR Lab IQ Recorder',
            in_sig=[np.complex64],
            out_sig=None
        )
        # Matching names let GRC update these values at runtime.
        self.team = team
        self.lab = lab
        self.fc = fc
        self.fs = fs
        self.gain = gain
        self.record = record
        self.max_seconds = max_seconds
        self.folder = folder

        # No files or folders are created while GRC inspects the block.
        self._state = 'IDLE'
        self._file = None
        self._settings = None
        self._written = 0
        self._limit = 0

    def _begin(self, settings):
        fc, fs, gain = settings
        duration = float(self.max_seconds)
        if not all(math.isfinite(v) for v in settings):
            raise ValueError('fc, fs and gain must be finite numbers')
        if fs <= 0 or not math.isfinite(duration) or duration < 0:
            raise ValueError('fs must be positive; max_seconds must be finite and nonnegative')

        self._limit = math.floor(duration * fs)
        stamp = time.strftime('%Y%m%dT%H%M%S')
        filename = (
            f'{self.team}_lab{int(self.lab):02d}_'
            f'{int(round(fc))}_{int(round(fs))}_{gain:.1f}_{stamp}.cf32'
        )
        folder = os.path.expanduser(os.fspath(self.folder))
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
        # Exclusive creation protects an existing recording with the same name.
        self._file = open(path, 'xb')
        self._settings = settings
        self._written = 0
        self._state = 'RECORDING'
        print(f'[REC] start {filename}', flush=True)

    def _finish(self, reason, next_state):
        if self._file is not None:
            self._file.close()
            self._file = None
            seconds = self._written / self._settings[1]
            print(
                f'[REC] stop {self._written} samples = '
                f'{seconds:.2f} s ({reason})',
                flush=True
            )
        self._state = next_state

    def work(self, input_items, output_items):
        samples = input_items[0]
        requested = bool(self.record)
        settings = (float(self.fc), float(self.fs), float(self.gain))

        if not requested:
            self._finish('record unchecked', 'IDLE')
            return len(samples)

        if self._state == 'WAIT':
            return len(samples)

        if self._state == 'IDLE':
            self._begin(settings)
        elif settings != self._settings:
            self._finish('fc/fs/gain changed', 'WAIT')
            return len(samples)

        # Trim the last chunk to reach the exact sample limit.
        count = min(len(samples), self._limit - self._written)
        if count > 0:
            np.asarray(samples[:count], dtype=np.complex64).tofile(self._file)
            self._written += count

        if self._written == self._limit:
            self._finish('max_seconds reached', 'WAIT')

        # A sink consumes the entire input, including samples not recorded.
        return len(samples)

    def stop(self):
        self._finish('flowgraph stopped', 'IDLE')
        return True
