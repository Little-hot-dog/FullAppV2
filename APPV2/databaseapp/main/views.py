from http.client import responses

from django.shortcuts import render, redirect
from django.http import HttpResponse
import requests
import json

from .forms import FilterForm, ExcelUploadForm, CriticalPointForm, UpdatePCForm

from datetime import datetime

import logging
logger = logging.getLogger(__name__)


def fetch_data_from_fastapi(params):
    api_url = "http://127.0.0.1:8000/get-filtered-system-info/"
    # logger.debug(f"Sending request to {api_url} with params: {params}")
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        return response.json()
    # logger.error(f"Error: Received status code {response.status_code}")
    return []

def index(request):
    form = FilterForm(request.GET or None)
    sys_info_list = []
    # problematic_pcs = []
    params = {}
    if form.is_valid():
        # logger.debug("Form is valid. Processing data...")
        
        if form.cleaned_data['id']:
            params['id'] = form.cleaned_data['id'].split(',')
        if form.cleaned_data['hosts']:
            params['hosts'] = form.cleaned_data['hosts'].split(',')
        if form.cleaned_data['params']:
            params['params'] = form.cleaned_data['params'].split(',')
        if form.cleaned_data['values']:
            params['values'] = form.cleaned_data['values'].split(',')
        if form.cleaned_data['start_date']:
            params['start_date'] = form.cleaned_data['start_date']
        if form.cleaned_data['end_date']:
            params['end_date'] = form.cleaned_data['end_date']


    sys_info_list = fetch_data_from_fastapi(params)
        #critical points
        # critical_points = fetch_critical_points()
        # problematic_pcs = analyze_critical_points(sys_info_list, critical_points)
        #critical points

    return render(request, 'main/index.html', {'form': form, 'sys_info_list': sys_info_list})

    # return render(request, 'main/index.html', {'form': form, 'sys_info_list': sys_info_list, 'problematic_pcs': problematic_pcs})

def fetch_actual_data_from_fastapi():
    api_url = "http://127.0.0.1:8000/get-actual-system-info/"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return []

def update_pc_list(request):
    params = []
    all_sys_info_list = fetch_actual_data_from_fastapi()
    last = ""
    sys_info_list = []
    for item in all_sys_info_list:
        if last != item['host']:
            sys_info_list.append(item)
        last = str(item['host'])
    return render(request, 'main/update_pc_list.html', {'sys_info_list': sys_info_list})

def fetch_actual_pc(id_raw):
    api_url = f"http://127.0.0.1:8000/get-system-info/{id_raw}"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.text
    return []

def update_pc(request, id_raw): 
    if request.method == 'POST':
        form = UpdatePCForm(request.POST)
        if form.is_valid():


            data = json.loads(form.cleaned_data['data'])
            print(form.cleaned_data['data'])
            print(data)


            api_url = f"http://127.0.0.1:8000/update-pc/{id_raw}"
            response = requests.put(api_url, json={"data": data})

            if response.status_code == 200:
                logger.debug("Critical point successfully updated.")
                return redirect('update_pc_list')
            else:
                logger.error(f"Error: Received status code {response.status_code}")
                return render(request, 'main/update_pc.html', {'form': form, 'error': 'Какая-то ошибка'})
    else:
        actual_pc = fetch_actual_pc(id_raw)
        form = UpdatePCForm(initial={'data': actual_pc})
        # form = UpdatePCForm()
    return render(request, 'main/update_pc.html', {'form': form, 'id_raw': id_raw})

def problem_pc_list(request):
    form = FilterForm(request.GET or None)
    problematic_pcs = []
    params = {}
    if form.is_valid():
        # logger.debug("Form is valid. Processing data...")
        
        if form.cleaned_data['id']:
            params['id'] = form.cleaned_data['id'].split(',')
        if form.cleaned_data['hosts']:
            params['hosts'] = form.cleaned_data['hosts'].split(',')
        if form.cleaned_data['params']:
            params['params'] = form.cleaned_data['params'].split(',')
        if form.cleaned_data['values']:
            params['values'] = form.cleaned_data['values'].split(',')
        if form.cleaned_data['start_date']:
            params['start_date'] = form.cleaned_data['start_date']
        if form.cleaned_data['end_date']:
            params['end_date'] = form.cleaned_data['end_date']

    sys_info_list = fetch_data_from_fastapi(params)

    critical_points = fetch_critical_points()
    problematic_pcs = analyze_critical_points(sys_info_list, critical_points)

 

    return render(request, 'main/problem_pc_list.html', {'form': form, 'problematic_pcs': problematic_pcs})

def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            files = {'file': (excel_file.name, excel_file, excel_file.content_type)}

            api_url = "http://127.0.0.1:8000/upload-excel/"
            response = requests.post(api_url, files=files)

            if response.status_code == 200:
                logger.debug("File successfully uploaded and processed.")
                return redirect('index')
            else:
                logger.error(f"Error: Received status code {response.status_code}")
                return render(request, 'main/upload_excel.html', {'form': form, 'error': 'Failed to upload file'})
    else:
        form = ExcelUploadForm()

    return render(request, 'main/upload_excel.html', {'form': form})

def fetch_critical_points():
    api_url = "http://127.0.0.1:8000/critical-points/"
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Error: Received status code {response.status_code}")
    return []

