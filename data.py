from datetime import datetime
import numpy as np


def check_date_format(date_str):
    try:
        # Attempt to parse the date string using the first format "%Y-%m-%dT%H:%M:%S"
        return np.datetime64(datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S"))

    except ValueError:
        try:
            # Attempt to parse the date string using the second format "%Y-%m-%d"
            return np.datetime64(datetime.strptime(date_str, "%Y-%m-%d"))

        except ValueError:
            # If neither format matches, raise an exception or return an appropriate message
            raise ValueError("Invalid date format")


def create_narration(text):
    try:
        x = text.split(sep=' ')
        # Captures the first instance where text starts starts with '|'
        start_point = x.index([i for i in x if i.startswith('|')][0])
        # Captures the first instance where text ends starts with '|'
        end_point = x.index([j for j in x if j.endswith('|')][0]) + 1
        return ' '.join(x[start_point:end_point]).title().replace('|', '')
    except (IndexError, AttributeError):
        # to handle sitituation wherer narration text does not start with / ends with '|' or
        # does not have '|' at all
        return None


company_info = [
    {'cid': '1',
     'data': {
         'database': 'elite_security',
         'long_name': 'Elite Security Services',
         'abbr': 'ESS',
         'rev_cat': ['Manpower', 'Projects', 'Services'],
         'nav_links': ['Finance', 'HR', 'Operations', 'Sales'],
         'constants': {'RP': 1_220, 'HC': 100, 'TRAINING': 500, 'ACCOMODATION': 3_420, 'TRPT': 3_000},
         'voucher_types': {'Sales Invoice': -1, 'Credit Note': -1, 'Journal Entry': 0, 'Project Invoice': 0,
                           'Contract Invoice': -1, 'Debit Note': -1, 'Receipt': 0, 'SERVICE INVOICE': -1}
     }
     },
    {'cid': '2',
     'data': {
         'database': 'premium',
         'long_name': 'Premium Hospitality',
         'abbr': 'PH',
         'rev_cat': ['Manpower'],
         'nav_links': ['Finance', 'Operations', 'Sales'],
         'constants': {'RP': 1_220, 'HC': 100, 'TRAINING': 500, 'ACCOMODATION': 3_320, 'TRPT': 3_000},
         'voucher_types': {'Sales Invoice': -1, 'Credit Note': -1, 'Journal Entry': -2, 'Project Invoice': -2,
                           'Receipt': -1, 'Contract Invoice': -1, 'Debit Note': -1, 'SERVICE INVOICE': -1}}
     },
    {'cid': '3',
     'data': {
         'database': 'nbn_logistics',
         'long_name': 'NBN Logistics',
         'abbr': 'NBL',
         'rev_cat': ['Clearance', 'Transport', 'Freight', 'Other'],
         'nav_links': ['Finance', 'HR', 'Sales'],
         'constants': {'RP': 0, 'HC': 0, 'TRAINING': 0, 'ACCOMODATION': 0, 'TRPT': 0},
         'voucher_types': {'Sales Invoice': -1, 'Credit Note': -1, 'Journal Entry': -1, 'Project Invoice': -2,
                           'Receipt': -1, 'Contract Invoice': -1, 'Debit Note': -1, 'SERVICE INVOICE': -1}}
     },
    {'cid': '4',
     'data': {
         'database': 'nbn_realestate',
         'long_name': 'NBN Real Estate',
         'abbr': 'NBR',
         'rev_cat': ['Clearance', 'Transport', 'Freight', 'Other'],
         'nav_links': ['Finance', 'HR', 'Sales'],
         'constants': {'RP': 0, 'HC': 0, 'TRAINING': 0, 'ACCOMODATION': 0, 'TRPT': 0},
         'voucher_types': {'Sales Invoice': -1, 'Credit Note': -1, 'Journal Entry': -1, 'Project Invoice': -2,
                           'Receipt': -1, 'Contract Invoice': -1, 'Debit Note': -1, 'SERVICE INVOICE': -1}}
     }
]

table_info = [
    {
        'sheetname': 'fData',
        'usecols': ['voucher_number', 'voucher_date', 'type', 'ledger_code', 'business_unit',
                    'job_number', 'service_element_code', 'debit', 'credit'],
        'index': 'voucher_number'
    },
    {
        'sheetname': 'fLogInv',
        'usecols': ['job_number', 'invoice_number', 'invoice_date', 'customer_code', 'sales_person_code', 'net_amount'],
        'index': 'invoice_number'
    },
    {
        'sheetname': 'fOutSourceInv',
        'usecols': ['invoice_number', 'invoice_date', 'customer_code', 'net_amount'],
        'index': 'invoice_number'
    },
    {
        'sheetname': 'fAMCInv',
        'usecols': ['invoice_number', 'invoice_date', 'customer_code', 'net_amount'],
        'index': 'invoice_number'
    },
    {
        'sheetname': 'fProInv',
        'usecols': ['invoice_number', 'invoice_date', 'customer_code', 'net_amount', 'order_id'],
        'index': 'invoice_number'
    },
    {
        'sheetname': 'fCreditNote',
        'usecols': ['invoice_number', 'invoice_date', 'ledger_code', 'net_amount', 'type'],
        'index': 'invoice_number'
    },
    {
        'sheetname': 'fBudget',
        'usecols': ['fy', 'ledger_code', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov',
                    'dec'],
        'index': 'ledger_code'
    },
    {
        'sheetname': 'dEmployee',
        'usecols': ['emp_id', 'emp_type', 'emp_name', 'dept', 'designation', 'grade', 'dob', 'doj', 'leave_policy',
                    'nationality', 'confirmation_date', 'sex', 'maritial_state', 'travel_cost', 'current_status',
                    'last_increment', 'last_rejoin', 'termination_date', 'ba', 'hra', 'tra', 'ma', 'oa', 'pda'],
        'index': 'emp_id'
    },
    {
        'sheetname': 'dJobs',
        'usecols': ['job_number', 'customer_code', 'job_date', 'emp_id'],
        'index': 'job_number'
    },
    {
        'sheetname': 'fGL',
        'usecols': ['bussiness_unit_name', 'cost_center', 'voucher_date', 'voucher_number', 'credit', 'debit',
                    'transaction_type', 'job_id', 'ledger_code', 'narration'],
        'index': 'ledger_code'
    },
    {
        'sheetname': 'fGlJob',
        'usecols': ['voucher_date', 'voucher_number', 'credit', 'debit', 'transaction_type', 'job_number',
                    'ledger_code'],
        'index': 'ledger_code'
    },
    {
        'sheetname': 'dCoAAdler',
        'usecols': ['ledger_code', 'ledger_name', 'first_level', 'forth_level', 'third_level', 'second_level'],
        'index': 'ledger_code'
    },
    {
        'sheetname': 'dCustomers',
        'usecols': ['customer_code', 'cus_name', 'ledger_code'],
        'index': 'customer_code'
    },
    {
        'sheetname': 'fOT',
        'usecols': ['cost_center', 'date', 'job_id', 'attendance', 'ot_hr', 'net', 'day_type'],
        'index': 'cost_center'
    },
    {
        'sheetname': 'fBudget',
        'usecols': ['fy', 'ledger_code', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov',
                    'dec'],
        'index': 'ledger_code'
    }
]

db_info = {'HOSTNAME': 'localhost',
           'USERNAME': 'postgres',
           'PWD': '1948',
           'PORT_ID': 5432}

fin_tiles_values = [
    {'value': 'Revenue', 'filt': [
        'Logistics Revenue', 'Manpower Revenue', 'Projects Revenue', 'Services Revenue']},

    {'value': 'GP', 'filt': ['Logistics Revenue', 'Manpower Revenue', 'Projects Revenue', 'Services Revenue',
                             'Staff Cost - Logistics', 'Service Cost - Logistics', 'Accommodation - Manpower',
                             'Staff Cost - Manpower',
                             'Transportation - Manpower', 'Others - Manpower',
                             'Material Parts & Consumables - Projects', 'Staff Cost - Projects',
                             'Maintenance - Projects', 'Depreciation - Projects', 'Others - Projects',
                             'Material Parts & Consumables - Services']},

    {'value': 'Overhead', 'filt': ['Staff Cost', 'Rental Expenses', 'Office Expenses.', 'Sales & Promotion',
                                   'Management Fees', 'Professional & Legal', 'Depreciation', 'Others - G & A',
                                   'Provision for Doubtful debts']},

    {'value': 'NP', 'filt': ['Logistics Revenue', 'Manpower Revenue', 'Projects Revenue', 'Services Revenue',
                             'Staff Cost - Logistics', 'Service Cost - Logistics', 'Accommodation - Manpower',
                             'Staff Cost - Manpower',
                             'Transportation - Manpower', 'Others - Manpower',
                             'Material Parts & Consumables - Projects', 'Staff Cost - Projects',
                             'Maintenance - Projects', 'Depreciation - Projects', 'Others - Projects',
                             'Interest Expenses', 'Other Income', 'Other Revenue', 'Staff Cost', 'Rental Expenses',
                             'Office Expenses.', 'Sales & Promotion',
                             'Management Fees', 'Professional & Legal', 'Depreciation', 'Others - G & A',
                             'Provision for Doubtful debts', 'Material Parts & Consumables - Services']},

    {'value': 'EBITDA', 'filt': ['Logistics Revenue', 'Manpower Revenue', 'Projects Revenue', 'Services Revenue',
                                 'Staff Cost - Logistics', 'Service Cost - Logistics', 'Accommodation - Manpower',
                                 'Staff Cost - Manpower',
                                 'Transportation - Manpower', 'Others - Manpower',
                                 'Material Parts & Consumables - Projects', 'Staff Cost - Projects',
                                 'Maintenance - Projects', 'Others - Projects',
                                 'Other Income', 'Other Revenue', 'Staff Cost', 'Rental Expenses', 'Office Expenses.',
                                 'Sales & Promotion',
                                 'Management Fees', 'Professional & Legal', 'Others - G & A',
                                 'Material Parts & Consumables - Services']}
]

fin_tiles_pct = ['GP %', 'NP %', 'EBITDA %']

time_series_data = {
    'Current Month': 'current_month',
    'Previous Year Same Month': 'previous_year_same_month',
    'YTD Current Year': 'ytd_current_year'
}

USER_MAPPING = {'njayathunga@nbn.qa': '123',
                'jdurage@nbn.qa': '6h#CheC9',
                'gmathew@nbn.qa': 'mE5r*bR$',
                'aalinkeel@nbn.qa': 'pHuj$&4e',
                'hmushtaq@nbn.qa': 'Y=9ADoP8',
                'mamaan@nbn.qa': 'cr2tr!Cr',
                'nsaleem@nbn.qa': '5i0Wa_ok',
                'amohan@nbn.qa': '@ePRUs1P',
                'mabdelkarem@nbn.qa': 'p_Ls3ok#',
                'skhazi@nbn.qa': 's_0ZU8Lt',
                'maziz@nbn.qa': 'bUc!1p3t',
                'adiab@nbn.qa': 'bUc!1p3t',
                'gdemaiche@nbn.qa': 'bUc!1p3t',
                'akhan@nbn.qa': '$iMogo32',
                'dthakker@hnbk.qa': '$iMogo32',
                'g.issa@nbn-media.com': '$iMogo32',
                'm.ezzat@nbn-media.com': 'F+Voj6'}

graph_legends = {'Logistics Revenue - Clearance': 'Clearance',
                 'Logistics Revenue - Transport': 'Transport',
                 'Logistics Revenue - Freight': 'Freight',
                 'Logistics Revenue - Other': 'Other',
                 'Manpower Revenue': 'Manpower',
                 'Projects Revenue': 'Projects',
                 'Services Revenue': 'Services'}

months = {'01': 'Jan',
          '02': 'Feb',
          '03': 'Mar',
          '04': 'Apr',
          '05': 'May',
          '06': 'Jun',
          '07': 'Jul',
          '08': 'Aug',
          '09': 'Sep',
          '10': 'Oct',
          '11': 'Nov',
          '12': 'Dec',
          'Total': 'Total',
          'first_level': 'Header'}

pl_sort_order = {'Manpower Revenue': 1,
                 'Projects Revenue': 2,
                 'Services Revenue': 3,
                 'Direct Income': 4,
                 'Staff Cost - Manpower': 5,
                 'Transportation - Manpower': 6,
                 'Accommodation - Manpower': 7,
                 'Others - Manpower': 8,
                 'Staff Cost - Projects': 9,
                 'Maintenance - Projects': 10,
                 'Depreciation - Projects': 11,
                 'Material Parts & Consumables - Projects': 12,
                 'Others - Projects': 13,
                 'Cost of Sales': 14,
                 'Gross Proft / Loss': 15,
                 'Gross Proft / Loss %': 16,
                 'Other Revenue': 17,
                 'Indirect Income': 18,
                 'Staff Cost': 19,
                 'Rental Expenses': 20,
                 'Office Expenses.': 21,
                 'Sales & Promotion': 22,
                 'Management Fees': 23,
                 'Professional & Legal': 24,
                 'Depreciation': 25,
                 'Others - G & A': 26,
                 'Provision for Doubtful debts': 27,
                 'Overhead': 28,
                 'Interest Expenses': 29,
                 'Finance Cost': 30,
                 'Net Profit / Loss': 31,
                 'Net Profit / Loss %': 32
                 }

job_type_exclusions = {'Manpower - Employee Benefits': ['not_joined', 'discharged'],
                       'exclude_list_ot': ['AC-ACCOMODATION', 'Annual Leave', 'Bereavement leave- Local',
                                           'Bereavement leave-Overseas', 'CI-CLIENT INTERVIEW', 'discharged',
                                           'FP-FINGER PRINT', 'Hajj Leave'
                                                              'HO-HEAD OFFICE', 'ME-MOI Exam', 'MM-MOI MEDICAL',
                                           'MT-MOI Training', 'not_joined', 'OF-Off', 'QM-QID MEDICAL', 'SB-STANDBY',
                                           'Sick Leave - FP', 'Sick Leave - HP',
                                           'Sick Leave - UP', 'SL-SICK LEAVE', 'TN-TRAINING', 'Unpaid Leave'],
                       'Manpower - Salaries': ['Annual Leave', 'Bereavement leave- Local', 'Bereavement leave-Overseas',
                                               'discharged', 'not_joined', 'Sick Leave - UP', 'Unpaid Leave'],
                       'exclude_list_fix_bil': ['AC-ACCOMODATION', 'Annual Leave', 'Bereavement leave- Local',
                                                'Bereavement leave-Overseas', 'discharged', 'Hajj Leave', 'not_joined',
                                                'OF-Off', 'PS-PATROLING SUPERVISOR',
                                                'SB-STANDBY', 'Sick Leave - FP', 'Sick Leave - HP', 'Sick Leave - UP',
                                                'SL-SICK LEAVE', 'Unpaid Leave'],
                       'exclude_list_fix_gen': ['not_joined', 'discharged'],
                       'exclude_list_off': ['AC-ACCOMODATION', 'Annual Leave', 'Bereavement leave- Local',
                                            'Bereavement leave-Overseas', 'CI-CLIENT INTERVIEW ', 'discharged',
                                            'FP-FINGER PRINT', 'Hajj Leave'
                                                               'HO-HEAD OFFICE', 'ME-MOI Exam', 'MM-MOI MEDICAL',
                                            'MT-MOI Training', 'not_joined', 'OF-Off', 'QM-QID MEDICAL', 'SB-STANDBY',
                                            'Sick Leave - FP', 'Sick Leave - HP',
                                            'Sick Leave - UP', 'SL-SICK LEAVE', 'TN-TRAINING', 'Unpaid Leave',
                                            'OJ-ON JOB TRAINING', 'PS-PATROLING SUPERVISOR']}

ctc_amount = {'insurance':
              {'a1': {'adult': 9_146, 'minor': 5_663},
               'a2': {'adult': 6_243, 'minor': 0},
               'b': {'adult': 5_898, 'minor': 3_693},
               'c': {'adult': 2_788, 'minor': 2_182},
               'd': {'adult': 1_977, 'minor': 0},
               },
              'rp':
                  {
                      'a1': {'adult': 1_220, 'minor': 500},
                      'a2': {'adult': 1_220, 'minor': 500},
                      'b': {'adult': 1_220, 'minor': 500},
                      'c': {'adult': 1_220, 'minor': 500},
                      'd': {'adult': 1_220, 'minor': 500},
              }}
