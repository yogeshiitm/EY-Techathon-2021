from .models import MedicalModel
from django.db.models import Q


def get_list(phase,state,district):
    if phase == 1:
        p1_users = MedicalModel.objects.filter(occupation = 'H').order_by('-age','-illness_score').filter(state = state, district = district, vaccination_status = '')
        # print('phase1\n')
        # print(p1_users)
        return p1_users
        

    elif phase == 2:
        p1_users = MedicalModel.objects.filter(occupation = 'H').filter(state = state, district = district, vaccination_status = '')
        users = MedicalModel.objects.filter(Q(age__gte=65) | Q(illness_score__gte=5) | Q(occupation = 'EPS') | Q(occupation = 'FAS') | Q(occupation = 'GS') | (Q(occupation = 'IM') & Q(work_status = 1))).filter(state = state, district = district, vaccination_status = '')
        p2_users = users.difference(p1_users).order_by('-age','-illness_score')
        # print(p1_users)
        # print(users)
        # print(p2_users)
        return p2_users
    
    elif phase == 3:
        p1_users = MedicalModel.objects.filter(occupation = 'H').filter(state = state, district = district, vaccination_status = '')
        p2_users = MedicalModel.objects.filter(Q(age__gte=65) | Q(illness_score__gte=5) | Q(occupation = 'EPS') | Q(occupation = 'FAS') | Q(occupation = 'GS') | (Q(occupation = 'IM') & Q(work_status = 1))).filter(state = state, district = district, vaccination_status = '')
        users = MedicalModel.objects.filter((Q(age__lte=64) & Q(no_illness__gte=2.5)) | ((Q(occupation ='C') | Q(occupation ='TSL') | Q(occupation ='FH') | Q(occupation ='RB') | Q(occupation ='TP') | Q(occupation ='OS') | Q(occupation ='DHC')) & Q(work_status =1))).filter(state = state, district = district, vaccination_status = '')
        p3_users = users.difference(p2_users).difference(p1_users).order_by('-illness_score','economy_score')
        # print(p1_users)
        # print(p2_users)
        # print(users)
        # print(p3_users)
        return p3_users
    
    elif phase == 4:
        p1_users = MedicalModel.objects.filter(occupation = 'H').filter(state = state, district = district, vaccination_status = '')
        p2_users = MedicalModel.objects.filter(Q(age__gte=65) | Q(illness_score__gte=5) | Q(occupation = 'EPS') | Q(occupation = 'FAS') | Q(occupation = 'GS') | (Q(occupation = 'IM') & Q(work_status = 1))).filter(state = state, district = district, vaccination_status = '')
        p3_users = MedicalModel.objects.filter((Q(age__lte=64) & Q(no_illness__gte=2.5)) | ((Q(occupation ='C') | Q(occupation ='TSL') | Q(occupation ='FH') | Q(occupation ='RB') | Q(occupation ='TP') | Q(occupation ='OS') | Q(occupation ='DHC')) & Q(work_status = 1))).filter(state = state, district = district, vaccination_status = '')

        users1 = MedicalModel.objects.filter(Q(age__lte=64) & Q(no_illness=0) & ((Q(occupation= 'NA') | Q(occupation='U')) & Q(work_status = 1))).filter(state = state, district = district, vaccination_status = '')
        p4_users1 = users1.difference(p3_users).difference(p2_users).difference(p1_users)
        print('phase4\n')
        print(p1_users)
        print(p2_users)
        print(p3_users)
        print(users1)

        users2 = MedicalModel.objects.filter(Q(age__lte=64) & Q(no_illness=0) & Q(work_status=2)).filter(state = state, district = district, vaccination_status = '')
        p4_users2 = users2.difference(p3_users).difference(p2_users).difference(p1_users)

        p4_users = p4_users1.union(p4_users2).order_by('work_status','-illness_score')
        #p4_users = (p4_users1 | p4_users2).distinct().order_by('work_status','-illness_score')

        print(p1_users)
        print(p2_users)
        print(p3_users)
        print(users2)

        print('\n',p4_users1)
        print('\n',p4_users2)
        print('\n',p4_users)

        return p4_users




        