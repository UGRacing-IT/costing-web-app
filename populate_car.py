import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'costing-web-app.settings')

import django
import pandas as pd
django.setup()
from django.core.files import File
from tool.models import *
from datetime import datetime
from pytz import utc
from django.contrib.auth.models import User




def populate():
    data= pd.read_csv('data.csv')
    
    Car = []
    for carID, car_df in data.groupby('carID'):
        #print(carID,car_df['carName'][0],car_df['carYear'][0])

        c= add_car(carID,car_df['carName'][0], car_df['carYear'][0])
        Car.append(c)

        System = []
        for systemName, sys_df in car_df.groupby('System'):
            print(systemName,carID,bool(sys_df['costed'].to_list()[0]))
            s=add_system(systemName,c, bool(sys_df['costed'].to_list()[0]))
            System.append(s)

            Assembly=[]
            for assemblyName, assembly_df in sys_df.groupby('Assembly'):
                #print('AN:',assemblyName)
                assemblyQuantity=1
                try:
                    a=add_assembly(assemblyName,s, assemblyQuantity)
                    Assembly.append(a)

                    Part=[]
                    for partName, part_df in assembly_df.groupby('Part'):

                        mB=part_df['M/B'].to_list()[0]
                        try:
                            if mB.lower() == 'm':
                                makeBuy=True
                                #print(partName,makeBuy,True)
                                pass
                            else:
                                makeBuy=False
                                pass

                            cost=part_df['Cost\n(per piece)'].to_list()[0]
                            cost=float(cost.split(' ')[1])
                            #cost=part_df['Cost\n(per piece)'].to_list()[0]
                            #cost=float(cost.split(' ')[1])
                            #Qt
                            Qt=part_df['Qt'].to_list()[0]
                            Qt=int(Qt)
                            #partCurrency
                            pC=part_df['partCurrency'].to_list()[0]
                            partC=part_df['Comments'].to_list()[0]
                                
                                
                            p=add_part(partName,a, makeBuy, cost,Qt,pC,partC)
                            Part.append(p)

                            PMFT = []
                            for pmftName, pmft_df in part_df.groupby('subtype'):

                                pmftC=pmft_df['Comments'].to_list()[0]
                                costp=pmft_df['Cost\n(per piece)'].to_list()[0]
                                costp=float(costp.split(' ')[1])
                                ppC=pmft_df['partCurrency'].to_list()[0]
                                #'Cost Comments'
                                pCC = pmft_df['Cost Comments'].to_list()[0]
                                pQt=part_df['Qt'].to_list()[0]
                                pQt=float(pQt)

                                pmft= pmft_df['P/M/F/T'].to_list()[0]
                                #print(pmftName,pmftC,costp,ppC,pCC,pQt,pmft)
                                #print(pmftName)
                                pm=add_pmft(pmftName,pmftC,costp,ppC,pCC,pQt,p,pmft)
                                PMFT.append(pm)
                        
                        except:
                            pass
                except Exception as e: 
                    print(e)
                    #print('Error',assemblyName)
                    #pass


def AddUserAccount(userName, email, pword, verified):
    user=User.objects.create_user(userName, email=email, password=pword)
    user.is_superuser=True
    user.is_staff=True
    user.save()
    u = UserAccount.objects.get_or_create(user=user, verified=verified)[0]
    u.user = user
    u.verified = verified
    u.save()
    return u

def add_car(carID,carName,carYear):


    c = Car.objects.get_or_create(carID=carID,carName=carName, carYear=carYear)[0]
    c.carName = carName
    c.carYear = carYear
    c.save()

    return c

def add_system(systemName,carID,costed):

    s = System.objects.get_or_create(systemName=systemName,carID=carID, costed=costed)[0]
    s.systemName = systemName
    s.carID = carID
    s.costed = costed
    s.save()

    return s

def add_assembly(assemblyName,systemID,assemblyQuantity):

    a = Assembly.objects.get_or_create(assemblyName=assemblyName,systemID=systemID, assemblyQuantity=assemblyQuantity)[0]
    a.assemblyName = assemblyName
    a.systemID = systemID
    a.assemblyQuantity = assemblyQuantity
    a.save()

    return a

def add_part(partName,assemblyID,makeBuy,partCost,partQuantity,partCurrency,partComment):

    p = Part.objects.get_or_create(partName=partName,assemblyID=assemblyID, makeBuy=makeBuy,partCost=partCost,partQuantity=partQuantity,partCurrency=partCurrency,partComment=partComment)[0]
    p.partName = partName
    p.assemblyID = assemblyID
    p.makeBuy = makeBuy
    p.partCost =partCost
    p.partQuantity = partQuantity
    p.partCurrency = partCurrency
    p.partComment = partComment
    p.save()

    return p

def add_pmft(pmftName,pmftComment,pmftCost,pmftCurrency,pmftCostComment,pmftQuantity,partID,pmftType):
    pm = PMFT.objects.get_or_create(pmftName=pmftName,pmftComment=pmftComment, pmftCost=pmftCost,pmftCurrency=pmftCurrency,pmftCostComment=pmftCostComment,pmftQuantity=pmftQuantity,partID=partID,pmftType=pmftType)[0]
    pm.pmftName = pmftName
    pm.pmftComment = pmftComment
    pm.pmftCost = pmftCost
    pm.pmftCurrency =pmftCurrency
    pm.pmftCostComment = pmftCostComment
    pm.partID = partID
    pm.pmftType = pmftType
    pm.save()

    return pm


def AddUserAccount(userName, email, pword, verified):
    user=User.objects.create_user(userName, email=email, password=pword)
    user.is_superuser=True
    user.is_staff=True
    user.save()
    u = UserAccount.objects.get_or_create(user=user, verified=verified)[0]
    u.user = user
    u.verified = verified
    u.save()
    return u


if __name__ == '__main__':
    print('Starting population script...')
    populate()
    print('Completed population script, exiting...')
