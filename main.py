# -*- coding: utf-8 -*-
# Copyrights (c), 2020, Rinat Mukhometzianov

import pandas as pd
import PySimpleGUI as sg
from os.path import exists
from os.path import join


class DataProcessing:
    def __init__(self):
        # CSV tables from ADNI website
        self.merge_file = join('CSVs', 'ADNIMERGE.csv')

        # Fields to read from a ADNIMERGE file
        self.fields = ['RID', 'PTID', 'AGE', 'COLPROT', 'EXAMDATE', 'Month', 'DX', 'DX_bl', 'VISCODE']
        self.filtered_groups = None

    def is_merge_exists(self):
        # Check if ADNIMERGE.csv file is available
        return exists(self.merge_file)

    def select_and_generate(self, stages, diags, age, age_range, stable_only):
        adni_full = pd.read_csv(self.merge_file, skipinitialspace=True, usecols=self.fields)

        if len(diags) == 1:
            if diags[0] == 'EMCI' or diags[0] == 'LMCI':
                # for classification group selection
                self.filtered_groups = adni_full[adni_full.COLPROT.isin(stages) & adni_full.DX_bl.isin(diags)]
            else:
                self.filtered_groups = adni_full[adni_full.COLPROT.isin(stages) & (adni_full.DX.isin(diags) |
                                                                                   adni_full.DX_bl.isin(diags))]

            if age != 0.0:
                self.filtered_groups = self.filtered_groups[self.filtered_groups.AGE.between(age - age_range, age +
                                                                                             age_range)]

            self.filtered_groups = self.filtered_groups.sort_values(by=['Month'])

            if stable_only:
                self.filtered_groups = self.filtered_groups.dropna(subset=['DX'])

                groups = self.filtered_groups.groupby('RID', sort=False)
                self.filtered_groups = groups.filter(lambda x: x.DX.eq(diags[0]).all())

        else:
            phase = adni_full[adni_full.COLPROT.isin(stages) & adni_full.DX.isin(diags)]

            if age != 0.0:
                phase = phase[phase.AGE.between(age - age_range, age + age_range)]

            phase = phase.sort_values(by=['Month'])

            groups = phase.groupby('RID', sort=False)

            # Filter subjects that are converged from diags[0] to diags[1]
            self.filtered_groups = groups.filter(lambda x: x.DX.eq(diags[0]).values[0] & x.DX.eq(diags[1]).values[-1])

        u_rids = self.filtered_groups.RID.unique()
        return u_rids

    def find_rid_ranges(self):
        rid_groups = self.filtered_groups.groupby('RID', sort=False)

        frame = pd.DataFrame({'First': rid_groups.first().EXAMDATE, 'Last': rid_groups.last().EXAMDATE})
        return frame.to_string()


