from django import forms

class ContactForm(forms.Form):
        DEPARTMENT_CHOICES = (
                ('BILL', 'Billing'),
                ('SUPP', 'Support'),
                ('SALE', 'Sales'),
                ('AFFI', 'Affiliates'),
                ('MANA', 'Management'),
        )

	department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, widget=forms.Select(attrs={'class':'form-control'}))
	subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class':'form-control'}))
	message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'rows': 4}))
