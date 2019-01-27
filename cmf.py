

# Function to limit a data set by it's p-th percentile
# Default percentile is 0.99
def bound_by_p(df,col, p=0.99):
    if col:
    	col_entries = df[col].unique()
    	for entry in col_entries:
        	val = df[df[col]==entry][col].quantile(p)
        	df.loc[(df[col] > val) & (df[by_control] == entry), col] = val
    else:
        val = df[col].quantile(p)
        df.loc[(df[col] > val), col] = val


# Bootstrap estimation of mean metric
def create_bootstrap_mean(data,iterations=100):
    bootstrap_mean = []
    error = None
    for i in range(1,iterations+1):
        sample = np.random.choice(data,size = data.shape[0],replace=True)
        bootstrap_mean.append(sample.mean())
    bootstrap_mean = np.asarray(bootstrap_mean)
    if len(bootstrap_mean) != iterations:
        error = 1
    return(bootstrap_mean,error)

# Confidence Interval
# Assumes normally distributed data
def get_ci(data,alpha=0.95):
    data = sorted(data)
    
    p = ((1.0-alpha)/2.0) * 100
    lower = np.percentile(data, p)
    
    p = (alpha+((1.0-alpha)/2.0)) * 100
    upper = np.percentile(data, p)
    return([lower,upper])

# Two-tailed test of proportions
def test_of_prop(control_success, control_size, test_success, test_size, p_val = 0.05):
    try:
        s1,n1,s2,n2 = control_success, control_size, test_success, test_size
        p1 = s1/n1
        p2 = s2/n2
        p = (s1+s2)/(n1+n2)
        z = (p2-p1)/ ((p*(1-p)*((1/n1)+(1/n2)))**0.5)
        if norm.cdf(z) < p_val:
            return('Y')
        else:
            return('N')

    except:
        return(None)

# Measureming Incremental Spend using a 4 point methodology
# Calls bootstrapping estimation and confidence interval functions

def measure_incremental_spend(data_pre_camp, data_camp, metric, control, by = None):
    # Data frames must be unique at the customer level
    # Must contain a flag to identify a row as a Control or Test
    # Metric column must be binary
    
    #Identify the control and metric column using a dictionary
    
    #control = {'col': 'control','test': 'N','control': 'Y'}
    #var = {'col': 'response', 'success': 'Y', 'failure': 'N'}

    # by = some categorical variable which will perform the measurements for each
    #      unique entry
    
    
    if by:
        a,b = data_pre_camp[by], data_camp[by]
        levels = set(a.append(b))
    else:
        by = 'by'
        data_pre_camp['by'] = 'Overall'
        data_camp['by'] = 'Overall'
        a,b = data_pre_camp[by], data_camp[by]
        levels = set(a.append(b))

    output = pd.DataFrame(columns = [by,'pop','pop_pct','control_spend','expected_spend','actual_spend',
                                     'pre_camp_sig','camp_sig','lift','error'])
    
    total_audience_size_test = len(data_camp[(data_camp[control['col']] == control['test'])])
    
    for level in levels:
        expected_spend, significant_pre, significant_camp, pre_camp_sig, camp_sig, lift = None, None, None, None, None, None
         
        count = len(data_camp[(data_camp[control['col']] == control['test']) &
                               (data_camp[by] == level)])
        test_spend_pre, x = create_bootstrap_mean(data_pre_camp[(data_pre_camp[control['col']] == control['test']) & 
                                                                (data_pre_camp[by] == level)
                                                                ][metric])
        
        control_spend_pre, y = create_bootstrap_mean(data_pre_camp[(data_pre_camp[control['col']] == control['control']) &
                                                                   (data_pre_camp[by] == level)
                                                                ][metric])
        ci_pre = []
        error = []

        if not (x and y):
            spend_diff_pre = test_spend_pre - control_spend_pre
            ci_pre = get_ci(spend_diff_pre)
            if ci_pre[0] <= 0 and ci_pre[1] >= 0:
                significant_pre = 'N'
            else:
                significant_pre = 'Y'
            
        if x:
            error.append('NPC')
        if y:
            error.append('NPT') 
        if test_spend_pre.sum() == 0:
            error.append('ZPT')
        if control_spend_pre.sum() == 0:
            error.append('ZPC')
            
            
        test_spend_camp, x = create_bootstrap_mean(data_camp[(data_camp[control['col']] == control['test']) &
                                                (data_camp[by] == level)][metric])
        control_spend_camp, y = create_bootstrap_mean(data_camp[(data_camp[control['col']] == control['control']) &
                                                   (data_camp[by] == level)][metric])
        
        ci_camp = []
        
        
        if not (x and y):
            spend_diff_camp = test_spend_camp - control_spend_camp
            ci_camp = get_ci(spend_diff_camp)
            if ci_camp[0] <= 0 and ci_camp[1] >= 0:
                significant_camp = 'N'
            else:
                significant_camp = 'Y'
                
        if x:
            error.append('NCC')
        if y:
            error.append('NCT') 
        if test_spend_camp.sum() == 0:
            error.append('ZCT')
        if control_spend_camp.sum() == 0:
            error.append('ZCC')
    
        actual_spend = test_spend_camp.mean()
        pre_diff = test_spend_pre.mean() - control_spend_pre.mean()
        if not error:
            control_spend = control_spend_camp.mean()
            
            expected_spend = (control_spend_camp.mean() / control_spend_pre.mean()) * test_spend_pre.mean()
            
            lift = (actual_spend - expected_spend) / expected_spend
            
            pop = len(data_camp[(data_camp[control['col']] == control['test']) &
                               (data_camp[by] == level)]) / total_audience_size_test
    
    

        output = output.append({
            by: level,
            #'pre_diff': pre_diff,
            'pop' : count,
            'pop_pct': pop,
            'control_spend': control_spend,
            'expected_spend': expected_spend,
            'actual_spend': actual_spend,
            'pre_camp_sig': significant_pre,
            'camp_sig': significant_camp,
            'lift': lift,
            'error': error
            
        }, ignore_index = True)
    return(output)
    
