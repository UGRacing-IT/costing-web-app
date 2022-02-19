from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse

from tool.models import *
from django.db.models import Sum, F
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from tool.forms import *
from tool.consts import USER_RANKS

########################################## Base ###############################################

# TODO: Stop logging out breaking the web app
def home(request):
    context_dict = {}

    car_list = Car.objects.filter(archived = False).order_by('carYear')
    archived_car_list = Car.objects.filter(archived = True).order_by('carYear')
    user_account, user_rank = get_user_details(request)

    context_dict['test'] = 'test'
    context_dict['cars'] = car_list
    context_dict['archived_cars'] = archived_car_list
    context_dict['user_rank'] = user_rank
    context_dict["display_add_car"] = False
    context_dict["display_edit_car"] = False

    if user_account.rank >= 4:
        context_dict["display_add_car"] = True
        context_dict["display_edit_car"] = True

    response = render(request, 'tool/home.html', context=context_dict)
    return response


def about(request):
    # information page
    context_dict = {}
    return render(request, 'tool/about.html', context=context_dict)

########################################## Displays ###############################################


def car_display(request, car_slug):
    context_dict = {}
    try:
        user_account, user_rank = get_user_details(request)
        car = Car.objects.get(carSlug=car_slug)
        systems = System.objects.filter(carID=car)

        context_dict['car'] = car
        context_dict['systems'] = systems

        context_dict['archived'] = car.archived
        context_dict['user_rank'] = user_rank
        context_dict['access_bool'] = {}
        context_dict['th_bool'] = {}
        access_bool = {}
        th_bool = {}

        if car.archived == True:
            context_dict['display_edit_system'] = False
            context_dict['display_add_system'] = False
            context_dict['display_edit_subteam'] = False
        elif user_account.rank >= 4:
            context_dict['display_edit_system'] = True
            context_dict['display_add_system'] = True
            context_dict['display_edit_subteam'] = True
        elif user_account.rank >= 4:
            # If assigned to system check
            for system in systems:
                subteams = Subteam.objects.filter(systems=system)
                found = False
                th = False
                for subteam in subteams:
                    if TeamLinking.objects.filter(user=user_account, subteam=subteam).exists():
                        found = True
                    if TeamLinking.objects.filter(user=user_account, subteam=subteam, teamHead=True).exists():
                        th = True
                    else:
                        context_dict['display_edit_system'] = False
                    
                    context_dict['display_add_system'] = False
                    context_dict['display_edit_subteam'] = False
                if found:
                    if th:
                        access_bool[system.systemID] = (True, True)
                    else:
                        access_bool[system.systemID] = (True, False)
                else:
                    access_bool[system.systemID] = (False, False)


        context_dict['access_bool'] = access_bool

    except Car.DoesNotExist:
        context_dict['car'] = None

    return render(request, 'tool/car_display.html', context=context_dict)


def system_display(request, system_slug, car_slug):
    context_dict = {}
    try:
        system = System.objects.get(systemSlug=system_slug)
        car = Car.objects.get(carSlug=car_slug)
        assemblys = Assembly.objects.filter(systemID=system)

        output = {}
        for assembly in assemblys:
            parts = Part.objects.filter(assemblyID=assembly.assemblyID)
            output[assembly] = {}
            for part in parts:
                pmfts = PMFT.objects.filter(partID=part.partID)
                output[assembly][part] = list(pmfts)

        context_dict['system'] = system
        context_dict['car'] = car
        context_dict['assemblys'] = assemblys
        context_dict['output'] = output

    except System.DoesNotExist:
        context_dict['System'] = None

    return render(request, 'tool/system_display.html', context=context_dict)


    ########################################## Forms ###############################################


def add_car(request, car_slug=None):
    context_dict = {}
    car = None
    context_dict['car'] = car
    
    '''
    # user verification stuff for later (not an outer if(verifed)) else print (form.errors) and  return HttpResponse("This page is exclusively for cost heads")
    # get user ID
    userID = request.user.get_username()
    # get user object
    users = User.objects.filter(username=userID)
    # get if user is verified
    verified = UserAccount.objects.filter(user__in=users, verified=True)
    '''

    if car_slug:
        car = get_object_or_404(Car, carSlug=car_slug)
        form = CarForm(request.POST, instance=car)
    else:
        form = CarForm(request.POST)
    
    if request.method == 'POST' and form.is_valid():
        newCar = form.save(commit=False)
        if not car_slug:
            newCar.carID = newCar.carName + str(newCar.carYear)
        newCar.save()
        return redirect(reverse('tool:home'))

    context_dict['form'] = form
    if car_slug:
        context_dict['edit'] = True
        context_dict['car'] = car
    else:
        context_dict['edit'] = False

    return render(request, 'tool/add_car.html', context_dict)
  
  
