import pandas as pd


#Load in data
app_companies = pd.read_csv('app-companies.csv')
app_financial_metrics = pd.read_csv('app-financial-metrics.csv')


#Cleaning and combining data
app_companies =  app_companies.drop('country_code', axis=1) 
dataset = app_financial_metrics.merge(app_companies, on = 'company_id', how = 'inner')
df = dataset.sort_values(['company_id', 'date'])


#Splitting the data
app_names = ['Kutch Town', 'Sun Stone', 'Spirit Hunt', 'Mind Dome', 
            'Guard of Light', 'Geospace', 'Galaxy Stars', 'Merge Castles', 
            'Match Zero', 'Fitness Champ', 'Bluecraft']

grouped = df.groupby(['app_name'])

Kutch_Town = grouped.get_group('Kutch Town')
Sun_Stone = grouped.get_group('Sun Stone')
Spirit_Hunt = grouped.get_group('Spirit Hunt')
Mind_Dome = grouped.get_group('Mind Dome')
Guard_of_Light = grouped.get_group('Guard of Light')
Geospace = grouped.get_group('Geospace')
Galaxy_Stars = grouped.get_group('Galaxy Stars')
Merge_Castles = grouped.get_group('Merge Castles')
Match_Zero = grouped.get_group('Match Zero')
Fitness_Champ = grouped.get_group('Fitness Champ')
Bluecraft = grouped.get_group('Bluecraft')

apps = [Kutch_Town, Sun_Stone, Spirit_Hunt, Mind_Dome, 
        Guard_of_Light,Geospace, Galaxy_Stars, Merge_Castles, 
        Match_Zero, Fitness_Champ, Bluecraft]


#Calculating Payback Period 
def payback_period_calculator(df):
    global marketing_spend
    marketing_spend = df.loc[df.marketing_spend > 1, 'marketing_spend'].values[0]
    
    global daily_revenue
    daily_revenue = []
    
    for days in range(31):
        daily_revenue.append(int(df['revenue'].values[days]))

    payback_calculation = []
    initial = marketing_spend - daily_revenue[0]
    payback_calculation.append(initial)
   
    day = 1 
    x = 0
    for days in daily_revenue:
        y = payback_calculation[x] - daily_revenue[day]
        payback_calculation.append(y)
        day +=1
        x +=1
        if int(y) <= 0:
            break
        if day == 31:
            break
    global payback_period
    payback_period = int(day)
    return payback_period


#Calculating LTV:CAC Ratio
def LTV_CAC_ratio_caclulator(df):
    payback_period_calculator(df)
    LTV = sum(daily_revenue)
    CAC = marketing_spend 
    global LTV_CAC_ratio
    LTV_CAC_ratio = (LTV/CAC)
    return LTV_CAC_ratio


#Calculating Risk Score
def risk_score_calculator(df):
    global payback_value

    if payback_period < 7:
        payback_value = 100

    if payback_period >= 7 and payback_period <= 13:
        payback_value = 60

    if payback_period >= 14 and payback_period <= 20:
        payback_value = 60

    if payback_period >= 21 and payback_period <= 27:
        payback_value = 30

    if payback_period > 28:
        payback_value = 10

    global LTV_CAC_value
    if LTV_CAC_ratio >= 3.0:
        LTV_CAC_value = 100

    if LTV_CAC_ratio > 2.5 and LTV_CAC_ratio < 3.0:
        LTV_CAC_value = 80    

    if LTV_CAC_ratio > 2.0 and LTV_CAC_ratio < 2.5:
        LTV_CAC_value = 60  
    
    if LTV_CAC_ratio > 1.5 and LTV_CAC_ratio < 2.0:
        LTV_CAC_value = 30      
    
    if LTV_CAC_ratio < 1.5:
        LTV_CAC_value = 10    
    
    payback_score = 0.7
    LTV_CAC_score = 0.3

    global risk_score
    risk_score = (payback_score * payback_value) + (LTV_CAC_score * LTV_CAC_value)
    
    return risk_score


#Calculating Risk Rating 
def credit_risk_rating(df):
    global risk_rating 

    if risk_score >= 85 and risk_score <= 100:
            risk_rating = 'Undoubted'

    if risk_score >= 65 and risk_score <= 84:
        risk_rating = 'Low'

    if risk_score >= 45 and risk_score <= 64:
        risk_rating = 'Moderate'

    if risk_score >= 25 and risk_score <= 44:
        risk_rating = 'Cautionary'

    if risk_score >= 15 and risk_score <= 24:
        risk_rating = 'Unsatisfactory'
    
    if risk_score <= 14:
        risk_rating = 'Unacceptable' 
 
    return risk_rating


#Creating new dataframe with scores
def df_calc(df):
    payback_period_calculator(df)
    LTV_CAC_ratio_caclulator(df)
    risk_score_calculator(df)
    credit_risk_rating(df)
    df1 = df.assign(risk_rating = risk_rating, risk_score = risk_score)
    df2 = df1.iloc[[0,1], [1,2,5,6,7]]
    return df2


#Combining into single csv
list_of_df = []
for df in apps:
    df = df_calc(df)
    list_of_df.append(df)

output = pd.concat(list_of_df, axis = 0)


#Sort by risk score in descending order
result = output.drop_duplicates()
result_sorted = result.sort_values(by = 'risk_score', ascending = False)


#Output as a single csv 
result_sorted.to_csv('app-credit-risk-ratings.csv', index = False)