def measure_incremental_binomial_var(data_pre_camp, data_camp, metric, control, by = None):
    # Data frames must be unique at the customer level
    # Must contain a flag to identify a row as a Control or Test
    # Metric column must be binary
    
    #Identify the control and metric column using a dictionary
    
    #control = {'col': 'control','test': 'N','control': 'Y'}
    #var = {'col': 'response', 'success': 'Y', 'failure': 'N'}

  
    if by:
        a,b = data_pre_camp[by], data_camp[by]
        levels = set(a.append(b))
    else:
        by = 'by'
        data_pre_camp['by'] = 'Overall'
        data_camp['by'] = 'Overall'
        a,b = data_pre_camp[by], data_camp[by]
        levels = set(a.append(b))
        
    
    output = pd.DataFrame(columns = [by,'pop','control_' + var['col'],'expected_' + var['col'],'actual_'+ var['col'],
                                     'pre_camp_sig','camp_sig','abs_lift','error'])
    
    total_audience_size_test = len(data_camp[(data_camp[control['col']] == control['test'])])
                                             
    for level in levels:
        c_p,t_p,c_c,t_c = None,None,None,None
        pre_diff,expected,abs_lift,significant_pre,significant_camp = None,None,None,None,None
        pop = None
        
        error = []
        
        control_success_pre = len(data_pre_camp[(data_pre_camp[control['col']] == control['control']) & 
                                    (data_pre_camp[by] == level) &
                                    (data_pre_camp[var['col']] == var['success'])])
        
        test_success_pre = len(data_pre_camp[(data_pre_camp[control['col']] == control['test']) & 
                                    (data_pre_camp[by] == level) &
                                    (data_pre_camp[var['col']] == var['success'])])
        
        control_success_camp = len(data_camp[(data_camp[control['col']] == control['control']) & 
                                    (data_camp[by] == level) &
                                    (data_camp[var['col']] == var['success'])])
        
        test_success_camp = len(data_camp[(data_camp[control['col']] == control['test']) & 
                                    (data_camp[by] == level) &
                                    (data_camp[var['col']] == var['success'])])
        
        control_size_pre = len(data_pre_camp[(data_pre_camp[control['col']] == control['control']) & 
                                    (data_pre_camp[by] == level)])
        test_size_pre = len(data_pre_camp[(data_pre_camp[control['col']] == control['test']) & 
                                    (data_pre_camp[by] == level)])
        
        control_size_camp = len(data_camp[(data_camp[control['col']] == control['control']) & 
                                    (data_camp[by] == level)])
        test_size_camp = len(data_camp[(data_camp[control['col']] == control['test']) & 
                                    (data_camp[by] == level)])
        
        
        try:
            c_p = control_success_pre/control_size_pre
            if not c_p:
                error.append('ZPC')
        except:
            error.append('NPC')
        try:        
            t_p = test_success_pre/test_size_pre
            if not t_p:
                error.append('ZPT')
        except:
            error.append('NPT')
        try:    
            c_c = control_success_camp/control_size_camp
            if not c_c:
                error.append('ZCC')
        except:
            error.append('NCC')
        try:
            t_c = test_success_camp/test_size_camp
            if not t_p:
                error.append('ZCT')
        except:
            error.append('NCT')
        
    
        pre_diff = t_p - c_p
        if not error:
            expected = (c_c / c_p) * (t_p)
            abs_lift = t_c - expected
                                             
        
            significant_pre = test_of_prop(control_success_pre, control_size_pre, 
                                           test_success_pre, test_size_pre, p_val = 0.05)
        
        
            significant_camp = test_of_prop(control_success_camp, control_size_camp, 
                                            test_success_camp, test_size_camp, p_val = 0.05)
            pop = test_size_camp / total_audience_size_test
        
        

        output = output.append({
            by: level,
            'pop': pop,
            'control_' + var['col']: c_c,
            'expected_' + var['col']: expected,
            'actual_'+ var['col']: t_c,
            'pre_camp_sig': significant_pre,
            'camp_sig': significant_camp,
            'abs_lift': abs_lift,
            'error': error
            
        }, ignore_index = True)
    return(output)
 
    
