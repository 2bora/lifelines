lifelines
=======
 


### Just show me the examples!

    from matplotlib import pylab as plt
    from lifelines.generate_datasets import *
    from lifelines.estimation import *

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


### Censorship events

    from matplotlib import pylab as plt
    from lifelines.generate_datasets import *
    from lifelines.estimation import *
    t = np.linspace(0,40,1000)
    hz, coefs, covart = generate_hazard_rates(1, 2, t, model="aalen")

    #generate random lifetimes with uniform censoring. C is the boolean of censorship
    T, C = generate_random_lifetimes(hz, t, size=750, censor=True )

    kmf = KaplanMeierFitter()
    kmf.fit(T,t,censorship=C)
    ax = kmf.survival_function_.plot()

    sv = construct_survival_curves(hz,t) 
    sv.plot(ax=ax) 

    ##what if we had ignored the censorship events?
    kmf.fit(T,t, column_name="KM-estimate without factoring censorship")
    kmf.survival_function_.plot(ax=ax)

    plt.show()

![SVest](http://i.imgur.com/jYm911Z.png)

