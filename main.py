# -*- coding: utf-8 -*-
# Copyrights (c), 2020, Rinat Mukhometzianov

import pandas as pd
import PySimpleGUI as sg
from os.path import exists

class DATA_PROCESS():
    def __init__(self):
        self.fields = ['RID', 'PTID', 'AGE', 'COLPROT', 'EXAMDATE', 'Month', 'DX']

    def is_merge_exists(self):
        return exists('ADNIMERGE.csv')

    def selectNgenerate(self, stages, diags):
        adni_full = pd.read_csv('ADNIMERGE.csv', skipinitialspace=True, usecols=self.fields)

        phase = adni_full[adni_full.COLPROT.isin(stages) & adni_full.DX.isin(diags)]
        phase = phase.sort_values(by=['Month'])

        temp = phase.groupby('RID', sort=False).filter(lambda x: x.DX.eq(diags[0]).values[0] & x.DX.eq(diags[1]).values[-1])
        return temp.RID.unique()

class GUI():
    def __init__(self):
        sg.theme('default1')

        self.main_layout = [
            [
             sg.Frame(layout=
                    [
                    [sg.Checkbox('ADNI-1', default=True, size=(7,1), font=("Verdana", 12)), 
                     sg.Checkbox("ADNI-GO", size=(7,1), font=("Verdana", 12)), 
                     sg.Checkbox('ADNI-2', size=(7,1), font=("Verdana", 12)), 
                     sg.Checkbox('ADNI-3', size=(7,1), font=("Verdana", 12))]
                    ], title='Select ADNI phase(s)', relief=sg.RELIEF_SUNKEN, font=("Verdana", 18))
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
                    ], title='Select group', relief=sg.RELIEF_SUNKEN, font=("Verdana", 18))
            ],
            [sg.Multiline(key='-res-', size=(50,8))],
            [sg.Button('Find', font=("Verdana", 14))]
        ]

        self.main_window = sg.Window('Select subjects', self.main_layout, grab_anywhere=False)

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
            if event == 'Find':
                if self.dp.is_merge_exists():
                    stages = [self.menu_map_stage[i] for i in range(4) if values[i]]
                    groups = [self.menu_map_group[i] for i in range(4, 10) if values[i]][0]

                    res = self.dp.selectNgenerate(stages, groups)
                    self.main_window['-res-'].update(', '.join([str(i) for i in res]))
                else:
                    sg.Popup('ADNIMERGE.csv not found!', 'Please, put it in the same folder.')

        self.main_window.close()

g = GUI()
g.run()
