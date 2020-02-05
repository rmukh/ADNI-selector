# -*- coding: utf-8 -*-
# Copyrights (c), 2020, Rinat Mukhometzianov

import pandas as pd
import PySimpleGUI as sg
from os.path import exists

class DATA_PROCESS():
    def __init__(self):
        # Fields to read from a ADNIMERGE file
        self.fields = ['RID', 'PTID', 'AGE', 'COLPROT', 'EXAMDATE', 'Month', 'DX', 'DX_bl', 'VISCODE']

    def is_merge_exists(self):
        # Check if ADNIMERGE.csv file is available
        return exists('ADNIMERGE.csv')

    def selectNgenerate(self, stages, diags, age, age_range, include_convrgd):
        adni_full = pd.read_csv('ADNIMERGE.csv', skipinitialspace=True, usecols=self.fields)

        if len(diags) == 1:
            self.filtered_groups = adni_full[adni_full.COLPROT.isin(stages) & adni_full.DX_bl.isin(diags)] # for classification group selection
            
            if age != 0.0:
                self.filtered_groups = self.filtered_groups[self.filtered_groups.AGE.between(age - age_range, age + age_range)]
            
            self.filtered_groups = self.filtered_groups.sort_values(by=['Month'])

            if not include_convrgd:
                self.filtered_groups = self.filtered_groups.dropna(subset=['DX'])
                
                self.groups = self.filtered_groups.groupby('RID', sort=False)
                self.filtered_groups = self.groups.filter(lambda x: x.DX.eq(diags[0]).all())

        else:
            self.phase = adni_full[adni_full.COLPROT.isin(stages) & adni_full.DX.isin(diags)]

            if age != 0.0:
                self.phase = self.phase[self.phase.AGE.between(age - age_range, age + age_range)]

            self.phase = self.phase.sort_values(by=['Month'])
    
            self.groups = self.phase.groupby('RID', sort=False)
            
            # Filter subjects that are converged from diags[0] to diags[1]
            self.filtered_groups = self.groups.filter(lambda x: x.DX.eq(diags[0]).values[0] & x.DX.eq(diags[1]).values[-1])
        
        self.u_rids = self.filtered_groups.RID.unique()
            
        return self.u_rids

    def findRidRanges(self):
        rid_groups = self.filtered_groups.groupby('RID', sort=False)
        
        frame = pd.DataFrame({'First':rid_groups.first().EXAMDATE, 'Last':rid_groups.last().EXAMDATE})
        return frame.to_string()