class GUI:
    def __init__(self):
        sg.theme('default1')

        # Visual layout
        self.main_layout = [
            [
                sg.Frame(layout=[
                    [sg.Checkbox('ADNI-1', default=True, size=(7, 1), font=("Open Sans", 11)),
                     sg.Checkbox('ADNI-GO', size=(7, 1), font=("Open Sans", 11)),
                     sg.Checkbox('ADNI-2', size=(7, 1), font=("Open Sans", 11)),
                     sg.Checkbox('ADNI-3', size=(7, 1), font=("Open Sans", 11))]
                ], title='Select ADNI phase(s)', relief=sg.RELIEF_SUNKEN, font=("Open Sans", 14))
            ],

            [
                sg.Frame(layout=[
                    [sg.Radio('CN->MCI', "g", default=True, size=(8, 1), font=("Open Sans", 11)),
                     sg.Radio('CN->AD', "g", size=(8, 1), font=("Open Sans", 11)),
                     sg.Radio('MCI->AD', "g", size=(8, 1), font=("Open Sans", 11))],
                    [sg.Radio('CN->CN', "g", size=(8, 1), font=("Open Sans", 11)),
                     sg.Radio('MCI->MCI', "g", size=(8, 1), font=("Open Sans", 11)),
                     sg.Radio('AD->AD', "g", size=(8, 1), font=("Open Sans", 11))],
                ], title='Converged subjects', relief=sg.RELIEF_SUNKEN, font=("Open Sans", 14))
            ],

            [
                sg.Frame(layout=[
                    [sg.Radio('CN', "g", size=(8, 1), font=("Open Sans", 11)),
                     sg.Radio('MCI', "g", size=(8, 1), font=("Open Sans", 11)),
                     sg.Radio('AD', "g", size=(8, 1), font=("Open Sans", 11))],
                    [sg.Radio('EMCI', "g", size=(8, 1), font=("Open Sans", 11)),
                     sg.Radio('LMCI', "g", size=(8, 1), font=("Open Sans", 11)),
                     sg.Checkbox('stable only?', font=("Open Sans", 11), default=True,
                                 tooltip='Include subjects that have been converged to other groups?')]
                ], title='Classification groups', relief=sg.RELIEF_SUNKEN, font=("Open Sans", 14))
            ],

            [sg.Text('Age', font=("Open Sans", 11)),
             sg.InputText(size=(5, 1), default_text='60.0', font=("Open Sans", 10)),
             sg.Text(u'\xb1', font=("Default 12", 12)),  # plus minus symbol
             sg.InputText(size=(5, 1), default_text='5.0', font=("Open Sans", 10)),
             sg.Checkbox('Save to file', font=("Open Sans", 11))],
            [sg.Text('RIDs', font=("Open Sans", 16))],
            [sg.Multiline(key='-res_rid-', size=(50, 7))],
            [sg.Text('RIDs date ranges', font=("Open Sans", 16))],
            [sg.Multiline(key='-res-rid_dates-', size=(50, 7))],
            [sg.Button('Select', font=("Open Sans", 14))]
        ]

        self.main_window = sg.Window('Select subjects', self.main_layout, grab_anywhere=False)

        # Maps for many only
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

        self.values = None
        self.dp = DataProcessing()

    def age_check(self):
        """
        Check if the user input age is indeed float point
        :return: return 'clean' age and range for it
        """
        age = 0.0
        age_range = 0.0
        if self.values[16].replace('.', '', 1).isdigit() and self.values[17].replace('.', '', 1).isdigit():
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
            event, self.values = self.main_window.read()

            if event == sg.WINDOW_CLOSED or event == 'Exit':
                break
            if event == 'Select':
                age, age_range = self.age_check()
                age_file_name = str(age - age_range) + '-' + str(age + age_range) if age != 0.0 else ''

                if self.dp.is_merge_exists():
                    stages = [self.menu_map_stage[i] for i in range(4) if self.values[i]]
                    groups = [self.menu_map_group[i] for i in range(4, 15) if self.values[i]][0]

                    res = self.dp.select_and_generate(stages, groups, age, age_range, self.values[15])
                    res_rid = ', '.join([str(i) for i in res])

                    if res_rid == '':  # if no results with specified input params
                        no_results_text = 'No results for the specified input!'
                        self.main_window['-res_rid-'].update(no_results_text)
                        self.main_window['-res-rid_dates-'].update(no_results_text)
                    else:
                        self.main_window['-res_rid-'].update(res_rid)

                        # Update window with fist and last date of exam for each subject
                        res_rid_dates = self.dp.find_rid_ranges()
                        self.main_window['-res-rid_dates-'].update(res_rid_dates)

                        # Write to file if selected and there are results to write
                        if self.values[18]:
                            self.write_to_file(stages, groups, age_file_name, res_rid, res_rid_dates)
                else:
                    sg.Popup('ADNIMERGE.csv not found!', 'Please, put it in the CSVs folder and restart the program.')

        self.main_window.close()

    @staticmethod
    def write_to_file(stages, groups, fn, res_rid, dates):
        with open('_'.join(stages) + '_' + '_'.join(groups) + '_' + fn + '.txt', 'w') as f:
            f.write("RIDs:\n")
            f.write(res_rid)
            f.write("\n\n")
            f.write("RIDs and date ranges:\n")
            f.write(dates)


g = GUI()
g.run()