def add_system(request, car_slug, system_slug=None):
    context_dict = {}
    context_dict['car'] = Car.objects.get(carSlug=car_slug)
    system = None
    context_dict['system'] = system

    if system_slug:
        system = get_object_or_404(System, systemSlug=system_slug)
        form = SystemForm(request.POST, instance=system)
    else:
        form = SystemForm(request.POST)

    if request.method == 'POST' and form.is_valid():
        newSystem = form.save(commit=False)
        if not system_slug:
            newSystem.carID = Car.objects.get(carSlug=car_slug)
        newSystem.save()
        return redirect(reverse('tool:car_display', args=[car_slug]))

    context_dict['form'] = form
    if system_slug:
        context_dict['edit'] = True
        context_dict['system'] = system
    else:
        context_dict['edit'] = False

    return render(request, 'tool/add_system.html', context_dict)


def add_assembly(request, car_slug, system_slug, assembly_slug=None):
    context_dict = {}
    context_dict['car'] = Car.objects.get(carSlug=car_slug)
    context_dict['system'] = System.objects.get(systemSlug=system_slug)
    assembly = None
    context_dict['assembly'] = assembly

    if assembly_slug:
        assembly = get_object_or_404(Assembly, assemblySlug=assembly_slug)
        form = AssemblyForm(request.POST, instance=assembly)
    else:
        form = AssemblyForm(request.POST)

    if request.method == 'POST' and form.is_valid():
        newAssembly = form.save(commit=False)
        if not assembly_slug:
            newAssembly.systemID = System.objects.get(systemSlug=system_slug)
        newAssembly.save()
        return redirect(reverse('tool:system_display', args=[car_slug, system_slug]))

    context_dict['form'] = form
    if assembly_slug:
        context_dict['edit'] = True
        context_dict['assembly'] = assembly
    else:
        context_dict['edit'] = False
        
    return render(request, 'tool/add_assembly.html', context_dict)
  
 
def add_part(request, car_slug, system_slug, assembly_slug, part_slug=None):
    context_dict = {}
    car = Car.objects.get(carSlug=car_slug)
    system = System.objects.get(systemSlug=system_slug)
    assembly = Assembly.objects.get(assemblySlug=assembly_slug)

    context_dict['car'] = car
    context_dict['system'] = system
    context_dict['assembly'] = assembly

    if part_slug:
        part = get_object_or_404(Part, partSlug=part_slug)
        form = PartForm(request.POST, instance=part)
    else:
        form = PartForm(request.POST)

    if request.method == 'POST' and form.is_valid():
        newPart = form.save(commit=False)
        if not part_slug:
            newPart.assemblyID = Assembly.objects.get(assemblySlug=assembly_slug)
        newPart.save()
        return redirect(reverse('tool:system_display', args=[car_slug, system_slug]))

    context_dict['form'] = form
    if part_slug:
        context_dict['edit'] = True
        context_dict['part'] = part
    else:
        context_dict['edit'] = False

    return render(request, 'tool/add_part.html', context_dict)


def add_pmft(request, car_slug, system_slug, assembly_slug, part_slug):
    context_dict = {}
    
    part = Part.objects.get(partSlug=part_slug)
    context_dict['assemblySlug'] = assembly_slug
    context_dict['carSlug'] = car_slug
    context_dict['systemSlug'] = system_slug
    context_dict['part'] = part


    form = PMFTForm()
    if request.method == 'POST':
        form = PMFTForm(request.POST)
        if form.is_valid():
            newPMFT = form.save(commit=False)

            newPMFT = form.save(commit=False)
            newPMFT.partID = Part.objects.get(partSlug=part_slug)

            # save details
            newPMFT.save()
            return redirect(reverse('tool:home'))
        else:
            print(form.errors)

    return render(request, 'tool/add_pmft.html', {'form': form, 'context': context_dict})

    
def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        account_form = UserAccountForm(request.POST)
        if user_form.is_valid() and account_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            account = account_form.save(commit=False)
            account.user = user
            account.save()
            registered = True
        else:
            print(user_form.errors, account_form.errors)
    else:
        user_form = UserForm()
        account_form = UserAccountForm()
    
    return render(request,
                    'tool/register.html',
                    context={'user_form': user_form,
                                'account_form': account_form,
                                'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('tool:home'))
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details.")
    else:
        return render(request, 'tool/login.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('tool:home'))


########################################## Helper Functions ###############################################


def get_user_details(request):
    user_account = UserAccount.objects.get(pk=request.user)
    user_rank = USER_RANKS[user_account.rank]

    return user_account, user_rank
