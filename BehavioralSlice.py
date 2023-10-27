#TO DO:
# Two logs.  One Receipt with NA
# 2nd log needs to first plus draft plus instructions.

# check various combos of instruments and studies
# include notes variables and check for PHI on the fly?
# map events to harmonized version (e.g. for FU stuff)
##########################################################################
## INSTRUCTIONS

# Create a directory containing this program:
## datarequestor='/your/path'
## make a directory within this folder called
# Download your AABC data (doesn't work on HCA data)... change the datadate and filenames
# Output is a table, slice dictionary, plots, distributions, and receipt

from ccf.box import LifespanBox
import pandas as pd
import matplotlib.pyplot as plt
import os
import shutil
from datetime import date
from config import *
import numpy as np
#requestsdir='/Users/petralenzini/work/datarequests/'
# Unless you are an administrator, Please create a folder somewhere, such as 'PL_test' below.
# Within that folder, create another folder called 'downloadedfiles'
# Download files from the Pre-Release folder in Box, and move them to the 'downloaded' files directory
# Place a copy of the encyclopedia in that directory, too.
# Recruitment pdf (always the latest because synced to BOX from local machine)
statsdir='/Users/petralenzini/work/Behavioral/AABC/AABC_Behavioral_QC/AABC_Behavioral_QC/'
statsfile='AABC_HCA_recruitmentstats.pdf'

# Now complete the following
datarequestor='jvando'  # name of folder in which you want to generate the slice.
study="HCA-AABC" #or HCA

#What instruments?  Please consult the Encyclopedia or check the boxes in the Data portal and use EXACT STRINGs (no extra spaces)
#modify this list:
BulkRequested=['Pre-Processed Imaging Sessions','Vasomotor Symptoms (VMS - Raw Bulk)']
InstRequested=['Actigraphy', 'International Physical Activity Questionnaire (IPAQ)', 'Pittsburgh Sleep Quality Index (PSQI)','Actigraphy Data Summaries Produced By Cobra Lab','Covid 19 Remote Visit - International Physical Activity Questionnaire (IPAQ) (Ipaq)', 'Covid 19 Remote Visit - Pittsburgh Sleep Quality Index (PSQI)','Extended Covid 19 Survey - Pittsburgh Sleep Quality Index (PSQI)','International Physical Activity Questionnaire (IPAQ) (Actigraphy Pilot)','Apoe Genotypes','Subject Inventory And Basic Information','Review Of Inclusion/Exclusion Criteria','Montreal Cognitive Assessment (MOCA)','Lab Collection','Lab Results','Medications','Menstrual Cycle','STRAW+10','Face-Name','Face-Name Counterbalance Group','Positive And Negative Affect Schedule (PANAS)','Visit Summary,','Followup: Menstrual Cycle','Followup: STRAW+10','CES-D Scale','STRAW+10','Vasomotor Symptom Device (VMS)']
DerivativesRequested=['Cognition Factor Analysis', 'Cardiometabolic Index and Allostatic Load','Imaging Derived Phenotypes','Vasomotor Symptoms (Processed)']
OtherInstruments=['Hormones (FSH, LH, testosterone, estradiol)']
#any additional variables?
IndividVars=[]
#Do you want caveman distributions of plots?
wantplots = True  # or False

#Are you an administrator with API credentials in the Pre-Release BOX folder?
isAdmin = True

#if you're not an admin, what is the name of the encyclopedia file you put in the downloadedfiles directory?
#encyclopedia_file="AABC_HCA_Encyclopedia_2023-10-14.csv" #if not an admin

#########################################################################################################
################################### Done with user specs #####################

InstRequest1=['Subject Inventory And Basic Information']+InstRequested
InstRequest=list(pd.DataFrame(InstRequest1).drop_duplicates()[0])

