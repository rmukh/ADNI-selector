# -*- coding: utf-8 -*-
# Copyrights (c), 2020, Rinat Mukhometzianov

import pandas as pd
import PySimpleGUI as sg
from os.path import exists

class DATA_PROCESS():
    def __init__(self):
        # Fields to read from a ADNIMERGE file
        self.fields = ['RID', 'PTID', 'AGE', 'COLPROT', 'EXAMDATE', 'Month', 'DX']

    def is_merge_exists(self):
        # Check if ADNIMERGE.csv file is available
        return exists('ADNIMERGE.csv')

    def selectNgenerate(self, stages, diags):
        adni_full = pd.read_csv('ADNIMERGE.csv', skipinitialspace=True, usecols=self.fields)

        self.phase = adni_full[adni_full.COLPROT.isin(stages) & adni_full.DX.isin(diags)]
        self.phase = self.phase.sort_values(by=['Month'])

        self.groups = self.phase.groupby('RID', sort=False)

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
                    [sg.Checkbox('ADNI-1', default=True, size=(7,1), font=("Verdana", 12)), 
                     sg.Checkbox('ADNI-GO', size=(7,1), font=("Verdana", 12)), 
                     sg.Checkbox('ADNI-2', size=(7,1), font=("Verdana", 12)), 
                     sg.Checkbox('ADNI-3', size=(7,1), font=("Verdana", 12))]
                    ], title='Select ADNI phase(s)', relief=sg.RELIEF_SUNKEN, font=("Verdana", 16))
            ],

            [
             sg.Frame(layout=
                    [
                    [sg.Radio('CN->MCI', "g", size=(8,1), font=("Verdana", 12)), 
                     sg.Radio("CN->AD", "g", default=True, size=(8,1), font=("Verdana", 12)), 
                     sg.Radio('MCI->AD', "g", size=(8,1), font=("Verdana", 12))],
                    [sg.Radio('CN->CN', "g", size=(8,1), font=("Verdana", 12)), 
                     sg.Radio('MCI->MCI', "g", size=(8,1), font=("Verdana", 12)), 
                     sg.Radio('AD->AD', "g", size=(8,1), font=("Verdana", 12))]
                    ], title='Select group', relief=sg.RELIEF_SUNKEN, font=("Verdana", 16))
            ],
            [sg.Checkbox('Save to file', font=("Verdana", 12))],
            [sg.Text('RIDs', font=("Verdana", 16))],
            [sg.Multiline(key='-res_rid-', size=(50,8))],
            [sg.Text('RIDs date ranges', font=("Verdana", 16))],
            [sg.Multiline(key='-res-rid_dates-', size=(50,8))],
            [sg.Button('Select', font=("Verdana", 14))]
        ]

        self.main_window = sg.Window('Select subjects', self.main_layout, grab_anywhere=False)
        
        # Maps for meny only
        self.menu_map_stage = dict([(0, 'ADNI1'),
                              (1, 'ADNIGO'),
                              (2, 'ADNI2'),
                              (3, 'ADNI3')])

        self.menu_map_group = dict([(4, ['CN', 'MCI']),
                              (5, ['CN', 'AD']),
                              (6, ['MCI', 'AD']),
                              (7, ['CN', 'CN']),
                              (8, ['MCI', 'MCI']),
                              (9, ['AD', 'AD'])
                              ])

        self.dp = DATA_PROCESS()

    def run(self):
        while True:
            event, values = self.main_window.read()

            if event is None:
                break
            if event == 'Select':
                if self.dp.is_merge_exists():
                    stages = [self.menu_map_stage[i] for i in range(4) if values[i]]
                    groups = [self.menu_map_group[i] for i in range(4, 10) if values[i]][0]

                    res = self.dp.selectNgenerate(stages, groups)
                    form_res = ', '.join([str(i) for i in res])
                    self.main_window['-res_rid-'].update(form_res)
                    
                    # Update window with fist and last date of exam for each subject
                    res_rid_dates = self.dp.findRidRanges()
                    self.main_window['-res-rid_dates-'].update(res_rid_dates)
                else:
                    sg.Popup('ADNIMERGE.csv not found!', 'Please, put it in the same folder.')

        self.main_window.close()

g = GUI()
g.run()
