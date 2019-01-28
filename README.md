# Campaign Measurement Module
Useful functions for campaign measurement

### bound-by-p

Limits some metric of your data set by the p-th percentile.
Useful to handle outliers in spend data. If *control* is provided with a valid column name, then the action is performed for each data segments.

### create-bootstrap-mean

Bootstrapped estimation of mean of some metric.  


### get-ci

Assumes the input is a vector with normal distribution and returns the *alpha*confidence interval.


### test-of-prop

Two sampled test of proportions to measure if two groups have significantly different success rate


### measure-incremental-spend

Measures the incremental spend of a *test* audience versus the expected spend calculated from the spend of a *control* group

Can be used for any non-binomial metric. [Read This](https://tawsifkhan.github.io/files/Bootstrapping_git.pdf)


### measure-incremental-binomial-var

Measures the incremental rate of success of a *test* audience versus the expected success rate calculated from the success rate of a *control* group
