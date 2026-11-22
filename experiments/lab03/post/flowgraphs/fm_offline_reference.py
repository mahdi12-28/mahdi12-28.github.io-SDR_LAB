#!/usr/bin/env python3
"""Reconstructed GNU Radio 3.10 reference, based on the supplied manual.

This is not the original session flowgraph. It uses only files, no RF hardware.
RX input: little-endian complex64 after translation to baseband at 240 kS/s.
RX outputs: little-endian float32 audio at 48 kS/s, before playback normalization.
"""
import argparse, math
from pathlib import Path
from gnuradio import gr, blocks, analog, filter
from gnuradio.filter import firdes

class Receiver(gr.top_block):
    def __init__(self,input_path,outdir,dev=75000,pll_bw=.15,audio_bw=15000,tau=75e-6):
        super().__init__('Lab03 offline FM comparison')
        fq=240000;fa=48000;gain=fq/(2*math.pi*dev)
        source=blocks.file_source(gr.sizeof_gr_complex,str(input_path),False)
        bw=min(2*(dev+audio_bw),200000)
        channel=filter.fir_filter_ccf(1,firdes.low_pass(1,fq,bw/2,bw/8))
        quad=analog.quadrature_demod_cf(gain)
        limit=min(2*math.pi*1.5*dev/fq,3.0)
        pll=analog.pll_freqdet_cf(pll_bw,limit,-limit)
        scale=blocks.multiply_const_ff(gain)
        self.connect(source,channel);self.connect(channel,quad);self.connect(channel,pll,scale)
        self.keep=[]
        for name,detector in [('quadrature',quad),('pll',scale)]:
            lp=filter.fir_filter_fff(5,firdes.low_pass(1,fq,audio_bw,.25*audio_bw+250))
            dc=blocks.dc_blocker_ff(512,True);de=analog.fm_deemph(fa,tau)
            sink=blocks.file_sink(gr.sizeof_float,str(outdir/(name+'_48k.f32')),False)
            self.keep.extend([lp,dc,de,sink]);self.connect(detector,lp,dc,de,sink)

class Transmitter(gr.top_block):
    def __init__(self,path,seconds=5,fm=1000,dev=5000):
        super().__init__('Lab03 file-only FM tone reference')
        fq=240000
        source=analog.sig_source_f(fq,analog.GR_COS_WAVE,fm,1,0)
        head=blocks.head(gr.sizeof_float,int(seconds*fq))
        mod=analog.frequency_modulator_fc(2*math.pi*dev/fq)
        amp=blocks.multiply_const_cc(.5)
        sink=blocks.file_sink(gr.sizeof_gr_complex,str(path),False)
        self.connect(source,head,mod,amp,sink)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['rx','tx'])
    ap.add_argument('path',type=Path);ap.add_argument('--outdir',type=Path,default=Path('offline_audio'))
    ap.add_argument('--dev',type=float,default=5000);ap.add_argument('--fm',type=float,default=1000)
    ap.add_argument('--seconds',type=float,default=5);ap.add_argument('--pll-bw',type=float,default=.15)
    ap.add_argument('--audio-bw',type=float,default=15000);args=ap.parse_args()
    if args.mode=='rx':
        args.outdir.mkdir(exist_ok=True,parents=True)
        graph=Receiver(args.path,args.outdir,args.dev,args.pll_bw,args.audio_bw)
    else:graph=Transmitter(args.path,args.seconds,args.fm,args.dev)
    graph.run()

if __name__=='__main__':main()
