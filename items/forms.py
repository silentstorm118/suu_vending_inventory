from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'level_in_backroom', 'min_level']
        labels = {
            'name': "Item Name",
            'level_in_backroom': 'Initial Backroom Stock',
            'min_level': 'Minimum Stock Level',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter item name'}),
            'level_in_backroom': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_level': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def clean_level_in_backroom(self):
        value: int = self.cleaned_data.get('level_in_backroom')
        if value is not None and value < 0:
            raise forms.ValidationError("Initial stock cannot be negative.")
        return value
