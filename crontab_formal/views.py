from django.shortcuts import render, redirect
from . import forms
from .read_program_base_info import ReadProgramsInfo

# Create your views here.


def insert(request):
    if request.method == 'POST':
        form = forms.Path(request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            path = form.save()
            ReadProgramsInfo(path).get_programs_info_list()
    else:
        form = forms.Path()
    return render(request, 'rcrontab_formals/insert.html', {'form': form})

#def insert(request):
#    if request.method == 'POST':
#        form = forms.ScriptBaseInfo(request.POST)
#        if form.is_valid():
#            print(request.POST)
#    else:
#        form = forms.ScriptBaseInfo()
#    return render(request, 'rcrontab_formals/insert.html', {'form': form})