if not isAdmin:
    E = pd.read_csv(os.getcwd()+datarequestor+'/downloadedfiles/'+encyclopedia_file, low_memory=False, encoding='ISO-8859-1')
    Evars = E.loc[(E['Form / Instrument'].isin(InstRequest)) | (E['Variable / Field Name'].isin(IndividVars))]
    t1 = Evars.loc[(~(Evars['Form / Instrument'] == 'Subject Inventory And Basic Information'))]
    t2 = t1.loc[t1.Unavailable == 'U']
    droplist = list(t2['Variable / Field Name'])

if isAdmin:
    try:
        os.mkdir(os.path.join(os.getcwd(),datarequestor))
        os.mkdir(os.path.join(os.getcwd(),datarequestor+'/downloadedfiles/'))
    except:
        print("couldn't make folder for datarequestor: [",datarequestor,"]")
    try:
        config = LoadSettings()
        secret=pd.read_csv(config['config_files']['secrets'])
        #get list of files in Box folders (interative)
        box = LifespanBox(cache=os.path.join(os.getcwd(),datarequestor+'/downloadedfiles/'))
        hca_pre=box.list_of_files([str(config['hca_pre'])])
        aabc_pre=box.list_of_files([str(config['aabc_pre'])])
        E=pd.read_csv(box.downloadFile(config['encyclopedia']),low_memory=False,encoding='ISO-8859-1')
        #Evars=E.loc[E['Form / Instrument'].isin(InstRequest)]
        Evars = E.loc[(E['Form / Instrument'].isin(InstRequest)) | (E['Variable / Field Name'].isin(IndividVars))]
        t1 = Evars.loc[(~(Evars['Form / Instrument'] == 'Subject Inventory And Basic Information'))]
        t2 = t1.loc[t1.Unavailable == 'U']
        droplist=list(t2['Variable / Field Name'])

        print("Number of Requested Instruments:",len(InstRequest)-1)
        #print("Requested Instruments:",InstRequest)
        print("Number of Instruments Found:",len(Evars['Form / Instrument'].unique()))
        #print("Found Instruments:",Evars['Form / Instrument'].unique())

        #whittle down the list of files in the Pre-Release folder to the most recent subset
        hcafiles=pd.DataFrame.from_dict(hca_pre, orient='index')
        hcafiles=hcafiles.loc[~(hcafiles.filename.str.upper().str.contains('DICTIONARY') | hcafiles.filename.str.upper().str.contains('ENCYCLOPEDIA'))].copy()
        hcafiles['datestamp']=hcafiles.filename.str.split('_',expand=True)[2]
        hcafiles['datatype']=hcafiles.filename.str.split('_',expand=True)[1]
        hcafiles=hcafiles.loc[(hcafiles.datestamp.str.contains('.csv')==True) & (hcafiles.datestamp.str.contains('-'))].copy()
        hcafiles.datestamp=hcafiles.datestamp.str.replace('.csv','')
        hcafiles.datestamp=pd.to_datetime(hcafiles.datestamp)
        hcafiles=hcafiles.sort_values('datestamp',ascending=False)
        hcafiles=hcafiles.drop_duplicates(subset='datatype',keep='first').copy()

        aabcfiles=pd.DataFrame.from_dict(aabc_pre, orient='index')
        aabcfiles['datestamp']=aabcfiles.filename.str.split('_',expand=True)[2]
        aabcfiles['datatype']=aabcfiles.filename.str.split('_',expand=True)[1]
        aabcfiles=aabcfiles.loc[(aabcfiles.datestamp.str.contains('.csv')==True) & (aabcfiles.datestamp.str.contains('-'))].copy()
        aabcfiles.datestamp=aabcfiles.datestamp.str.replace('.csv','')
        aabcfiles.datestamp=pd.to_datetime(aabcfiles.datestamp)
        aabcfiles=aabcfiles.sort_values('datestamp',ascending=False)
        aabcfiles=aabcfiles.drop_duplicates(subset='datatype',keep='first').copy()

        #download
        for i in list(aabcfiles.fileid)+list(hcafiles.fileid):
            print("downloading",i,"...")
            box.downloadFile(i)
    except:
        print("Something went wrong")
