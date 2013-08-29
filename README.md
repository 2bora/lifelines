lifelines
=======


This will be a library for survival analysis in Pyth---

Currently, the libary can only create arti---

...articial datasets. That e---

...okay, I get it: Lifelines. 



### Just show me the example!

    from matplotlib import pylab as plt
    from lifelines import *

    n_ind = 4 # how many lifetimes do we observe
    n_dim = 5 # the number of covarites to generate. 
    t = np.linspace(0,40,400)

    hz, coefs, covart = generate_hazard_rates(n_ind, n_dim, t, model="aalen")
    # you're damn right these are dataframes

    hz.plot()

![Hazard Rates](http://i.imgur.com/O8Og76O.png)

    sv = construct_survival_curves(hz, t )
    sv.plot() #moar dataframes

![Survival Curves](http://i.imgur.com/jWu3CM9.png)

    #using the hazard curves, we can sample from survival times.
    rv = generate_random_lifetimes(hz, t, 50 )
    print rv
    array([[ 9.4235589 ,  3.60902256,  3.0075188 ,  0.60150376],
           [ 1.00250627,  3.20802005,  0.70175439,  0.30075188],
           [ 5.71428571,  8.02005013,  5.41353383,  0.30075188],
           ...,
           [ 3.70927318,  4.41102757,  3.30827068,  0.30075188],
           [ 1.80451128,  1.5037594 ,  0.30075188,  0.40100251],
           [ 1.40350877,  1.5037594 ,  0.80200501,  0.10025063]])

    surival_times = rv[:,0][:,None]  

    #estimation is clean and built to resemble scikit learn's api.
    kmf = KaplanMeierFitter()
    kmf.fit(survival_times)
    kfm.survival_function_.plot()

![KaplanMeier estimate](http://i.imgur.com/aztRkvl.png)

    naf = NelsonAalenFitter()
    naf.fit(survival_times)
    naf.cumulative_hazard_.plot()

![NelsonAalen](http://i.imgur.com/xA9OBFN.png)