class GUI():
    def __init__(self):
        sg.theme('default1')
        
        # Visual layout
        self.main_layout = [
            [
             sg.Frame(layout=
                    [
                    [sg.Checkbox('ADNI-1', default=True, size=(7,1), font=("Open Sans", 11)), 
                     sg.Checkbox('ADNI-GO', size=(7,1), font=("Open Sans", 11)), 
                     sg.Checkbox('ADNI-2', size=(7,1), font=("Open Sans", 11)), 
                     sg.Checkbox('ADNI-3', size=(7,1), font=("Open Sans", 11))]
                    ], title='Select ADNI phase(s)', relief=sg.RELIEF_SUNKEN, font=("Open Sans", 14))
            ],

            [
             sg.Frame(layout=
                    [
                    [sg.Radio('CN->MCI', "g", size=(8,1), font=("Open Sans", 11)), 
                     sg.Radio("CN->AD", "g", default=True, size=(8,1), font=("Open Sans", 11)), 
                     sg.Radio('MCI->AD', "g", size=(8,1), font=("Open Sans", 11))],
                    [sg.Radio('CN->CN', "g", size=(8,1), font=("Open Sans", 11)), 
                     sg.Radio('MCI->MCI', "g", size=(8,1), font=("Open Sans", 11)), 
                     sg.Radio('AD->AD', "g", size=(8,1), font=("Open Sans", 11))],
                    ], title='Converged subjects', relief=sg.RELIEF_SUNKEN, font=("Open Sans", 14))
            ],
            
            [
             sg.Frame(layout=
                    [
                    [sg.Radio('CN', "g", size=(8,1), font=("Open Sans", 11)), 
                     sg.Radio('MCI', "g", size=(8,1), font=("Open Sans", 11)), 
                     sg.Radio('AD', "g", size=(8,1), font=("Open Sans", 11))],
                    [sg.Radio('EMCI', "g", size=(8,1), font=("Open Sans", 11)), 
                     sg.Radio('LMCI', "g", size=(8,1), font=("Open Sans", 11)),
                     sg.Checkbox('stable only?', font=("Open Sans", 11), default=True, 
                                 tooltip='Include subjects that have been converged to other groups?')]
                    ], title='Classification groups', relief=sg.RELIEF_SUNKEN, font=("Open Sans", 14))
            ],
            
            [sg.Text('Age', font=("Open Sans", 11)), 
             sg.InputText(size=(5,1), default_text='0.0', font=("Open Sans", 10)),
             sg.Text(u'\xb1', font=("Default 12", 12)), # plus minus symbol
             sg.InputText(size=(5,1), default_text='0.0', font=("Open Sans", 10)),
             sg.Checkbox('Save to file', font=("Open Sans", 11))],
            [sg.Text('RIDs', font=("Open Sans", 16))],
            [sg.Multiline(key='-res_rid-', size=(50,7))],
            [sg.Text('RIDs date ranges', font=("Open Sans", 16))],
            [sg.Multiline(key='-res-rid_dates-', size=(50,7))],
            [sg.Button('Select', font=("Open Sans", 14))]
        ]

        self.main_window = sg.Window('Select subjects', self.main_layout, grab_anywhere=False)

        # Maps for meny only
        self.menu_map_stage = dict([(0, 'ADNI1'),
                              (1, 'ADNIGO'),
                              (2, 'ADNI2'),
                              (3, 'ADNI3')
                              ])

        self.menu_map_group = dict([(4, ['CN', 'MCI']),
                              (5, ['CN', 'AD']),
                              (6, ['MCI', 'AD']),
                              (7, ['CN', 'CN']),
                              (8, ['MCI', 'MCI']),
                              (9, ['AD', 'AD']),
                              (10, ['CN']),
                              (11, ['MCI']),
                              (12, ['AD']),
                              (13, ['EMCI']),
                              (14, ['LMCI'])
                              ])

        self.dp = DATA_PROCESS()

    def age_check(self):
        age = 0.0
        age_range = 0.0
        if self.values[16].replace('.','',1).isdigit() and self.values[17].replace('.','',1).isdigit():
            age = float(self.values[16])
            age_range = float(self.values[17])
            if age < 0.0 or age_range < 0.0:
                sg.Popup('Age can\'t be negative. Will be ignored in the final output.')
                age = 0.0
                age_range = 0.0
        else:
            sg.Popup('Your input in the Age field is not a real value. Will be ignored in the final output.')
        return age, age_range

    def run(self):
        while True:
            self.event, self.values = self.main_window.read()

            if self.event is None:
                break
            if self.event == 'Select':
                age, age_range = self.age_check()
                self.age_file_name = str(age-age_range) + '-' + str(age+age_range) if age != 0.0 else ''

                if self.dp.is_merge_exists():
                    self.stages = [self.menu_map_stage[i] for i in range(4) if self.values[i]]
                    self.groups = [self.menu_map_group[i] for i in range(4, 12) if self.values[i]][0]

                    res = self.dp.selectNgenerate(self.stages, self.groups, age, age_range, self.values[15])
                    self.res_rid = ', '.join([str(i) for i in res])

                    if self.res_rid == '': # if no results with specified input params
                        no_results_text = 'No results for the specified input!'
                        self.main_window['-res_rid-'].update(no_results_text)
                        self.main_window['-res-rid_dates-'].update(no_results_text)
                    else:
                        self.main_window['-res_rid-'].update(self.res_rid)

                        # Update window with fist and last date of exam for each subject
                        self.res_rid_dates = self.dp.findRidRanges()
                        self.main_window['-res-rid_dates-'].update(self.res_rid_dates)

                        # Write to file if selected and there are results to write
                        if self.values[18]:
                            self.write_to_file()
                else:
                    sg.Popup('ADNIMERGE.csv not found!', 'Please, put it in the same folder.')

        self.main_window.close()

    def write_to_file(self):
        with open('_'.join(self.stages)+'_'+'_'.join(self.groups)+'_'+self.age_file_name+'.txt', 'w') as f:
            f.write("RIDs:\n")
            f.write(self.res_rid)
            f.write("\n\n")
            f.write("RIDs and date ranges:\n")
            f.write(self.res_rid_dates)

g = GUI()
g.run()