##### end Admin section
# Loop through downloaded files and grab any of the Instruments therein, by study.
# THen stack studies together, incorporating exceptions for APOE, FAMILIES, and REgistration variables
widefileAABC=pd.DataFrame(columns=['study','subject','redcap_event'])
widefileHCA=pd.DataFrame(columns=['study','subject','redcap_event'])
for i in os.listdir(os.path.join(os.getcwd(),datarequestor+'/downloadedfiles/')):
    print(i)
    Evars2=list(Evars['Variable / Field Name'])+IndividVars

    if 'NIH' in i and 'Scores' in i:
        bulk=pd.read_csv(os.path.join(os.getcwd(),datarequestor+'/downloadedfiles/'+i),low_memory=False)
        bulk=bulk.loc[bulk.Inst.isin(InstRequest)]
        if not bulk.empty:
            bulk['subject']=bulk.PIN.str.split('_',expand=True)[0]
            bulk['redcap_event']=bulk.PIN.str.split('_',expand=True)[1]
            tlbxlist=[j for j in InstRequest if 'NIH' in j]
            for k in tlbxlist:
                tlbxvars=E.loc[E['Form / Instrument']==k][['Variable / Field Name','NIH Toolbox Prefix in Slice']]
                tlbxvars['newname']=tlbxvars['NIH Toolbox Prefix in Slice']+'_'+tlbxvars['Variable / Field Name']
                mapvars=dict(zip(list(tlbxvars['Variable / Field Name']),list(tlbxvars.newname)))#,tlbxvars['newname'])
                temp=bulk.loc[bulk.Inst==k][['subject','redcap_event']+list(tlbxvars['Variable / Field Name'])]
                temp=temp.rename(columns=mapvars)
                for j in ['site', 'study', 'PIN', 'redcap_event_name', 'site', 'study_id', 'id', 'gender']:
                    try:
                        temp = temp.drop(columns=[j]).copy()
                    except:
                        pass
                if 'AABC' in i:
                    widefileAABC=pd.merge(widefileAABC,temp, on=['subject','redcap_event'],how='outer')
                if 'HCA' in i:
                    widefileHCA = pd.merge(widefileHCA, temp, on=['subject', 'redcap_event'], how='outer')
    if 'Inventory' in i:
        temp = pd.read_csv(os.path.join(os.getcwd(),datarequestor+'/downloadedfiles/' + i), low_memory=False)
        subtempA = temp[temp.columns.intersection(set(['subject', 'redcap_event'] + Evars2))]
        dropvars=['pedid','nda_age','nda_interview_date','pseudo_guid','DB_Source','HCAid','HCDid','legacy_yn','sub_event','daysfromtime0','REDCap_id','study_id','psuedo_guid']
        keepvars=[i for i in list(subtempA.columns) if i not in dropvars]
        subtempB = subtempA[keepvars].copy()
        if 'AABC' in i:
            widefileAABC = pd.merge(widefileAABC, subtempB, on=['subject', 'redcap_event'], how='outer')
        if 'HCA' in i:
            widefileHCA = pd.merge(widefileHCA, subtempB, on=['subject', 'redcap_event'], how='outer')

    if 'Inventory' not in i and 'Apoe' not in i and 'Encyclopedia' not in i and 'NIH' not in i and ".DS_Store" not in i and '-INS' not in i and '-Resp' not in i and '-Items' not in i and '-TS' not in i and '-TNS' not in i:
        print(i)
        try:
            temp=pd.read_csv(os.path.join(os.getcwd(),datarequestor+'/downloadedfiles/'+i),low_memory=False)
            subtempA=temp[temp.columns.intersection(set(['subject', 'redcap_event']+Evars2))]
            for j in ['site', 'study', 'PIN', 'redcap_event_name', 'site', 'study_id', 'id', 'gender','ethnic','age','racial','sex']+droplist:
                try:
                    subtempA = subtempA.drop(columns=[j]).copy()
                except:
                    pass
            if 'AABC' in i:
                widefileAABC=pd.merge(widefileAABC,subtempA, on=['subject','redcap_event'],how='outer')
            if 'HCA' in i:
                widefileHCA = pd.merge(widefileHCA, subtempA, on=['subject', 'redcap_event'], how='outer')
        except:
            print('error')

    if 'Apoe' in i or 'FAMILY' in i:
        temp = pd.read_csv(os.path.join(os.getcwd(),datarequestor+'/downloadedfiles/' + i), low_memory=False)
        subtempA = temp[temp.columns.intersection(set(['subject'] + Evars2))].copy()
        for j in ['age','sex','site','study', 'PIN', 'redcap_event_name', 'site', 'study_id', 'id', 'gender','Specimen_ID','Specimen_Mass','Specimen_Type','DoExtraction','Protocol','DNA_barcode','DNA_volume','DNA_concentration','DNA_260_280','DNA_260_230','Notes_Pre_Run','Notes_During_Run','Notes_Post_Run','PI','Project','Final_Comments']+droplist:
            try:
                subtempA = subtempA.drop(columns=[j]).copy()
            except:
                pass
        if 'Apoe' in i:
            subtempA=subtempA.drop_duplicates()
        widefileHCA=pd.merge(widefileHCA,subtempA,on='subject',how='outer')

