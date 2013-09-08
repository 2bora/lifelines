#test statistics
import numpy as np
import pandas as pd 
import pdb

def two_sample_test(event_times_A, event_times_B, censorship_A = None, censorship_B=None, t_0 = -1):
  """
  See Survival and Event Analysis, page 108. This implicitly uses the log-rank weights.

  event_times_X: a (nx1) array of event times (deaths,...) for the population.
  t_0: the period under observation, -1 for all time.

  """

  if censorship_A is None:
    censorship_A = np.ones((event_times_A.shape[0], 1))  
  if censorship_B is None:
    censorship_B = np.ones((event_times_B.shape[0], 1))

  if t_0 == -1: 
    t_0 = np.max([event_times_A.max(), event_times_B.max()])
  
  event_times_AB = dataframe_from_events_censorship( np.append(event_times_A,event_times_B),
                                                     np.append( censorship_A, censorship_B) )

  event_times_A = dataframe_from_events_censorship( event_times_A, censorship_A)
  event_times_B = dataframe_from_events_censorship( event_times_B, censorship_B)

  N_dot = event_times_AB[["observed"]].cumsum()
  Y_dot = event_times_AB["removed"].sum() - event_times_AB["removed"].cumsum()
  Y_1 = event_times_A["removed"].sum() - event_times_A["removed"].cumsum()
  Y_2 = event_times_B["removed"].sum() - event_times_B["removed"].cumsum()

  v = 0
  v_sq = 0
  y_1 = Y_1.ix[0]
  y_2 = Y_2.ix[0]
  for t, n_t in N_dot.ix[N_dot.index<=t_0].itertuples():
    try:
      y_1 = Y_1.loc[t]
    except KeyError:
      pass      
    try:  
      y_2 = Y_2.loc[t]
    except KeyError:
      pass
    y_dot = Y_dot.loc[t]
    if y_dot != 0:
      v += 1.*y_1/y_dot
      v_sq += (1.*y_2*y_1)/(y_dot**2)
  E_1 = v
  N_1 = event_times_A[["observed"]].sum()[0]
  Z_1 = N_1 - E_1
  U = Z_1/np.sqrt(v_sq)
  return U


def dataframe_from_events_censorship(event_times, censorship=None):
    """Accepts:
        event_times: (n,1) array of event times 
        censorship: if not None, (n,1) boolean array, 1 if observed event, 0 is censored
    """
    df = pd.DataFrame( event_times, columns=["event_at"] )
    df["removed"] = 1

    if censorship is None:
       censorship = np.ones_like(event_times, dtype=bool) #why boolean?
    else:
       censorship = censorship.copy()

    df["observed"] = censorship
    event_times = df.groupby("event_at").sum().sort_index()
    return event_times