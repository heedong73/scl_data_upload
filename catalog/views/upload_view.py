from django.shortcuts import render, redirect
from catalog.forms import ExcelUploadForm
from catalog.models import ExcelUpload, ExcelUploadRecord
import pandas as pd
from django.utils.timezone import now
import urllib3
import requests
import json, time

def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            company = form.cleaned_data['company']
            year_month = form.cleaned_data['year_month']
            upload_result = []
            upload_count = 0
            try:
                # pandas를 사용해 엑셀 파일 읽기
                df = pd.read_excel(excel_file, engine='openpyxl')
                
                #request.session['upload_result'] = df.to_dict(orient='records')
                
                request.session['company'] = company
                request.session['year_month'] = year_month

                # 각 행을 Product 모델로 저장
                for _, row in df.iterrows():
                    row_val_ = {
                        'company':row['회사 코드'],
                        'yyyymm': row['월'],
                        'account': row['계정 코드'],
                        'account_name': row['계정 이름'],
                        'account_value': row['실적'],
                    }
                    upload_result.append(row_val_)
                    upload_count += 1
                
                request.session['upload_result'] = upload_result
                request.session['upload_count'] = upload_count


                return redirect('upload_commit')
                         #render(request,'upload_result.html', data)  # 성공 페이지로 리다이렉트
            except Exception as e:
                return render(request, 'upload.html', {
                    'form': form,
                    'error': f'파일 처리 중 오류가 발생했습니다: {e}'
                })
    else:
        form = ExcelUploadForm()
    return render(request, 'upload.html', {'form': form})
    
    
def upload_success(request):

    text_response = request.session.get('api_result')

    data = {
        'upload_result': text_response,
    }
    return render(request, 'success.html', data)


def call_api(request):
    urllib3.disable_warnings()

    login_body = {
        "username":"sam_api",
        "password":"tlrhfmgmlend@@00"
        }
    login_url = "https://dm1-apse.informaticacloud.com/saas/public/core/v3/login"
    login_headers = {'Content-Type':'application/json; Accept:application/json'}
    login_response = requests.post(login_url, data=json.dumps(login_body), headers=login_headers, verify=False)
    login_response_list = login_response.json()
    Session_ID = login_response_list["userInfo"]["sessionId"]
    print('Session_ID : '+ Session_ID)
    task_url = "https://apse1.dm1-apse.informaticacloud.com/"
    task_api = "active-bpel/rt/REST_TEST_TASKFLOW"
    task_headers = {
        'Content-Type':'application/json',
        'Accept':'application/json', 
        'IDS-SESSION-ID':Session_ID
        }
    task_response = requests.post(task_url+task_api, headers=task_headers, verify=False)
    task_response_json = task_response.json()
    task_run_id = task_response_json["RunId"]
    print('RunId : '+ task_run_id)
    status_url = "https://apse1.dm1-apse.informaticacloud.com/active-bpel/services/tf/status/" + task_run_id
    status_response = requests.get(status_url, headers=task_headers, verify=False)
    if status_response.status_code == 200:
        print("API 호출 성공:", status_response.json())
        while True:
            # 예시 URL입니다. 실제 API URL로 변경하세요.
            response = requests.get(status_url, headers=task_headers, verify=False)
            
            if response.json().get('status') == 'SUCCESS':
                request.session['api_result'] = response.json()['status']
                print("작업이 성공했습니다!")
                break
            else:
                print("작업이 아직 완료되지 않았습니다. 3초 후 다시 시도합니다.")
                time.sleep(3)
    else:
        print("API 호출 실패:", status_response.status_code)
        request.session['api_result'] = status_response.json()['status']

    return status_response.status_code


def excel_upload_result(request):
    upload_result = ExcelUpload.objects.all()

    p_cnt = ExcelUpload.objects.all().count()


    data = {
        'upload_result': upload_result,
        'upload_count': p_cnt,
    }

    return render(request, 'upload_result.html', data)

def excel_upload_history(request):
    upload_history = ExcelUploadRecord.objects.filter(uploaded_by=request.user)
    print(upload_history)
    data = {
        'upload_history': upload_history,
    }

    return render(request, 'upload_history.html', data)


    
def commit_excel_upload(request):
    upload_result = request.session.get('upload_result', [])
    upload_count = request.session.get('upload_count', '')
    company = request.session.get('company', '')
    year_month = request.session.get('year_month', '')

    if request.method == 'POST':
        # 업로드 기록 생성
        upload_record = ExcelUploadRecord.objects.create(
            company=company,
            year_month=year_month,
            uploaded_by=request.user,
            uploaded_at=now(),
            num_record=upload_count
        )
        print(upload_record)

        # 세션의 데이터 저장
        for row in upload_result:
            ExcelUpload.objects.create(
                company=row['company'],
                yyyymm=row['yyyymm'],
                account=row['account'],
                account_name=row['account_name'],
                account_value=row['account_value'],
                upload_record=upload_record
            )

        # 세션 데이터 정리 후 성공 페이지로 이동
        if 'upload_result' in request.session:
            del request.session['upload_result']

        call_api(request) # 인포매티카 API 호출

        return redirect('upload_success')

    return render(request, 'upload_result.html', {
        'upload_result': upload_result,
        'upload_count': upload_count,
        'company': company,
        'year_month': year_month
        
    })

def upload_checker(company, yyyymm):
    # 특정 연월 데이터가 존재하는지 확인
    exists = ExcelUploadRecord.objects.filter(company=company).filter(year_month=yyyymm).exists()
    return exists


def excel_upload_detail(request, pk):
    upload_data= ExcelUpload.objects.filter(upload_record=pk)

    data = {
        'upload_data': upload_data,
    }

    return render(request, 'upload_detail.html', data)