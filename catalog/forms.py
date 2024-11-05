from django import forms
from .models import secUser, SecUserApprove, UserRequest, ExcelUpload
from django.contrib.auth.forms import PasswordChangeForm
from datetime import datetime
from .models import Company


class NewReqForm(forms.Form):
    req_date = forms.DateField(help_text="date 필드")
    req_text = forms.CharField(max_length=100)

    def clean_date(self):
        data = self.cleaned_data['req_date']

        # Remember to always return the cleaned data.
        return data


class RequestForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RequestForm, self).__init__(*args, **kwargs)
        self.fields['ip_address'].label = 'IP 주소'
        self.fields['ip_address'].widget.attrs.update({
            'placeholder': '요청자의 IP 주소를 입력하세요',
            'class': 'form-control',
            'autofocus': True,
        })

    class Meta:
        model = UserRequest
        fields = ('ip_address', 'memo')


class UserRequestForm(forms.ModelForm):
    class Meta:
        model = UserRequest
        fields = ['memo']


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = '기존 비밀번호'
        self.fields['old_password'].widget.attrs.update({
            'class': 'form-control',
            'autofocus': False,
        })
        self.fields['new_password1'].label = '새 비밀번호'
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
        })
        self.fields['new_password2'].label = '새 비밀번호 확인'
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
        })
        
        
        
#class ExcelUploadForm(forms.Form):
#    excel_file = forms.FileField()




COMPANY_CHOICES = [
    ('1001', '삼천리'),
    ('Company B', '삼천리 ENG'),
    ('Company C', '삼천리 ES'),
]

def get_year_month_choices():
    """현재 연도와 과거 5년까지의 연월을 드롭다운에 표시"""
    now = datetime.now()
    choices = [
        (f"{year}-{month:02d}", f"{year}-{month:02d}")
        for year in range(now.year, now.year - 6, -1)
        for month in range(1, 13)
    ]
    return choices

class ExcelUploadForm(forms.Form):
    #company_choices = [(company.code, company.name ) for company in Company.objects.all()]
    
    company = forms.ChoiceField(choices=COMPANY_CHOICES, label='회사명 선택', widget=forms.Select(attrs={'class': 'form-select'}))
    year_month = forms.ChoiceField(choices=get_year_month_choices(), label='실적 연월 선택', widget=forms.Select(attrs={'class': 'form-select'}))
    excel_file = forms.FileField(label='Select Excel File', widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    