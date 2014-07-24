from django import forms

class AddZoneForm(forms.Form):
	domain = forms.CharField(max_length=100)
	ip = forms.CharField(max_length=100)

class AddRecordForm(forms.Form):
	# Valid record SELECT types
	VALID_TYPES = (
		('A', 'A'),
		('A6', 'A6'),
		('AAAA', 'AAAA'),
		('CNAME', 'CNAME'),
		('DNAME', 'DNAME'),
		('MX', 'MX'),
		('NS', 'NS'),
		('PTR', 'PTR'),
		('SRV', 'SRV'),
		('TXT', 'TXT'),
	)
	domain = forms.CharField(max_length=200)
	ttl = forms.IntegerField(label="TTL")	
	rtype = forms.ChoiceField(label="Record Type", choices=VALID_TYPES)
	record = forms.CharField(max_length=200)
	zone = forms.CharField(max_length=200)

class AddMxRecordForm(AddRecordForm):
	priority = forms.IntegerField()

class AddSrvRecordForm(AddRecordForm):
	priority = forms.IntegerField()
	weight = forms.IntegerField()
	port = forms.IntegerField()

class ZoneForm(forms.Form):
	zone = forms.CharField(max_length=200)
	
class DeleteRecordForm(ZoneForm):
	line = forms.IntegerField()
