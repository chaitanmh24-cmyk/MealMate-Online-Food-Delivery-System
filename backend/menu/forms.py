from django import forms
from .models import FoodItem, Category
from restaurants.models import Restaurant, Cuisine


class FoodItemAdminForm(forms.ModelForm):
    """
    Admin form for creating/editing FoodItems.
    Enforces the business rule: Pure-Veg restaurant cannot have Non-Veg items
    (catches the ValidationError from FoodItem.clean() and surfaces it nicely
    in the form).
    """

    class Meta:
        model = FoodItem
        fields = [
            'restaurant', 'category', 'cuisine', 'name',
            'description', 'price', 'food_type', 'image', 'is_available',
        ]
        widgets = {
            'restaurant':  forms.Select(attrs={'class': 'form-select'}),
            'category':    forms.Select(attrs={'class': 'form-select'}),
            'cuisine':     forms.Select(attrs={'class': 'form-select'}),
            'name':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Paneer Butter Masala'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short appetising description…'}),
            'price':       forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.50', 'placeholder': '₹ e.g. 250.00'}),
            'food_type':   forms.Select(attrs={'class': 'form-select'}),
            'image':       forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'food_type': 'Type (Veg / Non-Veg)',
            'image':     'Image URL',
        }

    def clean(self):
        cleaned_data = super().clean()
        restaurant = cleaned_data.get('restaurant')
        food_type  = cleaned_data.get('food_type')

        # Enforce Pure-Veg restaurant rule at form level for a user-friendly error
        if restaurant and food_type:
            if restaurant.restaurant_type == 'Veg' and food_type == 'Non-Veg':
                raise forms.ValidationError(
                    f'"{restaurant.name}" is a Pure-Veg restaurant and cannot serve Non-Veg items. '
                    'Please choose a different restaurant or change the food type to Veg.'
                )
        return cleaned_data