widefileAABC['study'] = 'AABC'
widefileHCA['study'] = 'HCA'
wide=pd.concat([widefileAABC,widefileHCA],axis=0).copy()

#clean up age variable
wide.event_age=wide.event_age.round(1)

#subset by study
if study=="HCA":
    wide=wide.loc[wide.study=="HCA"].copy()

#don't subset by event...drop missing rows
wide['countmiss']=wide.isna().sum(axis=1)
#wide=wide.loc[wide.countmiss<(wide.shape[1]-14)]
wide.countmiss.value_counts()

#drop empty columns
wide.dropna(how='all', axis=1, inplace=True)
wide=wide.drop(columns=['countmiss'])
wide=wide.drop_duplicates().copy()
#drop the CCF_PCMP_ITK subjects
wide=wide.loc[~(wide.IntraDB=='CCF_PCMP_ITK')].copy()
#make sure you're only getting subjects in the inventory
wide=wide.loc[wide.event_age>0]


harmony=wide.copy()
harmony['Cohort']=''
harmony['HCAAABC_event']=harmony.redcap_event
harmony.loc[((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_1')))
         | ((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_2')))
         | ((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_3')))
         | ((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_4'))),'Cohort']='AABC A'
harmony.loc[((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_5')))
         | ((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_6')))
         | ((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_7')))
         | ((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_8'))),'Cohort']='AABC B'
harmony.loc[((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_9')))
         | ((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_10')))
         | ((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_11')))
         | ((harmony.study=='AABC') & (harmony.redcap_event_name.str.contains('arm_12'))),'Cohort']='AABC C'
harmony.loc[(harmony.study=='HCA'),'Cohort']='HCA Cross'
v2list=list(harmony.loc[(harmony.redcap_event=='V2') & (harmony.study=='HCA'),'subject'].unique())
harmony.loc[(harmony.study=='HCA') & (harmony.subject.isin(v2list)),'Cohort']='HCA Long'

#check
harmony.loc[(harmony.study=='HCA') & (harmony.redcap_event=='V1')].IntraDB.value_counts(dropna=False)
harmony.loc[(harmony.study=='HCA') & (harmony.redcap_event=='V2')].IntraDB.value_counts(dropna=False)


#assign the harmonized event, then double check order by age
harmony.loc[(harmony.Cohort=='AABC A') & (harmony.redcap_event=='AF1'),'HCAAABC_event']='V3F1'
harmony.loc[(harmony.Cohort=='AABC A') & (harmony.redcap_event=='AF2'),'HCAAABC_event']='V4F1'
harmony.loc[(harmony.Cohort=='AABC A') & (harmony.redcap_event=='AF3'),'HCAAABC_event']='V4F2'
harmony.loc[(harmony.Cohort=='AABC B') & (harmony.redcap_event=='AF1'),'HCAAABC_event']='V2F1'
harmony.loc[(harmony.Cohort=='AABC B') & (harmony.redcap_event=='AF2'),'HCAAABC_event']='V3F1'
harmony.loc[(harmony.Cohort=='AABC B') & (harmony.redcap_event=='AF3'),'HCAAABC_event']='V3F2'
harmony.loc[(harmony.Cohort=='AABC C') & (harmony.redcap_event=='AF1'),'HCAAABC_event']='V1F1'
harmony.loc[(harmony.Cohort=='AABC C') & (harmony.redcap_event=='AF2'),'HCAAABC_event']='V2F1'
harmony.loc[(harmony.Cohort=='AABC C') & (harmony.redcap_event=='AF3'),'HCAAABC_event']='V2F2'
harmony.loc[(harmony.redcap_event=='AFZ'),'HCAAABC_event']='VZ'
harmony.loc[(harmony.redcap_event=='AF0'),'HCAAABC_event']='V0'
harmony.loc[(harmony.Cohort=='HCA Cross') & (harmony.redcap_event=='F1'),'HCAAABC_event']='V1F1'
harmony.loc[(harmony.Cohort=='HCA Cross') & (harmony.redcap_event=='F2'),'HCAAABC_event']='V1F2'
harmony.loc[(harmony.Cohort=='HCA Cross') & (harmony.redcap_event=='F3'),'HCAAABC_event']='V1F3'
harmony=harmony.reset_index()
harmony=harmony.drop(columns='index')
#common protocol deviations
longsubs=list(harmony.loc[(harmony.Cohort=='HCA Long')].subject.unique())
harmonysub=harmony.loc[(harmony.redcap_event.isin(['V1','V2','V3','F1','F2','F3'])) & (harmony.Cohort=='HCA Long')][['subject','redcap_event','HCAAABC_event','event_age']]
harmonysub=harmonysub.sort_values(['subject','event_age']).copy()
for s in longsubs:
    harmonysub.loc[(harmonysub.subject==s) & (harmonysub.redcap_event.shift(1)=='V1') & (harmonysub.redcap_event.str.contains('F')),'HCAAABC_event']='V1F1'
    harmonysub.loc[(harmonysub.subject==s) & (harmonysub.HCAAABC_event.shift(1)=='V1F1') & (harmonysub.redcap_event.shift(2)=='V1') & (harmonysub.redcap_event.str.contains('F')),'HCAAABC_event']='V1F2'
    harmonysub.loc[(harmonysub.subject==s) & (harmonysub.HCAAABC_event.shift(1)=='V1F2') & (harmonysub.redcap_event.shift(3)=='V1') & (harmonysub.redcap_event.str.contains('F')),'HCAAABC_event']='V1F3'
    harmonysub.loc[(harmonysub.subject==s) & (harmonysub.redcap_event.shift(1)=='V2') & (harmonysub.redcap_event.str.contains('F')),'HCAAABC_event']='V2F1'
    harmonysub.loc[(harmonysub.subject==s) & (harmonysub.HCAAABC_event.shift(1)=='V2F1') & (harmonysub.redcap_event.shift(2)=='V2') & (harmonysub.redcap_event.str.contains('F')),'HCAAABC_event']='V2F2'
    harmonysub.loc[(harmonysub.subject==s) & (harmonysub.HCAAABC_event.shift(1)=='V2F2') & (harmonysub.redcap_event.shift(3)=='V2') &( harmonysub.redcap_event.str.contains('F')),'HCAAABC_event']='V2F3'

#update the harmonized HCAAABC_event field
harmony.update(harmonysub.loc[(harmonysub.redcap_event.isin(['F1','F2','F3'])) & (harmony.Cohort=='HCA Long')][['HCAAABC_event']])
harmony.loc[harmony.HCAAABC_event.isin(['V1F1','V1F2','V1F3','V2F1','V2F2','V0','VZ','Covid','CR','A']),'IntraDB']='Behavioral Only'

#drop the non-visit events with ages <36 (was experimental and/or protocol deviation for non-visit events)
harmony=harmony.loc[~(harmony.event_age <36)]

#create output
sliceout = harmony[harmony.isna().sum(axis=1).ne(harmony.shape[1]-3)] #subtracting subject and redcap from total number of missings
#reorder columns
firstcols=['study','Cohort','HCAAABC_event','subject','redcap_event','redcap_event_name','PIN','event_age','race','ethnic_group','M/F','site','IntraDB','Actigraphy_Cobra','Curated_TLBX','Curated_Q','ASA_Totals']
lastcols=[col for col in sliceout.columns if col not in firstcols]
sliceout[firstcols+lastcols].drop(columns='PIN').to_csv(os.path.join(os.getcwd(),datarequestor+"/"+study+"_Slice_"+ date.today().strftime("%Y-%m-%d") + '.csv'),index=False)

slicevars=[i for i in list(sliceout.columns) if i not in ['redcap_event','subject','study']]

headerE=E.loc[(E['Variable / Field Name'].isin(['subject','redcap_event'])) & (E['Form / Instrument']=='SUBJECT INVENTORY AND BASIC INFORMATION')]
Evars=Evars.copy()
Evars['newname']=Evars['Variable / Field Name']
Evars.loc[Evars['NIH Toolbox Prefix in Slice'].isnull()==False,'newname']= Evars['NIH Toolbox Prefix in Slice']+'_'+Evars['Variable / Field Name']
D=pd.concat([headerE,Evars.loc[Evars['newname'].isin(slicevars)]])
D=D.drop(columns=['newname'])
D.to_csv(os.path.join(os.getcwd(),datarequestor+"/"+study+"_Slice_Dictionary_"+ date.today().strftime("%Y-%m-%d") + '.csv'),index=False)

#get the precise filenames downlaoded for the receipt
y = list(Evars['HCA Pre-Release File'].unique())+list(Evars['AABC Pre-Release File'].unique())
new=[]
for j in y:
    print(j)
    newlist=[]
    try:
        newlist=[j.replace("<date>.csv",'')]
    except:
        pass
    new=new+newlist
versionlist=[]
for i in os.listdir(os.path.join(os.getcwd(),datarequestor+"/downloadedfiles")):
    for n in new:
        if n.upper() in i.upper():
            versionlist=versionlist+[i]


#plots:
skip_plots=['subject','redcap_event','redcap_event_name','PIN','Actigraphy_Cobra']
plotlist=[vars for vars in list(sliceout.columns) if vars not in skip_plots]
if wantplots:
    if os.path.exists(os.path.join(os.getcwd(),datarequestor+"/plots")):
        pass
    else:
        os.mkdir(os.path.join(os.getcwd(),datarequestor+"/plots"))
    for i in plotlist:
        try:
            sliceout[i].hist()
            if i=='M/F':
                i='sex'
            plt.title(i)
            plt.savefig(os.path.join(os.getcwd(),datarequestor+"/plots/"+i))#, *, dpi='figure', format=None, metadata=None,
                    #bbox_inches=None, pad_inches=0.1,
                    #facecolor='auto', edgecolor='auto',
                   # backend=None, **kwargs
                   # )
            plt.show()
        except:
            pass


#write receipt
file_object = open(os.path.join(os.getcwd(),datarequestor+"/"+study+"_Data_Request_Receipt_"+date.today().strftime("%Y-%m-%d")+".txt"), "w")
print("***************************************************************",file=file_object)
print("",file=file_object)
print("Data Requested By:",datarequestor, file=file_object)
print("Request Fulfilled:",date.today().strftime("%Y-%m-%d"),file=file_object)
print("", file=file_object)
print("***************************************************************",file=file_object)
print("",file=file_object)
print("Instruments Requested:",file=file_object)
print("",file=file_object)
for i in InstRequest:
    print(i,file=file_object)
print("",file=file_object)
print("***************************************************************",file=file_object)
print("",file=file_object)
print("Derivatives Requested:",file=file_object)
print("",file=file_object)
for i in DerivativesRequested:
    print(i,file=file_object)
print("",file=file_object)
print("***************************************************************",file=file_object)
print("",file=file_object)
print("Bulk Data Requested:",file=file_object)
print("",file=file_object)
for i in BulkRequested:
    print(i,file=file_object)
    print("-- LETS TALK -- ",file=file_object)
print("",file=file_object)
print("***************************************************************",file=file_object)
print("",file=file_object)
print("Data Returned:",file=file_object)
print("",file=file_object)
shutil.copyfile(statsdir+statsfile,os.path.join(os.getcwd(),datarequestor+"/"+statsfile))
print("Most Recent Recruitment Report:",statsfile,file=file_object)
print("Slice:",study+"_Slice_"+ date.today().strftime("%Y-%m-%d") + '.csv',file=file_object)
print("Slice Dictionary:",study+"_Slice_Dictionary_"+ date.today().strftime("%Y-%m-%d") + '.csv',file=file_object)
print("Slice Univariate Descriptions:",study+"Slice_Univariate_Descriptions.txt",file=file_object)
print("Slice Univariate Plots:","/plots",file=file_object)
#point to new download location which is the same as the slice:
box = LifespanBox(cache=os.path.join(os.getcwd(),datarequestor))
if 'Cognition Factor Analysis' in DerivativesRequested:
    box.downloadFile(config['cogsHCAAABC'])
    box.downloadFile(1331283608435) #readme
    print("Cognition Factor Analysis: ",os.path.basename(box.downloadFile(config['cogsHCAAABC'])),file=file_object)
if 'Cardiometabolic Index and Allostatic Load' in DerivativesRequested:
    box.downloadFile(config['cardiosHCA'])
    f=box.downloadFile(config['cardiosHCA'])
    os.rename(f,os.path.join(os.getcwd(),datarequestor,"HCA_Cardiometabolic_Essentials.xlsx"))
    print("Cardiometabolic Index and Allostatic Load: HCA_Cardiometabolic_Essentials.xlsx",file=file_object)
    box.downloadFile(1287112770879)  #Readme
if 'Vasomotor Symptoms (Processed)' in DerivativesRequested:
    print("")
    print("NOT AVAILABLE: Processed Vasomotor Symptom Data", file=file_object)
if 'Imaging Derived Phenotypes' in DerivativesRequested:
    print("")
    print("Imaging Derived Phenotypes for HCA: https://wustl.box.com/s/kohbh1xvh93o35ztns1y8j9nwxw9twqi",file=file_object)

print("", file=file_object)
print("***************************************************************", file=file_object)
print("", file=file_object)
print("Slice created from the following files in the Pre-Release folder(s):",file=file_object)
print("",file=file_object)
for i in versionlist:
    print(i,file=file_object)
print("", file=file_object)
print("Links:",file=file_object)
print("", file=file_object)
print("AABC Pre-Release Folder in Box: https://wustl.box.com/s/9gnrbyq7fybw0wtd82zfoagki2d5uky1", file=file_object)
print("HCA Pre-Release Folder in Box: https://wustl.box.com/s/9gnrbyq7fybw0wtd82zfoagki2d5uky1", file=file_object)
print("Encyclopedia: https://wustl.box.com/s/csumk9o2cir3mniyp59wtb735kz51hqc", file=file_object)
print("", file=file_object)
file_object.close()

distrib_object = open(os.getcwd()+datarequestor+"/"+study+"_Slice_Univariate_Descriptions.txt", "w")
print("Slice_Univariate_Descriptions:",file=distrib_object)
print("",file=distrib_object)
for i in [j for j in sliceout.columns if j not in skip_plots]:
    print("************", file=distrib_object)
    print(sliceout[i].describe(),file=distrib_object)

print("",file=distrib_object)
print("***************************************************************",file=distrib_object)
distrib_object.close()

##################################################################################################
##################################################################################################
#clean up
#remove the downloaddir:
shutil.rmtree(os.path.join(os.getcwd(),datarequestor+"/downloadedfiles"))
