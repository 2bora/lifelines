#estimation tests
import pandas as pd
import numpy as np
import pdb
from numpy.linalg import LinAlgError



def _additive_estimate(event_times, timeline, observed, additive_f, initial, column_name, nelson_aalen_smoothing=False):
    """

    nelson_aalen_smoothing: see section 3.1.3 in Survival and Event History Analysis

    """
    n = timeline.shape[0]
    _additive_estimate_ = pd.DataFrame(np.zeros((n,1)), index=timeline, columns=[column_name])
    _additive_var = pd.DataFrame(np.zeros((n,1)), index=timeline)

    N = event_times["removed"].sum()
    t_0 = event_times.index[0]
    _additive_estimate_.ix[(timeline<t_0)]=initial
    _additive_var.ix[(timeline<t_0)]=0

    v = initial
    v_sq = 0
    for t, removed, observed_deaths in event_times.itertuples():
        #pdb.set_trace()
        missing = removed - observed_deaths
        N -= missing
        if nelson_aalen_smoothing:
           v += np.sum([additive_f(N,i) for i in range(observed_deaths)])
        else:
           v += additive_f(N,observed_deaths)
           v_sq += (1.*observed_deaths/N)**2
        N -= observed_deaths
        _additive_estimate_.ix[ (t_0<timeline)*(timeline<=t) ] = v  
        _additive_var.ix[ (t_0<timeline)*(timeline<=t) ] = v_sq
        t_0 = t

    _additive_estimate_.ix[(timeline>t)]=v
    _additive_var.ix[(timeline>t)]=v_sq
    return _additive_estimate_, _additive_var


class NelsonAalenFitter(object):
    def __init__(self, alpha=0.95, nelson_aalen_smoothing=False):
        self.alpha = alpha
        self.nelson_aalen_smoothing = nelson_aalen_smoothing

    def additive_f(self, N,d ):
       #check it 0
       return 1.*d/N

    def fit(self, event_times, timeline=None, censorship=None, column_name='NA-estimate'):
        """
        event_times: an (n,1) array of times that the death event occured at 
        timeline: return the best estimate at the values in timelines (postively increasing)

        Returns:
          DataFrame with index either event_times or timelines (if not None), with
          values as the NelsonAalen estimate
        """
        #need to sort event_times
        df = pd.DataFrame( event_times, columns=["event_at"] )
        df["removed"] = 1

        if censorship is None:
           self.censorship = np.ones_like(event_times, dtype=bool)
        else:
           self.censorship = censorship.copy()

        df["observed"] = self.censorship
        self.event_times = df.groupby("event_at").sum().sort_index()

        if timeline is None:
           self.timeline = self.event_times.index.values.copy()
        else:
           self.timeline = timeline
        self.cumulative_hazard_, cumulative_sq_ = _additive_estimate(self.event_times, 
                                                                     self.timeline, self.censorship, 
                                                                     self.additive_f, 0, column_name,
                                                                     nelson_aalen_smoothing=self.nelson_aalen_smoothing )
        self.confidence_interval_ = self._bounds(cumulative_sq_)
        return

    def _bounds(self, cumulative_sq_):
        inverse_norm = { 0.95:1.65, 0.99:1.99 }
        try:
          coef = inverse_norm[self.alpha]
        except:
          pass
        df = pd.DataFrame( index=self.timeline)
        df["upper_bound_%.2f"%self.alpha] = self.cumulative_hazard_.values*np.exp(coef*np.sqrt(cumulative_sq_)/self.cumulative_hazard_.values )
        df["lower_bound_%.2f"%self.alpha] = self.cumulative_hazard_.values*np.exp(-coef*np.sqrt(cumulative_sq_)/self.cumulative_hazard_.values )
        return df

        

