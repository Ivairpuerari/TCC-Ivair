# Programa para extração de informações referentes à pacientes
# sobreviventes e mortos afim de gerar duas coleções de documentos.
# Ivair Puerari
# ivaair@hotmail.com
 
import postgresql
from collections import defaultdict
import csv

def insertAdmissionDeath(sql):
    sql = sql.format('1')
    rs = db.prepare(sql)
    for linha in rs:
        admissionDeath[linha[0]].append(linha[1])

def insertAdmissionLife(sql):
    sql = sql.format('0')
    rs = db.prepare(sql)
    for linha in rs:
        admissionLife[linha[0]].append(linha[1])

def buildCSV(fileName, dicAdmissions):    
    row = ''
    i = 0
    with open(fileName, mode='w', newline='') as admission_file:
        admission_writer = csv.writer(admission_file)
        for key, registers in dicAdmissions.items():
            for data in registers: 
                row = row + ' ' + str(data)      
            admission_writer.writerow({row})
            row = ''
        admission_file.close()

try:
    
    db = postgresql.open(user = 'postgres', database = 'mimic', port = 5432, password = 'postgres')
    
    admissionDeath  = defaultdict(list)
    admissionLife = defaultdict(list)
    
    sql = 'SELECT ' \
    +'hadm_id, '\
    +'diagnosis '\
    +'FROM admissions '\
    +'WHERE admissions.hospital_expire_flag = {}'

   
    
    insertAdmissionDeath(sql)
    insertAdmissionLife(sql)

    sql = 'SELECT ' \
    +'admissions.hadm_id,' \
    +'d_icd_diagnoses.long_title '\
    +'FROM admissions ' \
    +'JOIN diagnoses_icd on diagnoses_icd.hadm_id = admissions.hadm_id ' \
    +'JOIN d_icd_diagnoses on d_icd_diagnoses.icd9_code = diagnoses_icd.icd9_code '\
    +'WHERE admissions.hospital_expire_flag = {}'
	
    insertAdmissionDeath(sql)
    insertAdmissionLife(sql)

       
    sql =  'SELECT '\
    +'admissions.hadm_id, '\
    +'d_icd_procedures.long_title '\
    +'FROM admissions '\
    +'JOIN procedures_icd ON procedures_icd.hadm_id = admissions.hadm_id '\
    +'JOIN d_icd_procedures ON d_icd_procedures.icd9_code = procedures_icd.icd9_code '\
    +'WHERE admissions.hospital_expire_flag = {}'
    
    insertAdmissionDeath(sql)
    insertAdmissionLife(sql)
   
   
    sql = 'SELECT '\
    +'admissions.hadm_id, '\
    +'noteevents.text ' \
    +'FROM admissions '\
    +'JOIN noteevents ON noteevents.hadm_id = admissions.hadm_id '\
    +'WHERE admissions.hospital_expire_flag = {}'
    
    insertAdmissionDeath(sql)
    insertAdmissionLife(sql)


    buildCSV('admissionDeath.csv', admissionDeath)
    buildCSV('admissionLife.csv', admissionLife)
    
    
    
finally:
    db.close()