def manage_critical_points(request):
    critical_points = fetch_critical_points()

    if request.method == 'POST':
        form = CriticalPointForm(request.POST)
        if form.is_valid():
            data = {
                "param": form.cleaned_data['param'],
                "check_type": form.cleaned_data['check_type'],  
                "min_value": form.cleaned_data['min_value'],
                "max_value": form.cleaned_data['max_value'],
                "exact_value": form.cleaned_data['exact_value'],
                "measure_of_calculation": form.cleaned_data['measure_of_calculation'], 
                "day_count": form.cleaned_data['day_count'],
                "string_value": form.cleaned_data['string_value']
            }
            api_url = "http://127.0.0.1:8000/critical-points/"
            response = requests.post(api_url, json=data)
      
            if response.status_code == 200:
                logger.debug("Critical point successfully added.")
                return redirect('manage_critical_points')
            else:
               
                logger.error(f"Error: Received status code {response.status_code}")
                return render(request, 'main/manage_critical_points.html', {'form': form, 'critical_points': critical_points, 'error': 'Failed to add critical point'})
    else:
        form = CriticalPointForm()
    
    return render(request, 'main/manage_critical_points.html', {'form': form, 'critical_points': critical_points})

def update_critical_point(request, param):
    if request.method == 'POST':
        form = CriticalPointForm(request.POST)
        if form.is_valid():
            data = {
                "param": form.cleaned_data['param'],
                "check_type": form.cleaned_data['check_type'],  
                "min_value": form.cleaned_data['min_value'],
                "max_value": form.cleaned_data['max_value'],
                "exact_value": form.cleaned_data['exact_value'],
                "measure_of_calculation": form.cleaned_data['measure_of_calculation'], 
                "day_count": form.cleaned_data['day_count'],
                "string_value": form.cleaned_data['string_value']
            }
            api_url = f"http://127.0.0.1:8000/critical-points/{param}"
            response = requests.put(api_url, json=data)

            if response.status_code == 200:
                logger.debug("Critical point successfully updated.")
                return redirect('manage_critical_points')
            else:
                logger.error(f"Error: Received status code {response.status_code}")
                return render(request, 'main/update_critical_point.html', {'form': form, 'error': 'Failed to update critical point'})
    else:
        critical_points = fetch_critical_points()
        initial_data = next((cp for cp in critical_points if cp['param'] == param), None)
        form = CriticalPointForm(initial=initial_data)

    return render(request, 'main/update_critical_point.html', {'form': form, 'param': param})

def delete_critical_point(request, param):
    api_url = f"http://127.0.0.1:8000/critical-points/{param}"
    response = requests.delete(api_url)

    if response.status_code == 200:
        logger.debug("Critical point successfully deleted.")
        return redirect('manage_critical_points')
    else:
        logger.error(f"Error: Received status code {response.status_code}")
        return render(request, 'main/manage_critical_points.html', {'error': 'Failed to delete critical point'})

def analyze_critical_points(sys_info_list, critical_points):
    problematic_pcs = []
    # print(f'Весь sys_info_list {sys_info_list}')
    for pc in sys_info_list:
        issues = []
        # logger.debug(f"Analyzing PC: {pc}")
        for criterion in critical_points:
            
            param_value = None

            # Найти значение параметра для текущего ПК
            if pc['param'] == criterion['param']:
                param_value = pc['value']
                print(f'нашел критический параметр: {pc['param']}')

            # Если значение параметра в таблцие не пустое
            if param_value is not None:
                #Если выбрали границы
                if criterion['check_type'] == 'borders':
                    value = float(param_value)
                    
                    #Если выбрали GB
                    if criterion['measure_of_calculation'] == 'GB':
                        value = float(param_value.replace(' GB', ''))
                    else:
                        value = float(param_value)


                    if (criterion['min_value'] is not None and value < criterion['min_value']) or \
                        (criterion['max_value'] is not None and value > criterion['max_value']):
                        issues.append({'param': criterion['param'],
                                       'expected': criterion,
                                       'actual': param_value})
                

                #Если выбрали точное значение 
                elif criterion['check_type'] == 'exact_value':
                    if criterion['measure_of_calculation'] == 'GB':
                        value = float(param_value.replace(' GB', ''))
                    else:
                        value = float(param_value)

                    print(f"Неправильное значение {pc['param']} = {value}")

                    if (criterion['exact_value'] is not None and value != criterion['exact_value']):
                        issues.append({'param': criterion['param'],
                                       'expected': criterion,
                                       'actual': param_value})

                #Если выбрали точное значение строки
                elif criterion['check_type'] == 'string_value':
                    value = str(param_value)
                    print(f"Неправильное значение {pc['param']} = {value}")


                    # if (criterion['string_value'] is not None and value != criterion['string_value']):
                    if (criterion['string_value'] is not None and value.find(str(criterion['string_value']))) == -1:

                        issues.append({'param': criterion['param'],
                                       'expected': criterion,
                                       'actual': param_value})

                #Если выбрали кол-во дней до сегодняшнего  
                elif criterion['check_type'] == 'day_count':
                    value = datetime.now().date() - datetime.strptime(param_value.split(' ')[0], "%d.%m.%Y").date()
                    value = value.days
                    print(f"Неправильное значение {pc['param']} = {param_value}")
                    if (criterion['day_count']) is not None and value >= criterion['day_count']:
                        issues.append({'param': criterion['param'],
                                       'expected': criterion,
                                       'actual': param_value})
                        
                
                
        if issues:
            problematic_pcs.append({
                'host': pc['host'],
                'issues': issues,
                'value': pc['value']

            })

    return problematic_pcs