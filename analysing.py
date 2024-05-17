import pandas as pd
import statsmodels.api as sm
import seaborn as sns

class AnalysingResults:
    def __init__(self, title:str) -> None:
        self.results = {
            'pp':[],
            'training':[],
            'set':[],
            'B0' : [],
            'B0_std' : [],
            'B1':[],
            'B1_std':[],
            'R2':[],
            'type_analysis':[]
        }
        
        self.title = title
        
    
    def _analysis(self, grouped_var, predictor, plot=False, **kwargs):
        X = sm.add_constant(grouped_var['rep'])
        y = grouped_var[predictor]
        model = sm.OLS(y, X).fit()
        B1, B0 = model.params[1], model.params[0]
        std = model.bse
        R2 = model.rsquared
        if plot:
            color = {
            1 : 'red',
            2 : 'blue',
            3 : 'orange',
            4 : 'green',
            5 : 'purple'
        
            }
            sns.regplot(grouped_var, x='rep', y=predictor , ax=kwargs['ax'], color=color[grouped_var['pp'].iloc[0]])
            kwargs['ax'].set_title(kwargs['title'])
            
        return (B0, B1, std, R2)  
        
    
    @property    
    def df(self):
        return pd.DataFrame(self.results)
    
    def update(self, pp, training, set, type_analysis, *args, **kwargs):
        results = self._analysis(*args, **kwargs)
        self.results['pp'].append(pp)
        self.results['training'].append(training)
        self.results['set'].append(set)
        self.results['type_analysis'].append(type_analysis)
        self.results['B0'].append(results[0])
        self.results['B0_std'].append(results[2][0])
        self.results['B1'].append(results[1])
        self.results['B1_std'].append(results[2][1])
        self.results['R2'].append(results[3])
        
    def to_csv(self, file_path):
        self.to_df().to_csv(file_path)
        
        
class AnalysisContainer:
    def __init__(self) -> None:
        self.container = {}
        
    def __add__(self, other: 'AnalysisContainer') -> 'AnalysisContainer':
        new_container = AnalysisContainer()
        new_container.container = {**self.container, **other.container}
        return new_container
        
    def update(self, analysing_results):
        if isinstance(analysing_results, AnalysingResults):
            self.container[analysing_results.title] = analysing_results
        elif all(isinstance(result, AnalysingResults) for result in analysing_results):
            for result in analysing_results:
                self.update(result)
        else:
            raise ValueError("Invalid input type. Expected AnalysingResults or list of AnalysingResults.")
    
    @property 
    def df_with_type_column(self):
        result = []
        for _, analysis in self.container.items():
            df = analysis.df
            result.append(df)
            merged_df = pd.concat(result)
        return merged_df
    
    @property
    def df_with_diffrent_columns(self):
        result = []
        for title, analysis in self.container.items():
            new_dict = {}
            keys_copy = list(analysis.results.keys())
            for key in keys_copy:
                if key in ['pp', 'training', 'set', 'type_analysis']:
                    new_dict[key] = analysis.results[key]
                    
                    
                else:
                    new_dict[f"{key}_{'_'.join(title.split('_')[:2])}"] = analysis.results[key]
             
            df = pd.DataFrame(new_dict)
            result.append(df)
        
        for df in result:
          df = df.drop('type_analysis', axis=1, inplace=True)
        #merged_df = result[0]
        #for df in result[1:]:
        #    merged_df = pd.merge(merged_df, df, on=['pp', 'set', 'training'], how='outer')
        
        merged_df = pd.concat(result)
        merged_df = merged_df.groupby(['training', 'pp', 'set']).mean().reset_index()
        return merged_df
            
        