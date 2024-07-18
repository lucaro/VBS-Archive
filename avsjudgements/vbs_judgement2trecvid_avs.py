#
# Conversion code to generate AVS judgements in TRECVID format 
#
# 2024-07-18 Werner Bailer <werner.bailer@joanneum.at>
#
# CC-BY 4.0 licensed


import pandas as pd
import json
import math
import numpy as np
import argparse
import os

def process_dres_json(json_fn,outdir,competition,msbdir=None,dresformat=False):

    f = open(json_fn)

    data = json.load(f)

    # check if we use DRES 2.x format
    dres2 = False
    if 'template' in data:
        dres2 = 'true'
        print('INFO: DRES 2.0 format detected')
        

       
    judgement_df = pd.DataFrame(columns=['taskName', 'query', 'junk','item','start_fr','start_s','end_fr','end_s','shot_id','stratum','judgement'])
           
    # collect judged submissions       
    task_subm_list = data['tasks']
        
    for task_subm in task_subm_list:
    
        if dres2:
            # look up task properties
            tid = task_subm['templateId']
            isavs = True
            for taskdef in data['template']['tasks']:
                if taskdef['id'] == tid:
                    if taskdef['taskGroup'] != 'AVS':
                        isavs = False
                    task_name = taskdef['name']
                    task_query = taskdef['hints'][0]['description']
                        
                    continue
            if not(isavs):
                continue
            
        
            
        else:
            if (task_subm['description']['taskType']['score']['option'] != 'AVS') and (task_subm['description']['taskType']['score']['option'] != 'AVS2'):
                continue

            task_name = task_subm['description']['name']
            task_query = task_subm['description']['hints'][0]['text']
        
            
        submissions = task_subm['submissions']
        
        for s in submissions:
            answer = s # no difference in DRES 1
            if dres2:
                answer = s['answers'][0]
        
            fps = answer['item']['fps']
            start_s = answer['start'] / 1000
            end_s = answer['end'] / 1000
            start_fr = math.floor(start_s*fps)
            end_fr = math.floor(end_s*fps)
            judgement = -1
            if s['status'] == 'CORRECT':
                judgement = 1
            elif s['status'] == 'WRONG':
                judgement = 0
            judgement_df.loc[len(judgement_df.index)] = [task_name, task_query, 0, answer['item']['name'], start_fr, start_s, end_fr, end_s, '', 1, judgement]   
    
    
    print(judgement_df)
    
    items = judgement_df['item'].unique()
    for item in items:
        print('processing '+str(item))
        item_subm = judgement_df.loc[judgement_df['item'] == item]
        item_subm_sorted = item_subm.drop_duplicates(subset=['start_fr','end_fr'],ignore_index=True)
        item_subm_sorted = item_subm_sorted.sort_values(['start_fr','end_fr'],ignore_index=True)
        
        if msbdir==None:
            # write shot reference and transform to shot ids
            for index, row in item_subm_sorted.iterrows():
                judgement_df.loc[np.logical_and(judgement_df['item']==item,np.logical_and(judgement_df['start_fr']==row['start_fr'], judgement_df['end_fr']==row['end_fr'])), 'shot_id'] = 'shot'+str(item)+'_'+str(index)
            
            item_subm_sorted.to_csv(os.path.join(outdir,str(item)+'.tsv'),sep='\t',columns=['start_fr','start_s','end_fr','end_s'],header=['startframe','starttime','endframe','endtime'],index=False)
    
            # map to TRECVID shot
        else:
            shotlist = pd.read_csv(os.path.join(msbdir,item+'.tsv'),sep='\t')
 
            additional_segments = pd.DataFrame(columns=judgement_df.columns)

            for index, row in shotlist.iterrows():
                overlap = judgement_df.loc[np.logical_and(judgement_df['item']==item,np.logical_or(np.logical_and(judgement_df['start_fr']>=row['startframe'], judgement_df['start_fr']<=row['endframe']),np.logical_and(judgement_df['end_fr']>=row['startframe'], judgement_df['end_fr']<=row['endframe'])))]
                for oindex,orow in overlap.iterrows():
                    # set shot id if not set
                    if len(orow['shot_id'])==0:
                        judgement_df.loc[judgement_df.index[oindex],'shot_id'] = 'shot'+str(item)+'_'+str(index)
                    # otherwise add new entry
                    else:  
                        baserow = judgement_df.loc[[oindex],:].copy()
                        baserow['hot_id'] = 'shot'+str(item)+'_'+str(index)
                        additional_segments = pd.concat([additional_segments,baserow])
                        
            if len(additional_segments)>0:
                judgement_df = pd.concat([judgement_df,additional_segments])
        
    judgement_df.to_csv(os.path.join(outdir,'avs.'+competition+'.txt'),sep='\t',columns=['taskName', 'junk','shot_id','stratum','judgement'],index=False,header=False)

    # write cleaned query list
    querylist = judgement_df.drop_duplicates(subset=['taskName','query'],ignore_index=True)
    querylist = querylist.sort_values(['taskName'],ignore_index=True)
    querylist = querylist.replace('\n','', regex=True)
    querylist = querylist.replace('\t','', regex=True)
    querylist = querylist.replace('"','', regex=True)
    querylist = querylist.replace('"','', regex=True)
    querylist.to_csv(os.path.join(outdir,'avs.'+competition+'.topics.txt'),sep='\t',columns=['taskName', 'query'],index=False,header=False)


    if dresformat:
        judgement_df.to_csv(os.path.join(outdir,'avs.'+competition+'_dres.txt'),sep='\t',columns=['taskName', 'junk','item','start_fr','start_s','end_fr','end_s','stratum','judgement'],index=False,header=True)


parser = argparse.ArgumentParser()
parser.add_argument('input_dir',
                    help='directory for input files (DRES run JSON)')
parser.add_argument('output_dir',
                    help='directory to write query list, annotation text files, and reference shot boundaries (if applicable)')
parser.add_argument('filename',
                    help='name of the run JSON file to process')
parser.add_argument('competition',
                    help='label of the competition (used to name the output files), e.g. vbs2022')
parser.add_argument('--msbdir', type=str, required=False, default=None,
                    help='map judgements to the TRECVID master shot boundaries provided in the directory')
parser.add_argument('--dresformat', action='store_true', required=False, default=False,
                    help='write outputs also in DRES (VBS/LSC) format (not applicable when --msbdir is used)')
args = parser.parse_args()

dresformat = args.dresformat
if args.msbdir:
    dresformat = False

process_dres_json(os.path.join(args.input_dir,args.filename),args.output_dir,args.competition,args.msbdir,dresformat)
