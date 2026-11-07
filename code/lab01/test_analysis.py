"""Algorithm checks on synthetic signals; never used as lab observations."""
import unittest
import numpy as np
from analyze_iq import spectra, measure_roi, tone_estimate, burst_envelope
class AnalysisTest(unittest.TestCase):
    def test_welch_parseval_and_all_sample_waterfall(self):
        rng=np.random.default_rng(14);x=(rng.normal(size=18001)+1j*rng.normal(size=18001))/np.sqrt(2)
        avg,hold,wf,edges,nwin,tail=spectra(x,100000,1024,max_rows=10)
        self.assertAlmostEqual(avg.sum()*100000/1024,np.mean(abs(x)**2),delta=.03)
        self.assertEqual(edges[-1],len(x)/100000);self.assertLessEqual(len(wf),10)
        self.assertEqual(nwin,1+(len(x)-1024)//512)
        self.assertTrue(np.all(hold>=avg));self.assertEqual(tail,(len(x)-1024)%512)
    def test_positive_and_negative_offbin_tone(self):
        fs=2600000;fc=434000000;n=65536;t=np.arange(n)/fs
        for freq in [250123.4,-250123.4]:
            x=np.exp(2j*np.pi*freq*t)
            r=tone_estimate(x,fs,fc,{'f_tx_hz':freq,'search_hz':[fc+freq-500,fc+freq+500]})
            self.assertLess(abs(r['error_hz']),1.0)
    def test_flat_obw99(self):
        f=np.arange(1000.)*100;psd=np.ones(1000)
        r=measure_roi(f,psd,psd,{'id':'flat','roi_hz':[0,99900],'x_db':6},100)
        self.assertAlmostEqual(r['obw99_hz'],99000,places=5)
        self.assertTrue(r['bx_clipped'])
    def test_gaussian_xdb_width(self):
        f=np.arange(-5000,5001,10.);p=np.exp(-.5*(f/500)**2)
        r=measure_roi(f,p,p,{'id':'gauss','roi_hz':[-5000,5000],'x_db':6},10)
        expected=2*500*np.sqrt(2*np.log(10)*.6)
        self.assertAlmostEqual(r['bx_hz'],expected,delta=1)
    def test_burst_duration_and_right_censoring(self):
        fs=100000;n=10000;t=np.arange(n)/fs
        env=((t>=.02)&(t<.03))|((t>=.08)&(t<.1))
        x=env*np.exp(2j*np.pi*5000*t)
        _,edges,r=burst_envelope(x,fs,1000000,{'center_hz':1005000,'bandwidth_hz':10000,'threshold_db_relative':-6,'warmup_s':.002,'step_s':.0001})
        self.assertEqual(len(r['events']),2)
        self.assertAlmostEqual(r['events'][0]['duration_s'],.01,delta=.0003)
        self.assertTrue(r['events'][-1]['right_censored']);self.assertEqual(edges[-1],.1)
if __name__=='__main__':unittest.main()