class KaplanMeierFitter(object):
   
  def __init__(self, alpha = 0.95):
       self.alpha = alpha

  def fit(self, event_times, timeline=None, censorship=None, column_name='KM-estimate'):
       """
       event_times: an (n,1) array of times that the death event occured at 
       timeline: return the best estimate at the values in timelines (postively increasing)
       censorship: an (n,1) array of booleans -- True if the the death was observed, False if the event 
          was lost (right-censored). Defaults all True if censorship==None
       Returns:
         DataFrame with index either event_times or timelines (if not None), with
         values as the NelsonAalen estimate
       """
       #need to sort event_times
       df = pd.DataFrame( event_times, columns=["event_at"] )
       df["removed"] = 1

       if censorship is None:
          self.censorship = np.ones_like(event_times, dtype=bool)
       else:
          self.censorship = censorship.copy()

       df["observed"] = self.censorship
       self.event_times = df.groupby("event_at").sum().sort_index()

       if timeline is None:
          self.timeline = self.event_times.index.values.copy()
       else:
          self.timeline = timeline
       log_surivial_function, cumulative_sq_ = _additive_estimate(self.event_times, self.timeline, 
                                                                  self.censorship, self.additive_f, 
                                                                  0, column_name )
       self.survival_function_ = np.exp(log_surivial_function)
       self.confidence_interval_ = self._bounds(cumulative_sq_)
       return self

  def additive_f(self,N,d):
      return np.log(1 - 1.*d/N)

  def _bounds(self, cumulative_sq_):
      inverse_norm = { 0.95:1.65, 0.99:1.99 }
      try:
        coef = inverse_norm[self.alpha]
      except:
        pass
      df = pd.DataFrame( index=self.timeline)
      "broken?"
      df["upper_bound_%.2f"%self.alpha] = self.survival_function_.values**(np.exp(coef*cumulative_sq_/np.log(self.survival_function_.values)))
      df["lower_bound_%.2f"%self.alpha] = self.survival_function_.values**(np.exp(-coef*cumulative_sq_/np.log(self.survival_function_.values)))
      #df["upper_bound_%.2f"%self.alpha] = self.survival_function_ + coef*np.sqrt(self.survival_function_*cumulative_sq_)
      #df["lower_bound_%.2f"%self.alpha] = self.survival_function_ - coef*np.sqrt(self.survival_function_*cumulative_sq_)
      return df



"""
hz, coef, covrt = generate_hazard_rates(2000, 4, t)
T,C = generate_random_lifetimes(hz,t, size = 1,censor = True)
aam.fit(T, X, censorship=C)
aam.cumulative_hazards_.plot()
coef.plot()

"""



class AalenAdditiveModel(object):

  def __init__(self,fit_intercept=True):
      self.fit_intercept = fit_intercept

  def fit(self, event_times, X, timeline = None, censorship=None):
      """currently X is a static (n,d) array

      event_times: (1,n) array of event times
      X: (n,d) the design matrix 
      timeline: (t,) timepoints in ascending order
      censorship: (1,n) boolean array of censorships: True if observed, False if right-censored.
                  By default, assuming all are observed.

      Fits: self.cumulative_hazards_: a (t,d+1) dataframe of cumulative hazard coefficients
            self.hazards_: a (t,d+1) dataframe of hazard coefficients

      """

      n,d = X.shape

      ix = event_times.argsort(1)[0,:]
      X_ = X[ix,:].copy() if not self.fit_intercept else np.c_[ X[ix,:].copy(), np.ones((n,1)) ]
      sorted_event_times = event_times[0,ix].copy()

      if censorship is None:
          observed = np.ones(n, dtype=bool)
      else:
          observed = censorship.reshape(n)

      if timeline is None:
          timeline = sorted_event_times
      t = timeline.shape[0]

      self.cumulative_hazards_ = pd.DataFrame(np.zeros((t,d+self.fit_intercept)), index=timeline)
      self.hazards_ = pd.DataFrame(np.zeros((t,d+self.fit_intercept)), index=timeline)
      t_0 = sorted_event_times[0]
      cum_v = np.zeros((d+self.fit_intercept,1))
      for i,time in enumerate(sorted_event_times):
          if not observed[i]:
            X[i,:] = 0
          try:
            V = np.dot(np.linalg.inv(np.dot(X_.T,X_)), X_.T)
          except LinAlgError:
            continue
          v = np.dot(V,basis(n,i))
          cum_v = cum_v + v
          self.cumulative_hazards_.ix[(t_0<timeline)*(timeline<=t)] = cum_v.T
          self.hazards_.ix[(t_0<timeline)*(timeline<=t)] = v.T
          X_[i,:] = 0
          t_0 = time
      return self

  def predict(self, X):
    """
    X: a (n,d) covariate matrix
    """
    n,d = X.shape
    X_ = X.copy() if not self.fit_intercept else np.c_[ X.copy(), np.ones((n,1)) ]
    return np.dot(self.cumulative_hazards_, X_.T)


def basis(n,i):
  x = np.zeros((n,1))
  x[i] = 1
  return x


