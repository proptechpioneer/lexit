from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from news.models import NewsArticle
from datetime import date
import json

from .utils.corp_tax_calculator import corp_tax_calculator
from .utils.offshore_tax_calculator import offshore_tax_calculator
from .utils.tax_calculator import income_tax_calculator as tax_calculator
from .utils.sdlt_calculator import sdlt_calculator

# Simple CGT calculation function (inline)
def calculate_simple_cgt(current_value, purchase_price, growth_rate, years=10, ownership_type='individual'):
    """Simple CGT calculation for property growth scenarios"""
    future_value = current_value * ((1 + growth_rate) ** years)
    
    # Standard selling costs
    agency_fees = future_value * 0.015  # 1.5%
    legal_fees = 1500
    epc_costs = 5000
    total_selling_costs = agency_fees + legal_fees + epc_costs
    
    # Calculate gross gain
    gross_gain = future_value - purchase_price - total_selling_costs
    
    if gross_gain <= 0:
        return {
            'future_value': future_value,
            'cgt_liability': 0,
            'net_proceeds': future_value - total_selling_costs,
            'cgt_rate': 0,
            'gross_gain': gross_gain,
            'net_gain_after_cgt': future_value - total_selling_costs - current_value,
            'selling_costs': total_selling_costs
        }
    
    # Simple CGT calculation
    if ownership_type == 'company':
        # Corporation tax rates
        if gross_gain <= 50000:
            cgt_rate = 0.19
        else:
            cgt_rate = 0.25
    else:
        # Individual CGT rates (simplified)
        cgt_rate = 0.18  # Basic rate (could be 0.24 for higher rate)
        annual_exempt = 3000  # 2024/25 allowance
        taxable_gain = max(0, gross_gain - annual_exempt)
        gross_gain = taxable_gain
    
    cgt_liability = gross_gain * cgt_rate
    net_proceeds = future_value - total_selling_costs - cgt_liability
    net_gain_after_cgt = net_proceeds - current_value
    
    return {
        'future_value': future_value,
        'cgt_liability': cgt_liability,
        'net_proceeds': net_proceeds,
        'cgt_rate': cgt_rate,
        'gross_gain': gross_gain,
        'net_gain_after_cgt': net_gain_after_cgt,
        'selling_costs': total_selling_costs
    }

def calculate_nrat(property_obj, net_return_after_tax):
    """Calculate Net Return After Tax (NRAT) as a percentage of total cash deployed"""
    # Debug: Print input values
    print(f"\n=== NRAT CALCULATION DEBUG for {property_obj.property_name} ===")
    print(f"Input net_return_after_tax: £{net_return_after_tax}")
    print(f"Property ownership_status: {property_obj.ownership_status}")
    print(f"Property uk_resident: {property_obj.uk_resident}")
    print(f"Property deposit_paid: £{property_obj.deposit_paid}")
    print(f"Property purchase_price: £{property_obj.purchase_price}")
    print(f"Property date_of_purchase: {property_obj.date_of_purchase}")
    
    # Determine buyer type using the property's method
    buyer_type = property_obj.buyer_type_for_sdlt
    print(f"Determined buyer_type: {buyer_type}")
    
    # Calculate SDLT using the calculator - always treat as BTL property
    print(f"Calling SDLT calculator with:")
    print(f"  - purchase_date: {property_obj.date_of_purchase}")
    print(f"  - purchase_price: {int(property_obj.purchase_price)}")
    print(f"  - buyer_type: {buyer_type}")
    print(f"  - is_btl: True")
    
    sdlt_result = sdlt_calculator.calculate_sdlt(
        purchase_date=property_obj.date_of_purchase,
        purchase_price=int(property_obj.purchase_price),
        buyer_type=buyer_type,
        is_btl=True
    )
    
    print(f"SDLT calculation result: {sdlt_result}")
    
    # Extract SDLT amount (handle potential errors)
    sdlt_amount = Decimal(str(sdlt_result.get('sdlt', 0)))
    print(f"Extracted SDLT amount: £{sdlt_amount}")
    
    # Calculate total cash deployed
    total_cash_deployed = property_obj.deposit_paid + sdlt_amount
    print(f"Total cash deployed calculation:")
    print(f"  - Deposit paid: £{property_obj.deposit_paid}")
    print(f"  - SDLT amount: £{sdlt_amount}")
    print(f"  - Total cash deployed: £{total_cash_deployed}")
    
    # Calculate NRAT as percentage
    if total_cash_deployed > 0:
        nrat = (net_return_after_tax / total_cash_deployed) * 100
        print(f"NRAT calculation:")
        print(f"  - Net return after tax: £{net_return_after_tax}")
        print(f"  - Total cash deployed: £{total_cash_deployed}")
        print(f"  - NRAT = (£{net_return_after_tax} / £{total_cash_deployed}) * 100 = {nrat:.3f}%")
    else:
        nrat = Decimal('0')
        print(f"NRAT = 0% (total cash deployed is zero)")
    
    result = {
        'nrat': nrat,
        'sdlt_amount': sdlt_amount,
        'total_cash_deployed': total_cash_deployed,
        'sdlt_details': sdlt_result
    }
    
    print(f"Final NRAT result: {result}")
    print(f"=== END NRAT CALCULATION DEBUG ===\n")
    
    return result
from .models import Property
from .forms import PropertyForm

# Create your views here.

@login_required
def user_home(request):
    """Dashboard home page for logged-in users"""
    user = request.user
    
    # Get user profile information
    profile = getattr(user, 'profile', None)
    
    # Get user's properties
    properties = Property.objects.filter(owner=user)
    total_properties = properties.count()
    
    # Define standard metrics used in calculations
    vacancy_rate = Decimal('0.0385')  # 3.85%
    maintenance_rate = Decimal('0.035')  # 3.5%
    
    # Calculate dashboard stats
    total_weekly_rent = sum(prop.weekly_rent for prop in properties)
    total_annual_rent = total_weekly_rent * 52
    total_portfolio_value = sum(prop.estimated_market_value or 0 for prop in properties)
    
    # Calculate total equity across all properties
    total_equity = Decimal('0')
    for prop in properties:
        if prop.estimated_market_value:
            property_equity = prop.estimated_market_value
            if prop.has_mortgage and prop.outstanding_mortgage_balance:
                property_equity -= prop.outstanding_mortgage_balance
            total_equity += property_equity
    
    # Calculate average metrics
    total_nrat = Decimal('0')
    total_roe = Decimal('0')
    properties_with_nrat = 0
    properties_with_roe = 0
    
    for prop in properties:
        # Calculate basic property metrics for NRAT and ROE
        annual_rent = prop.weekly_rent * 52
        annual_vacancy_loss = annual_rent * vacancy_rate
        annual_gross_rent = annual_rent - annual_vacancy_loss
        
        # Calculate annual expenses
        annual_property_management_fees = annual_gross_rent * (prop.property_management_fees / 100)
        annual_service_charge = prop.service_charge
        annual_ground_rent = prop.ground_rent
        annual_other_annual_costs = prop.other_annual_costs
        annual_maintenance = annual_gross_rent * maintenance_rate
        total_annual_expenses = (annual_property_management_fees + annual_service_charge +
                               annual_ground_rent + annual_other_annual_costs + annual_maintenance)
        
        # Calculate net operating income
        net_operating_income = annual_gross_rent - total_annual_expenses
        
        # Calculate annual mortgage payment
        annual_mortgage_payment = Decimal('0')
        if prop.has_mortgage and prop.outstanding_mortgage_balance and prop.mortgage_interest_rate:
            monthly_interest_rate = prop.mortgage_interest_rate / Decimal('100') / Decimal('12')
            if prop.mortgage_type == 'interest_only':
                annual_mortgage_payment = prop.outstanding_mortgage_balance * monthly_interest_rate * 12
            elif prop.mortgage_type == 'principal_and_interest' and prop.mortgage_years_remaining:
                num_payments = prop.mortgage_years_remaining * 12
                if monthly_interest_rate > 0:
                    monthly_payment = prop.outstanding_mortgage_balance * (
                        monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments
                    ) / ((1 + monthly_interest_rate) ** num_payments - 1)
                    annual_mortgage_payment = monthly_payment * 12
                else:
                    annual_mortgage_payment = prop.outstanding_mortgage_balance / num_payments * 12
        
        # Calculate net cash flow before tax
        net_cash_flow_before_tax = net_operating_income - annual_mortgage_payment
        
        # Simple tax calculation (20% for dashboard purposes)
        estimated_tax = max(0, net_operating_income * Decimal('0.20'))
        net_cash_flow_after_tax = net_cash_flow_before_tax - estimated_tax
        
        # Calculate NRAT if we have the required data
        if prop.deposit_paid and prop.purchase_price and prop.date_of_purchase:
            try:
                nrat_result = calculate_nrat(prop, net_cash_flow_after_tax)
                if nrat_result and 'nrat' in nrat_result:
                    total_nrat += nrat_result['nrat']
                    properties_with_nrat += 1
            except Exception as e:
                print(f"Error calculating NRAT for {prop.property_name}: {e}")
        
        # Calculate ROE if we have equity
        if prop.estimated_market_value:
            property_equity = prop.estimated_market_value
            if prop.has_mortgage and prop.outstanding_mortgage_balance:
                property_equity -= prop.outstanding_mortgage_balance
            
            if property_equity > 0:
                roe = (net_cash_flow_after_tax / property_equity) * 100
                total_roe += roe
                properties_with_roe += 1
    
    # Calculate averages
    average_nrat = total_nrat / properties_with_nrat if properties_with_nrat > 0 else Decimal('0')
    average_roe = total_roe / properties_with_roe if properties_with_roe > 0 else Decimal('0')
    
    # Calculate total net monthly income across all properties
    total_net_monthly_income = Decimal('0')
    vacancy_rate = Decimal('0.0385')  # 3.85%
    maintenance_rate = Decimal('0.035')  # 3.5%
    
    for prop in properties:
        # Calculate annual rent and gross income for this property
        annual_rent = prop.weekly_rent * 52
        annual_vacancy_loss = annual_rent * vacancy_rate
        annual_gross_rent = annual_rent - annual_vacancy_loss
        monthly_gross_income = annual_gross_rent / 12
        
        # Calculate monthly expenses for this property
        monthly_property_management_fees = (annual_gross_rent * prop.property_management_fees / 100) / 12
        monthly_service_charge = prop.service_charge / 12
        monthly_ground_rent = prop.ground_rent / 12
        monthly_other_annual_costs = prop.other_annual_costs / 12
        monthly_maintenance = (annual_gross_rent * maintenance_rate) / 12
        total_monthly_expenses = (monthly_property_management_fees + monthly_service_charge + 
                                  monthly_ground_rent + monthly_other_annual_costs + 
                                  monthly_maintenance)
        
        # Calculate monthly mortgage payment (full payment including principal + interest)
        monthly_mortgage_payment = Decimal('0')
        if prop.has_mortgage and prop.outstanding_mortgage_balance and prop.mortgage_interest_rate and prop.mortgage_years_remaining:
            # Calculate full monthly mortgage payment using same logic as property detail
            monthly_interest_rate = prop.mortgage_interest_rate / Decimal('100') / Decimal('12')
            num_payments = prop.mortgage_years_remaining * 12
            
            if prop.mortgage_type == 'interest_only':
                monthly_mortgage_payment = prop.outstanding_mortgage_balance * monthly_interest_rate
            else:  # principal_and_interest
                if monthly_interest_rate > 0:
                    monthly_mortgage_payment = prop.outstanding_mortgage_balance * (
                        monthly_interest_rate * (1 + monthly_interest_rate) ** num_payments
                    ) / ((1 + monthly_interest_rate) ** num_payments - 1)
                else:
                    monthly_mortgage_payment = prop.outstanding_mortgage_balance / num_payments

        # Calculate net monthly income for this property (full cash flow after all expenses)
        property_net_monthly_income = monthly_gross_income - total_monthly_expenses - monthly_mortgage_payment
        total_net_monthly_income += property_net_monthly_income    # Calculate total net income after tax (Year 1) across all properties using detailed cashflow calculation
    total_net_income_after_tax_year1 = Decimal('0')
    rental_growth_rate = Decimal('0.0371')  # 3.71%
    
    for prop in properties:
        # Year 1 cashflow calculation (detailed calculation matching property detail view)
        
        # Calculate Year 1 projected rent (same as property detail view logic)
        annual_rent = prop.weekly_rent * 52
        projected_gross_rent = annual_rent * (Decimal('1') - vacancy_rate)
        
        # Calculate Year 1 expenses with inflation (same rates as property detail view)
        projected_property_management_fees = projected_gross_rent * (prop.property_management_fees / 100)
        projected_service_charge = prop.service_charge
        projected_ground_rent = prop.ground_rent
        projected_other_annual_costs = prop.other_annual_costs
        projected_maintenance = projected_gross_rent * maintenance_rate
        projected_total_expenses = (projected_property_management_fees + projected_service_charge +
                                   projected_ground_rent + projected_other_annual_costs + projected_maintenance)
        
        # Calculate net operating income
        net_operating_income = projected_gross_rent - projected_total_expenses
        
        # Calculate mortgage payments for Year 1
        annual_interest_payment = Decimal('0')
        annual_principal_payment = Decimal('0')
        
        if prop.has_mortgage and prop.outstanding_mortgage_balance and prop.mortgage_interest_rate:
            mortgage_balance = prop.outstanding_mortgage_balance
            monthly_interest_rate = prop.mortgage_interest_rate / Decimal('100') / Decimal('12')
            annual_interest_payment = mortgage_balance * monthly_interest_rate * 12
            
            if prop.mortgage_type == 'principal_and_interest' and prop.mortgage_years_remaining:
                # Calculate principal payment for P&I mortgages
                remaining_months = prop.mortgage_years_remaining * 12
                if monthly_interest_rate > 0:
                    monthly_payment = mortgage_balance * (
                        monthly_interest_rate * (1 + monthly_interest_rate) ** remaining_months
                    ) / ((1 + monthly_interest_rate) ** remaining_months - 1)
                    annual_total_payment = monthly_payment * 12
                    annual_principal_payment = annual_total_payment - annual_interest_payment
                else:
                    annual_principal_payment = mortgage_balance / remaining_months * 12
        
        # Calculate net cash flow before tax
        net_cash_flow_before_tax = net_operating_income - annual_interest_payment - annual_principal_payment
        
        # Detailed tax calculation (matching property detail view logic)
        net_income_for_tax = net_operating_income - annual_interest_payment
        
        # Tax calculation based on ownership status
        if prop.ownership_status == 'company':
            # Corporate tax rates
            if net_income_for_tax > 250000:
                corporate_tax = net_income_for_tax * Decimal('0.25')  # 25% main rate
            else:
                corporate_tax = net_income_for_tax * Decimal('0.19')  # 19% small profits rate
            applicable_tax = max(corporate_tax, Decimal('0'))
        else:
            # Individual tax calculation with proper bands
            if net_income_for_tax <= Decimal('12570'):
                # Below personal allowance
                applicable_tax = Decimal('0')
            elif net_income_for_tax <= Decimal('50270'):
                # Basic rate (20%) above personal allowance
                taxable_income = net_income_for_tax - Decimal('12570')
                applicable_tax = taxable_income * Decimal('0.20')
            else:
                # Higher rate (40%) for income above £50,270
                basic_rate_portion = Decimal('50270') - Decimal('12570')  # £37,700
                higher_rate_portion = net_income_for_tax - Decimal('50270')
                applicable_tax = (basic_rate_portion * Decimal('0.20')) + (higher_rate_portion * Decimal('0.40'))
        
        # Calculate net cash flow after tax for this property (Year 1 from cashflow forecast)
        property_net_cash_flow_after_tax = net_cash_flow_before_tax - applicable_tax
        total_net_income_after_tax_year1 += property_net_cash_flow_after_tax
    
    # Calculate average yield
    average_yield = 0
    if total_properties > 0 and total_portfolio_value > 0:
        average_yield = (total_annual_rent / total_portfolio_value) * 100

    # Get recent news articles for the dashboard
    try:
        recent_articles = NewsArticle.objects.all()[:4]
    except:
        recent_articles = []

    # Dashboard context data
    context = {
        'user': user,
        'profile': profile,
        'properties': properties[:5],  # Show only 5 most recent
        'recent_articles': recent_articles,  # Add recent articles
        'total_properties': total_properties,
        'total_weekly_rent': total_weekly_rent,
        'total_net_monthly_income': total_net_monthly_income,
        'total_annual_rent': total_annual_rent,
        'total_net_income_after_tax_year1': total_net_income_after_tax_year1,
        'total_portfolio_value': total_portfolio_value,
        # Add missing template variables
        'total_value': total_portfolio_value,
        'monthly_rent': total_net_monthly_income,
        'average_yield': average_yield,
        # Add the missing equity and advanced metrics
        'total_equity': total_equity,
        'net_annual_return': total_net_income_after_tax_year1,  # Now uses Year 1 cashflow forecast totals
        'average_nrat': average_nrat,
        'average_roe': average_roe,
        'page_title': 'Dashboard',
    }
    
    # Customer Journey: Users with properties ALWAYS see dashboard.html, new users see welcome
    if total_properties > 0:
        # Users with properties - ALWAYS show portfolio management dashboard
        return render(request, 'user_home/dashboard.html', context)
    else:
        # New users with no properties - show welcome experience
        return render(request, 'user_home/dashboard_welcome.html', context)

@login_required
@login_required
def upload_property(request):
    """View for uploading a new property"""
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
            messages.success(request, f'Property "{property_obj.property_name}" has been added successfully!')
            
            # FIXED CUSTOMER JOURNEY: Always redirect to property detail page after upload
            # This allows users to review their property details before returning to dashboard
            return redirect('user_home:property_detail', slug=property_obj.slug)
        else:
            # Display form errors to the user
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyForm()
    
    context = {
        'form': form,
        'title': 'Add New Property',
    }
    return render(request, 'user_home/property_form.html', context)

@login_required
def analyse_deal(request):
    """View for analysing a potential investment deal"""
    if request.method == 'POST':
        # Get form data
        deal_data = {
            'deal_name': request.POST.get('deal_name'),
            'property_type': request.POST.get('property_type'),
            'number_bedrooms': int(request.POST.get('number_bedrooms') or 0),
            'number_bathrooms': int(request.POST.get('number_bathrooms') or 0),
            'car_parking_spaces': int(request.POST.get('car_parking_spaces') or 0),
            'epc_rating': request.POST.get('epc_rating'),
            'purchase_price': Decimal(request.POST.get('purchase_price') or 0),
            'deposit_paid': Decimal(request.POST.get('deposit_paid') or 0),
            'current_market_value': Decimal(request.POST.get('current_market_value') or 0),
            'weekly_rent': Decimal(request.POST.get('weekly_rent') or 0),
            'ownership_status': request.POST.get('ownership_status'),
            'has_mortgage': request.POST.get('has_mortgage') == 'on',
            'mortgage_type': request.POST.get('mortgage_type'),
            'outstanding_mortgage_balance': Decimal(request.POST.get('outstanding_mortgage_balance') or 0) or (Decimal(request.POST.get('purchase_price') or 0) - Decimal(request.POST.get('deposit_paid') or 0)),
            'mortgage_interest_rate': Decimal(request.POST.get('mortgage_interest_rate') or 0),
            'mortgage_years_remaining': int(request.POST.get('mortgage_years_remaining') or 0),
            'conveyancing_fees': Decimal(request.POST.get('conveyancing_fees') or 0),
            'mortgage_arrangement_fees': Decimal(request.POST.get('mortgage_arrangement_fees') or 0),
            'survey_costs': Decimal(request.POST.get('survey_costs') or 0),
            'management_fees': Decimal(request.POST.get('management_fees') or 0),
            'service_charge': Decimal(request.POST.get('service_charge') or 0),
            'ground_rent': Decimal(request.POST.get('ground_rent') or 0),
            'selective_license_fee': Decimal(request.POST.get('selective_license_fee') or 0),
            'accounting_costs': Decimal(request.POST.get('accounting_costs') or 0),
            'gas_electrical_testing': Decimal(request.POST.get('gas_electrical_testing') or 0),
            'landlord_insurance': Decimal(request.POST.get('landlord_insurance') or 0),
            'other_costs': Decimal(request.POST.get('other_costs') or 0),
            'annual_income': Decimal(request.POST.get('annual_income') or 0),
            'is_uk_resident': request.POST.get('is_uk_resident') == 'on',
            'has_personal_allowance': request.POST.get('has_personal_allowance') == 'on',
        }
        
        # STANDARD METRICS
        vacancy_rate = Decimal('0.0385')  # 3.85%
        maintenance_rate = Decimal('0.035')  # 3.5%
        
        # Calculate rental income
        annual_rent = deal_data['weekly_rent'] * 52
        annual_vacancy_loss = annual_rent * vacancy_rate
        annual_gross_rent = annual_rent - annual_vacancy_loss
        monthly_gross_income = annual_gross_rent / 12
        
        # Calculate expenses
        monthly_management = (annual_gross_rent * deal_data['management_fees'] / 100) / 12
        monthly_service_charge = deal_data['service_charge'] / 12
        monthly_ground_rent = deal_data['ground_rent'] / 12
        monthly_selective_license = deal_data['selective_license_fee'] / 12
        monthly_accounting = deal_data['accounting_costs'] / 12
        monthly_gas_electrical = deal_data['gas_electrical_testing'] / 12
        monthly_insurance = deal_data['landlord_insurance'] / 12
        monthly_other = deal_data['other_costs'] / 12
        monthly_maintenance = (annual_gross_rent * maintenance_rate) / 12
        
        total_monthly_expenses = (monthly_management + monthly_service_charge + 
                                 monthly_ground_rent + monthly_selective_license +
                                 monthly_accounting + monthly_gas_electrical +
                                 monthly_insurance + monthly_other + monthly_maintenance)
        
        # Calculate mortgage payments
        monthly_mortgage_payment = Decimal('0')
        if deal_data['has_mortgage'] and deal_data['outstanding_mortgage_balance']:
            monthly_rate = deal_data['mortgage_interest_rate'] / 100 / 12
            num_payments = deal_data['mortgage_years_remaining'] * 12
            
            if deal_data['mortgage_type'] == 'repayment' and monthly_rate > 0:
                monthly_mortgage_payment = (
                    deal_data['outstanding_mortgage_balance'] * 
                    (monthly_rate * (1 + monthly_rate) ** num_payments) / 
                    ((1 + monthly_rate) ** num_payments - 1)
                )
            elif deal_data['mortgage_type'] == 'interest_only':
                monthly_mortgage_payment = deal_data['outstanding_mortgage_balance'] * monthly_rate
        
        # Calculate net income
        monthly_net_income = monthly_gross_income - total_monthly_expenses - monthly_mortgage_payment
        annual_net_income = monthly_net_income * 12
        
        # Calculate total cash invested
        acquisition_costs = (deal_data['conveyancing_fees'] + 
                           deal_data['mortgage_arrangement_fees'] + 
                           deal_data['survey_costs'])
        total_cash_invested = deal_data['deposit_paid'] + acquisition_costs
        
        # Calculate ROI
        roi = (annual_net_income / total_cash_invested * 100) if total_cash_invested > 0 else 0
        
        # ============================================
        # ADVANCED METRICS (matching property_detail)
        # ============================================
        
        # Constants for analysis
        rental_growth_rate = Decimal('0.0371')  # 3.71% annual rental growth
        inflation_rate = Decimal('0.028')  # 2.8% annual inflation
        
        # Calculate Gross Annual Yield
        current_market_value = deal_data['current_market_value']
        if current_market_value > 0:
            gross_annual_yield = (annual_gross_rent / current_market_value) * 100
        else:
            gross_annual_yield = Decimal('0')
        
        # Calculate Net Annual Yield
        monthly_operating_income = monthly_gross_income - total_monthly_expenses
        if current_market_value > 0:
            net_annual_yield = ((monthly_operating_income * 12) / current_market_value) * 100
        else:
            net_annual_yield = Decimal('0')
        
        # Calculate DSCR (Debt Service Coverage Ratio)
        annual_operating_income = monthly_operating_income * 12
        total_annual_mortgage_payments = monthly_mortgage_payment * 12
        
        if deal_data['has_mortgage'] and total_annual_mortgage_payments > 0:
            dscr = annual_operating_income / total_annual_mortgage_payments
        else:
            dscr = Decimal('0')  # No mortgage = N/A
        
        # Calculate Opex Load (Operating Expense Load)
        if annual_gross_rent > 0:
            opex_load = ((total_monthly_expenses * 12) / annual_gross_rent) * 100
        else:
            opex_load = Decimal('0')
        
        # ============================================
        # 10-YEAR CASHFLOW PROJECTION
        # ============================================
        
        cashflow_projection = []
        tax_loss_carryforward = Decimal('0')
        
        # Calculate fixed monthly payment for Principal & Interest mortgages
        if deal_data['has_mortgage'] and deal_data['mortgage_type'] == 'repayment':
            monthly_rate = deal_data['mortgage_interest_rate'] / 100 / 12
            num_payments = deal_data['mortgage_years_remaining'] * 12
            if monthly_rate > 0:
                fixed_monthly_payment = (deal_data['outstanding_mortgage_balance'] * monthly_rate * ((1 + monthly_rate) ** num_payments)) / \
                                      (((1 + monthly_rate) ** num_payments) - 1)
            else:
                fixed_monthly_payment = deal_data['outstanding_mortgage_balance'] / num_payments if num_payments > 0 else Decimal('0')
        else:
            fixed_monthly_payment = Decimal('0')
        
        remaining_balance = deal_data['outstanding_mortgage_balance'] if deal_data['has_mortgage'] else Decimal('0')
        
        for year in range(1, 11):  # Years 1-10
            # Project rental income with growth
            projected_annual_rent = annual_rent * ((1 + rental_growth_rate) ** (year - 1))
            projected_vacancy_loss = projected_annual_rent * vacancy_rate
            projected_gross_rent = projected_annual_rent - projected_vacancy_loss
            
            # Project expenses with inflation
            projected_management = (projected_gross_rent * deal_data['management_fees'] / 100)
            projected_service_charge = (deal_data['service_charge']) * ((1 + inflation_rate) ** (year - 1))
            projected_ground_rent = (deal_data['ground_rent']) * ((1 + inflation_rate) ** (year - 1))
            projected_selective_license = (deal_data['selective_license_fee']) * ((1 + inflation_rate) ** (year - 1))
            projected_accounting = (deal_data['accounting_costs']) * ((1 + inflation_rate) ** (year - 1))
            projected_gas_electrical = (deal_data['gas_electrical_testing']) * ((1 + inflation_rate) ** (year - 1))
            projected_insurance = (deal_data['landlord_insurance']) * ((1 + inflation_rate) ** (year - 1))
            projected_other = (deal_data['other_costs']) * ((1 + inflation_rate) ** (year - 1))
            projected_maintenance = (projected_gross_rent * maintenance_rate)
            
            projected_total_expenses = (projected_management + projected_service_charge + 
                                       projected_ground_rent + projected_selective_license +
                                       projected_accounting + projected_gas_electrical +
                                       projected_insurance + projected_other + projected_maintenance)
            
            # Calculate mortgage payments
            if deal_data['has_mortgage']:
                if deal_data['mortgage_type'] == 'repayment':
                    # Calculate interest on current balance
                    annual_interest = remaining_balance * (deal_data['mortgage_interest_rate'] / 100)
                    annual_interest_payment = annual_interest
                    
                    # Total annual payment
                    annual_total_mortgage_payment = fixed_monthly_payment * 12
                    
                    # Principal payment is total - interest
                    annual_principal_payment = annual_total_mortgage_payment - annual_interest_payment
                    
                    # Update remaining balance
                    remaining_balance = max(Decimal('0'), remaining_balance - annual_principal_payment)
                else:  # interest_only
                    annual_interest_payment = deal_data['outstanding_mortgage_balance'] * (deal_data['mortgage_interest_rate'] / 100)
                    annual_principal_payment = Decimal('0')
                    annual_total_mortgage_payment = annual_interest_payment
            else:
                annual_interest_payment = Decimal('0')
                annual_principal_payment = Decimal('0')
                annual_total_mortgage_payment = Decimal('0')
            
            # Net Operating Income
            net_operating_income = projected_gross_rent - projected_total_expenses
            net_cash_flow_before_tax = net_operating_income - annual_total_mortgage_payment
            
            # ============================================
            # TAX CALCULATIONS
            # ============================================
            
            # Taxable profit for company (interest is deductible, principal is not)
            company_taxable_profit = net_operating_income - annual_interest_payment
            corporate_tax = corp_tax_calculator.calculate_corporation_tax(company_taxable_profit)
            
            # Tax payable if owned individually (onshore)
            # Apply inflation growth to personal income
            if year == 1:
                personal_income = deal_data['annual_income']
            else:
                personal_income = deal_data['annual_income'] * ((1 + inflation_rate) ** (year - 1))
            
            rental_profit = net_operating_income  # Gross rental income - total operating expenses
            
            # Tax without property
            tax_result_without = tax_calculator.calculate_income_tax(personal_income)
            notional_income_tax_without_property = tax_result_without['tax_payable']
            
            # Tax with property (personal income + rental profit)
            total_income_with_property = personal_income + rental_profit
            tax_result_with = tax_calculator.calculate_income_tax(total_income_with_property)
            tax_with_property_before_relief = tax_result_with['tax_payable']
            
            # Apply 20% mortgage interest relief
            interest_rate_relief = annual_interest_payment * Decimal('0.20')
            tax_with_property_after_relief = max(0, tax_with_property_before_relief - interest_rate_relief)
            
            # Final tax payable = tax with property - tax without property
            tax_payable_on_shore_individual = tax_with_property_after_relief - notional_income_tax_without_property
            
            # Debug output for Year 1
            if year == 1:
                print(f"\n=== TAX CALCULATION DEBUG Year {year} ===")
                print(f"Deal: {deal_data['deal_name']}")
                print(f"Ownership status: {deal_data['ownership_status']}")
                print(f"Personal income: £{personal_income:,.2f}")
                print(f"Net operating income (rental profit): £{net_operating_income:,.2f}")
                print(f"Annual interest payment: £{annual_interest_payment:,.2f}")
                print(f"\nTax calculation:")
                print(f"  Tax without property: £{notional_income_tax_without_property:,.2f}")
                print(f"  Total income with property: £{total_income_with_property:,.2f}")
                print(f"  Tax with property before relief: £{tax_with_property_before_relief:,.2f}")
                print(f"  Interest rate relief (20%): £{interest_rate_relief:,.2f}")
                print(f"  Tax with property after relief: £{tax_with_property_after_relief:,.2f}")
                print(f"  Tax payable onshore individual: £{tax_payable_on_shore_individual:,.2f}")
                print(f"=== END TAX DEBUG ===\n")
            
            # Tax payable if owned by foreign individual (offshore)
            if year == 1:
                personal_income_offshore = deal_data['annual_income']
            else:
                personal_income_offshore = deal_data['annual_income'] * ((1 + inflation_rate) ** (year - 1))
            
            rental_profit_offshore = net_operating_income
            
            # Tax without property (offshore rates)
            notional_income_tax_without_property_offshore = offshore_tax_calculator.calculate_offshore_tax(personal_income_offshore)['tax_payable']
            
            # Tax with property (personal income + rental profit)
            total_income_with_property_offshore = personal_income_offshore + rental_profit_offshore
            tax_with_property_before_relief_offshore = offshore_tax_calculator.calculate_offshore_tax(total_income_with_property_offshore)['tax_payable']
            
            # Apply 20% mortgage interest relief
            interest_rate_relief_offshore = annual_interest_payment * Decimal('0.20')
            tax_with_property_after_relief_offshore = max(0, tax_with_property_before_relief_offshore - interest_rate_relief_offshore)
            
            # Final tax payable = tax with property - tax without property
            tax_payable_offshore_individual = tax_with_property_after_relief_offshore - notional_income_tax_without_property_offshore
            
            # Determine applicable tax before carryforward adjustments
            if deal_data['ownership_status'] == 'company':
                gross_applicable_tax = corporate_tax
            elif deal_data['ownership_status'] == 'individual':
                gross_applicable_tax = tax_payable_on_shore_individual
            elif deal_data['ownership_status'] == 'individual_offshore':
                gross_applicable_tax = tax_payable_offshore_individual
            else:
                gross_applicable_tax = Decimal('0')
            
            # Debug output for Year 1
            if year == 1:
                print(f"\n=== APPLICABLE TAX DETERMINATION Year {year} ===")
                print(f"Ownership status: {deal_data['ownership_status']}")
                print(f"Corporate tax: £{corporate_tax:,.2f}")
                print(f"Tax payable onshore individual: £{tax_payable_on_shore_individual:,.2f}")
                print(f"Tax payable offshore individual: £{tax_payable_offshore_individual:,.2f}")
                print(f"Gross applicable tax (selected): £{gross_applicable_tax:,.2f}")
                print(f"=== END APPLICABLE TAX DEBUG ===\n")
            
            # Apply tax corkscrew logic (loss carryforward)
            if gross_applicable_tax < 0:
                # Tax loss - add to carryforward balance and set current tax to 0
                tax_loss_carryforward += abs(gross_applicable_tax)
                applicable_tax = Decimal('0')
                tax_loss_utilized = Decimal('0')
            elif gross_applicable_tax > 0 and tax_loss_carryforward > 0:
                # Positive tax - use carryforward to offset
                if tax_loss_carryforward >= gross_applicable_tax:
                    # Sufficient carryforward to cover all tax
                    tax_loss_utilized = gross_applicable_tax
                    applicable_tax = Decimal('0')
                    tax_loss_carryforward -= gross_applicable_tax
                else:
                    # Partial offset - use all remaining carryforward
                    tax_loss_utilized = tax_loss_carryforward
                    applicable_tax = gross_applicable_tax - tax_loss_carryforward
                    tax_loss_carryforward = Decimal('0')
            else:
                # Positive tax with no carryforward
                applicable_tax = gross_applicable_tax
                tax_loss_utilized = Decimal('0')
            
            # Calculate net cash flow after tax
            net_cash_flow_after_tax = net_cash_flow_before_tax - applicable_tax
            
            # Net income for tax purposes (excluding principal payments)
            net_income_for_tax = net_operating_income - annual_interest_payment
            
            cashflow_projection.append({
                'year': year,
                'gross_rent': projected_gross_rent,
                'total_expenses': projected_total_expenses,
                'net_operating_income': net_operating_income,
                'annual_interest_payment': annual_interest_payment,
                'annual_principal_payment': annual_principal_payment,
                'annual_total_mortgage_payment': annual_total_mortgage_payment,
                'net_cash_flow': net_cash_flow_before_tax,
                'net_income_for_tax': net_income_for_tax,
                'remaining_mortgage_balance': remaining_balance,
                'corporate_tax': corporate_tax,
                'tax_payable_on_shore_individual': tax_payable_on_shore_individual,
                'tax_payable_offshore_individual': tax_payable_offshore_individual,
                'gross_applicable_tax': gross_applicable_tax,
                'tax_loss_carryforward_beginning': tax_loss_carryforward + tax_loss_utilized - (abs(gross_applicable_tax) if gross_applicable_tax < 0 else 0),
                'tax_loss_generated': abs(gross_applicable_tax) if gross_applicable_tax < 0 else Decimal('0'),
                'tax_loss_utilized': tax_loss_utilized,
                'tax_loss_carryforward_ending': tax_loss_carryforward,
                'applicable_tax': applicable_tax,
                'net_cash_flow_after_tax': net_cash_flow_after_tax,
            })
        
        # ============================================
        # NRAT CALCULATION
        # ============================================
        
        # Get Year 1 Net Cash Flow After Tax
        if len(cashflow_projection) > 0:
            year_1_net_return_after_tax = cashflow_projection[0]['net_cash_flow_after_tax']
            
            # Determine buyer type for SDLT calculation
            if deal_data['ownership_status'] == 'uk_limited_company':
                buyer_type = 'uk_company'
            elif deal_data['ownership_status'] in ['individual_onshore', 'individual_onshore_notaxfree']:
                buyer_type = 'uk_individual'
            elif deal_data['ownership_status'] == 'individual_offshore':
                buyer_type = 'non_uk_individual'
            else:
                buyer_type = 'uk_individual'
            
            # Calculate SDLT (always BTL)
            purchase_date = date.today()  # Use current date for deal analysis
            
            sdlt_result = sdlt_calculator.calculate_sdlt(
                purchase_date=purchase_date,
                purchase_price=int(deal_data['purchase_price']),
                buyer_type=buyer_type,
                is_btl=True
            )
            
            sdlt_amount = Decimal(str(sdlt_result.get('sdlt', 0)))
            
            # Total cash deployed = deposit + SDLT + acquisition costs
            total_cash_deployed = deal_data['deposit_paid'] + sdlt_amount + acquisition_costs
            
            # Calculate NRAT
            if total_cash_deployed > 0:
                nrat = (year_1_net_return_after_tax / total_cash_deployed) * 100
            else:
                nrat = Decimal('0')
        else:
            year_1_net_return_after_tax = Decimal('0')
            sdlt_amount = Decimal('0')
            total_cash_deployed = deal_data['deposit_paid'] + acquisition_costs
            nrat = Decimal('0')
        
        # Calculate 10-year total
        total_net_income_after_tax = sum(projection['net_cash_flow_after_tax'] for projection in cashflow_projection)
        
        # ============================================
        # CAPITAL GROWTH CALCULATIONS
        # ============================================
        
        # Setup for capital growth calculations
        current_value = deal_data['current_market_value']
        agency_fees_rate = Decimal('0.015')  # 1.5%
        legal_fees_rate = Decimal('1500')
        
        # EPC upgrade costs (if needed)
        epc_rating = deal_data.get('epc_rating', 'C')
        if epc_rating and epc_rating not in ['A', 'B', 'C']:
            epc_upgrade_cost = Decimal('5000')
        else:
            epc_upgrade_cost = Decimal('0')
        
        # Calculate total principal paid over 10 years (for notional equity)
        if deal_data['has_mortgage']:
            total_principal_paid = sum(projection['annual_principal_payment'] for projection in cashflow_projection)
        else:
            total_principal_paid = Decimal('0')
        
        # Calculate notional equity
        notional_equity = current_value - deal_data['outstanding_mortgage_balance'] + total_principal_paid
        
        # --- SCENARIO 1: 0% Growth ---
        future_value_no_growth = current_value
        agency_fees_no_growth = future_value_no_growth * agency_fees_rate
        total_selling_costs_no_growth = agency_fees_no_growth + legal_fees_rate + epc_upgrade_cost
        net_capital_growth_no_growth = -total_selling_costs_no_growth
        
        # Calculate CGT for 0% growth
        if net_capital_growth_no_growth <= 0:
            cgt_payable_no_growth = Decimal('0')
            net_capital_growth_after_cgt_no_growth = net_capital_growth_no_growth
        else:
            if deal_data['ownership_status'] == 'company':
                cgt_payable_no_growth = corp_tax_calculator.calculate_corporation_tax(net_capital_growth_no_growth)
            else:
                year_10_cashflow = cashflow_projection[9]['net_cash_flow_after_tax'] if len(cashflow_projection) >= 10 else Decimal('0')
                total_gains_and_income = net_capital_growth_no_growth + year_10_cashflow
                cgt_rate = Decimal('0.24') if total_gains_and_income > 50270 else Decimal('0.18')
                cgt_payable_no_growth = net_capital_growth_no_growth * cgt_rate
            net_capital_growth_after_cgt_no_growth = net_capital_growth_no_growth - cgt_payable_no_growth
        
        no_growth_value = net_capital_growth_after_cgt_no_growth
        no_growth_capital_growth_display = no_growth_value
        
        # Calculate return rates for 0% growth
        if notional_equity and notional_equity != 0:
            no_growth_annual_capital_return_rate = float((float(no_growth_value) / float(notional_equity)) / 10 * 100)
            no_growth_total_return = float(total_net_income_after_tax + no_growth_value)
            no_growth_annual_return_rate = float((no_growth_total_return / float(notional_equity)) / 10 * 100)
        else:
            no_growth_annual_capital_return_rate = 0
            no_growth_annual_return_rate = 0
        
        # --- SCENARIO 2: 1.7% Growth ---
        future_value_moderate_growth = current_value * ((Decimal('1.017')) ** 10)
        agency_fees_moderate_growth = future_value_moderate_growth * agency_fees_rate
        total_selling_costs_moderate_growth = agency_fees_moderate_growth + legal_fees_rate + epc_upgrade_cost
        net_capital_growth_moderate = future_value_moderate_growth - current_value - total_selling_costs_moderate_growth
        
        # Calculate CGT for 1.7% growth
        if net_capital_growth_moderate <= 0:
            cgt_payable_moderate_growth = Decimal('0')
            net_capital_growth_after_cgt_moderate = net_capital_growth_moderate
        else:
            if deal_data['ownership_status'] == 'company':
                cgt_payable_moderate_growth = corp_tax_calculator.calculate_corporation_tax(net_capital_growth_moderate)
            else:
                year_10_cashflow = cashflow_projection[9]['net_cash_flow_after_tax'] if len(cashflow_projection) >= 10 else Decimal('0')
                total_gains_and_income = net_capital_growth_moderate + year_10_cashflow
                cgt_rate = Decimal('0.24') if total_gains_and_income > 50270 else Decimal('0.18')
                cgt_payable_moderate_growth = net_capital_growth_moderate * cgt_rate
            net_capital_growth_after_cgt_moderate = net_capital_growth_moderate - cgt_payable_moderate_growth
        
        moderate_growth_value = net_capital_growth_after_cgt_moderate
        moderate_growth_capital_growth_display = moderate_growth_value
        
        # Calculate return rates for 1.7% growth
        if notional_equity and notional_equity != 0:
            moderate_growth_annual_capital_return_rate = float((float(moderate_growth_value) / float(notional_equity)) / 10 * 100)
            moderate_growth_total_return = float(total_net_income_after_tax + moderate_growth_value)
            moderate_growth_annual_return_rate = float((moderate_growth_total_return / float(notional_equity)) / 10 * 100)
        else:
            moderate_growth_annual_capital_return_rate = 0
            moderate_growth_annual_return_rate = 0
        
        # --- SCENARIO 3: 3.4% Growth ---
        future_value_average_growth = current_value * ((Decimal('1.034')) ** 10)
        agency_fees_average_growth = future_value_average_growth * agency_fees_rate
        total_selling_costs_average_growth = agency_fees_average_growth + legal_fees_rate + epc_upgrade_cost
        net_capital_growth_average = future_value_average_growth - current_value - total_selling_costs_average_growth
        
        # Calculate CGT for 3.4% growth
        if net_capital_growth_average <= 0:
            cgt_payable_average_growth = Decimal('0')
            net_capital_growth_after_cgt_average = net_capital_growth_average
        else:
            if deal_data['ownership_status'] == 'company':
                cgt_payable_average_growth = corp_tax_calculator.calculate_corporation_tax(net_capital_growth_average)
            else:
                year_10_cashflow = cashflow_projection[9]['net_cash_flow_after_tax'] if len(cashflow_projection) >= 10 else Decimal('0')
                total_gains_and_income = net_capital_growth_average + year_10_cashflow
                cgt_rate = Decimal('0.24') if total_gains_and_income > 50270 else Decimal('0.18')
                cgt_payable_average_growth = net_capital_growth_average * cgt_rate
            net_capital_growth_after_cgt_average = net_capital_growth_average - cgt_payable_average_growth
        
        average_growth_value = net_capital_growth_after_cgt_average
        average_growth_capital_growth_display = average_growth_value
        
        # Calculate return rates for 3.4% growth
        if notional_equity and notional_equity != 0:
            average_growth_annual_capital_return_rate = float((float(average_growth_value) / float(notional_equity)) / 10 * 100)
            average_growth_total_return = float(total_net_income_after_tax + average_growth_value)
            average_growth_annual_return_rate = float((average_growth_total_return / float(notional_equity)) / 10 * 100)
        else:
            average_growth_annual_capital_return_rate = 0
            average_growth_annual_return_rate = 0
        
        # Get additional capital growth data for PDF
        no_growth_future_value = current_value
        moderate_growth_future_value = current_value * ((1 + Decimal('0.017')) ** 10)
        average_growth_future_value = current_value * ((1 + Decimal('0.034')) ** 10)
        
        # Calculate net gains (value after selling costs)
        agency_fees_rate = Decimal('0.015')
        no_growth_net_gain = no_growth_value
        moderate_growth_net_gain = moderate_growth_value  
        average_growth_net_gain = average_growth_value
        
        # Risk analysis values
        tenant_dispute_total = (monthly_mortgage_payment * 18) + 1500
        tenant_dispute_monthly = tenant_dispute_total / 18
        rrb_rent_recovery = deal_data['weekly_rent'] * 104
        
        context = {
            'deal_data': deal_data,
            'monthly_gross_income': monthly_gross_income,
            'total_monthly_expenses': total_monthly_expenses,
            'monthly_mortgage_payment': monthly_mortgage_payment,
            'monthly_net_income': monthly_net_income,
            'annual_net_income': annual_net_income,
            'total_cash_invested': total_cash_invested,
            'roi': roi,
            'vacancy_rate': vacancy_rate * 100,
            'maintenance_rate': maintenance_rate * 100,
            # Advanced metrics
            'gross_annual_yield': gross_annual_yield,
            'net_annual_yield': net_annual_yield,
            'dscr': dscr,
            'opex_load': opex_load,
            'cashflow_projection': cashflow_projection,
            'total_net_income_after_tax': total_net_income_after_tax,
            'nrat': nrat,
            'sdlt_amount': sdlt_amount,
            'total_cash_deployed': total_cash_deployed,
            'year_1_net_return_after_tax': year_1_net_return_after_tax,
            'acquisition_costs': acquisition_costs,
            # Capital growth variables
            'no_growth_value': no_growth_value,
            'moderate_growth_value': moderate_growth_value,
            'average_growth_value': average_growth_value,
            'no_growth_capital_growth_display': no_growth_capital_growth_display,
            'moderate_growth_capital_growth_display': moderate_growth_capital_growth_display,
            'average_growth_capital_growth_display': average_growth_capital_growth_display,
            'notional_equity': notional_equity,
            'no_growth_annual_capital_return_rate': no_growth_annual_capital_return_rate,
            'moderate_growth_annual_capital_return_rate': moderate_growth_annual_capital_return_rate,
            'average_growth_annual_capital_return_rate': average_growth_annual_capital_return_rate,
            'no_growth_annual_return_rate': no_growth_annual_return_rate,
            'moderate_growth_annual_return_rate': moderate_growth_annual_return_rate,
            'average_growth_annual_return_rate': average_growth_annual_return_rate,
            # PDF-specific data
            'no_growth_future_value': no_growth_future_value,
            'moderate_growth_future_value': moderate_growth_future_value,
            'average_growth_future_value': average_growth_future_value,
            'no_growth_net_gain': no_growth_net_gain,
            'moderate_growth_net_gain': moderate_growth_net_gain,
            'average_growth_net_gain': average_growth_net_gain,
            'no_growth_capital_return': no_growth_annual_capital_return_rate,
            'moderate_growth_capital_return': moderate_growth_annual_capital_return_rate,
            'average_growth_capital_return': average_growth_annual_capital_return_rate,
            'no_growth_total_return': no_growth_annual_return_rate,
            'moderate_growth_total_return': moderate_growth_annual_return_rate,
            'average_growth_total_return': average_growth_annual_return_rate,
            'ten_year_total': total_net_income_after_tax,
            'tenant_dispute_total': tenant_dispute_total,
            'tenant_dispute_monthly': tenant_dispute_monthly,
            'rrb_rent_recovery': rrb_rent_recovery,
        }
        
        # Store analysis data in session for PDF generation
        request.session['deal_analysis_context'] = {
            'deal_data': {k: float(v) if isinstance(v, Decimal) else v for k, v in deal_data.items()},
            'metrics': {
                'monthly_gross_income': float(monthly_gross_income),
                'total_monthly_expenses': float(total_monthly_expenses),
                'monthly_mortgage_payment': float(monthly_mortgage_payment),
                'monthly_net_income': float(monthly_net_income),
                'annual_net_income': float(annual_net_income),
                'total_cash_invested': float(total_cash_invested),
                'roi': float(roi),
                'gross_annual_yield': float(gross_annual_yield),
                'net_annual_yield': float(net_annual_yield),
                'dscr': float(dscr),
                'opex_load': float(opex_load),
                'nrat': float(nrat),
                'sdlt_amount': float(sdlt_amount),
                'total_cash_deployed': float(total_cash_deployed),
                'acquisition_costs': float(acquisition_costs),
                'notional_equity': float(notional_equity),
            },
            'cashflow_projection': [
                {k: float(v) if isinstance(v, Decimal) else v for k, v in proj.items()}
                for proj in cashflow_projection
            ],
            'capital_growth': {
                'no_growth_future_value': float(no_growth_future_value),
                'moderate_growth_future_value': float(moderate_growth_future_value),
                'average_growth_future_value': float(average_growth_future_value),
                'no_growth_net_gain': float(no_growth_net_gain),
                'moderate_growth_net_gain': float(moderate_growth_net_gain),
                'average_growth_net_gain': float(average_growth_net_gain),
                'no_growth_capital_return': float(no_growth_annual_capital_return_rate),
                'moderate_growth_capital_return': float(moderate_growth_annual_capital_return_rate),
                'average_growth_capital_return': float(average_growth_annual_capital_return_rate),
                'no_growth_total_return': float(no_growth_annual_return_rate),
                'moderate_growth_total_return': float(moderate_growth_annual_return_rate),
                'average_growth_total_return': float(average_growth_annual_return_rate),
            },
            'risk_analysis': {
                'tenant_dispute_total': float(tenant_dispute_total),
                'tenant_dispute_monthly': float(tenant_dispute_monthly),
                'rrb_rent_recovery': float(rrb_rent_recovery),
            },
            'ten_year_total': float(total_net_income_after_tax),
        }
        
        return render(request, 'user_home/deal_analysis_result.html', context)
    
    context = {
        'title': 'Analyse a Potential Investment',
        'today': date.today().strftime('%Y-%m-%d'),
    }
    return render(request, 'user_home/analyse_deal.html', context)

@login_required
def property_detail(request, slug):
    """View for displaying property details"""
    property_obj = get_object_or_404(Property, slug=slug, owner=request.user)
    
    ####################################################
    #####
    ############
    ############
    
    # STANDARD METRICS
    vacancy_rate = Decimal('0.0385')  # 3.85%
    maintenance_rate = Decimal('0.035')  # 3.5%
    inflation_rate = Decimal('0.028')  # 2.8%
    rental_growth_rate = Decimal('0.0371')  # 3.71%

    # Estimated Market Value
    estimated_market_value = property_obj.estimated_market_value if property_obj.estimated_market_value else 0
    capital_appreciation = estimated_market_value - property_obj.purchase_price if property_obj.purchase_price else 0

    # Calculate basic net income for other properties 
    annual_rent = property_obj.weekly_rent * 52
    annual_vacancy_loss = annual_rent * vacancy_rate
    annual_gross_rent = annual_rent - annual_vacancy_loss
    monthly_gross_income = annual_gross_rent / 12

    monthly_property_management_fees = (annual_gross_rent * property_obj.property_management_fees / 100) / 12
    monthly_service_charge = property_obj.service_charge / 12
    monthly_ground_rent = property_obj.ground_rent / 12
    monthly_other_annual_costs = property_obj.other_annual_costs / 12   
    monthly_maintenance = (annual_gross_rent * maintenance_rate) / 12
    total_monthly_expenses = (monthly_property_management_fees + monthly_service_charge + 
                              monthly_ground_rent + monthly_other_annual_costs + 
                              monthly_maintenance)
    

    # Calculate monthly mortgage payment based on mortgage type
    monthly_mortgage_payment = Decimal('0')
    monthly_interest_payment = Decimal('0')
    monthly_principal_payment = Decimal('0')
    
    if property_obj.has_mortgage and property_obj.outstanding_mortgage_balance:
        # Scenario 1: Interest Only Mortgage
        if property_obj.mortgage_type == 'interest_only' and property_obj.mortgage_interest_rate:
            # Simple interest calculation: Principal × (Interest Rate / 12)
            monthly_interest_rate = property_obj.mortgage_interest_rate / Decimal('100') / Decimal('12')
            monthly_interest_payment = property_obj.outstanding_mortgage_balance * monthly_interest_rate
            monthly_principal_payment = Decimal('0')  # No principal payment for interest-only
            monthly_mortgage_payment = monthly_interest_payment
        
        # Scenario 2: Principal & Interest Mortgage (PMT calculation)
        elif property_obj.mortgage_type == 'principal_and_interest' and property_obj.mortgage_interest_rate and property_obj.mortgage_years_remaining:
            # PMT formula: P * [r(1+r)^n] / [(1+r)^n - 1]
            monthly_interest_rate = property_obj.mortgage_interest_rate / Decimal('100') / Decimal('12')
            number_of_payments = property_obj.mortgage_years_remaining * 12
            P = property_obj.outstanding_mortgage_balance
            r = float(monthly_interest_rate)  # Convert to float for power calculations
            n = number_of_payments
            
            if r > 0:
                monthly_mortgage_payment = Decimal(str(float(P) * (r * (1 + r) ** n) / ((1 + r) ** n - 1)))
                # For first month, calculate interest and principal breakdown
                monthly_interest_payment = property_obj.outstanding_mortgage_balance * monthly_interest_rate
                monthly_principal_payment = monthly_mortgage_payment - monthly_interest_payment
            else:
                # If interest rate is 0, divide principal by number of payments
                monthly_mortgage_payment = P / Decimal(str(n))
                monthly_interest_payment = Decimal('0')
                monthly_principal_payment = monthly_mortgage_payment
        else:
            # Fallback: if mortgage type or required fields are missing
            monthly_mortgage_payment = Decimal('0')
            monthly_interest_payment = Decimal('0')
            monthly_principal_payment = Decimal('0')
    else:
        # Scenario 3: No mortgage (has_mortgage = False)
        monthly_mortgage_payment = Decimal('0')
        monthly_interest_payment = Decimal('0')
        monthly_principal_payment = Decimal('0')

    # Calculate net monthly income (excluding principal payment for cash flow purposes)
    # Principal payment is equity building, not an expense
    net_monthly_income = monthly_gross_income - total_monthly_expenses - monthly_mortgage_payment
    
    # DEBUG: Print calculation values
    #print(f"=== DEBUG: Net Monthly Income Calculation for {property_obj.property_name} ===")
    #print(f"Monthly Gross Income: £{monthly_gross_income}")
    #print(f"Total Monthly Expenses: £{total_monthly_expenses}")
    #print(f"  - Property Management Fees: £{monthly_property_management_fees}")
    #print(f"  - Service Charge: £{monthly_service_charge}")
    #print(f"  - Ground Rent: £{monthly_ground_rent}")
    #print(f"  - Other Annual Costs: £{monthly_other_annual_costs}")
    #print(f"  - Maintenance: £{monthly_maintenance}")
    #print(f"Monthly Interest Payment: £{monthly_interest_payment}")
    #print(f"Monthly Mortgage Payment: £{monthly_mortgage_payment}")
    #print(f"Net Monthly Income: £{net_monthly_income}")
    #print(f"============================================")

    # Calculate net monthly cash flow (including all mortgage payments)
    net_monthly_cash_flow = monthly_gross_income - total_monthly_expenses - monthly_mortgage_payment   

    # Calculate Gross Annual Yield
    gross_annual_yield = (annual_gross_rent / property_obj.estimated_market_value * 100) if property_obj.purchase_price else 0

    # Calculate Net Annual Yield
    monthly_operating_income = monthly_gross_income - total_monthly_expenses
    net_annual_yield = ((monthly_operating_income * 12) / property_obj.estimated_market_value * 100) if property_obj.purchase_price else 0


    ## KPIS ##
    # Debt Service Coverage Ratio
    total_annual_mortgage_payments = monthly_mortgage_payment * 12

    #calulation of annual expenses
    annual_property_management_fees = annual_gross_rent * (property_obj.property_management_fees / 100)
    annual_service_charge = property_obj.service_charge 
    annual_ground_rent = property_obj.ground_rent
    annual_other_annual_costs = property_obj.other_annual_costs
    annual_maintenance = annual_gross_rent * maintenance_rate

    total_annual_expenses = (annual_property_management_fees + annual_service_charge +
                             annual_ground_rent + annual_other_annual_costs + annual_maintenance)

    annual_operating_income = annual_gross_rent - total_annual_expenses

    # DEBUG: Print annual calculations
    #print(f"=== DEBUG: Annual Calculations for {property_obj.property_name} ===")
    #print(f"Annual Gross Rent: £{annual_gross_rent}")
    #print(f"Annual Expenses Breakdown:")
    #print(f"  - Property Management Fees: £{annual_property_management_fees}")
    #print(f"  - Service Charge: £{annual_service_charge}")
    #print(f"  - Ground Rent: £{annual_ground_rent}")
    #print(f"  - Other Annual Costs: £{annual_other_annual_costs}")
    #print(f"  - Maintenance: £{annual_maintenance}")
    #print(f"Total Annual Expenses: £{total_annual_expenses}")
    #print(f"Annual Operating Income: £{annual_operating_income}")
    #print(f"Total Annual Mortgage Payments: £{total_annual_mortgage_payments}")

    if total_annual_mortgage_payments > 0:
        dscr = annual_operating_income / total_annual_mortgage_payments
        #print(f"DSCR: {dscr}")
    else:
        dscr = None  # Not applicable if no mortgage payments
        #print(f"DSCR: Not applicable (no mortgage payments)")
    #print(f"============================================")


    # Opex Load
    if annual_gross_rent > 0:
        opex_load = (total_monthly_expenses * 12) / annual_gross_rent * 100
    else:
        opex_load = None  # Not applicable if no gross rent

    # NRAT will be calculated after cashflow projection using Year 1 figures
    # This is a placeholder - actual calculation happens after cashflow projection
    nrat_result = None
    nrat_percentage = 0

    ## CASHFLOWS ##
    # Annual Cash Flow with Mortgage Payment Breakdown and Tax Corkscrew
    cashflow_projection = []
    remaining_balance = property_obj.outstanding_mortgage_balance if property_obj.has_mortgage else Decimal('0')
    tax_loss_carryforward = Decimal('0')  # Initialize tax loss carryforward balance
    
    # Calculate fixed monthly payment for principal & interest mortgages (stays constant throughout loan)
    fixed_monthly_payment = Decimal('0')
    if property_obj.has_mortgage and property_obj.mortgage_type == 'principal_and_interest' and property_obj.mortgage_interest_rate and property_obj.mortgage_years_remaining:
        monthly_interest_rate = property_obj.mortgage_interest_rate / Decimal('100') / Decimal('12')
        total_payments = property_obj.mortgage_years_remaining * 12
        P = property_obj.outstanding_mortgage_balance
        r = float(monthly_interest_rate)
        n = total_payments
        
        if r > 0:
            fixed_monthly_payment = Decimal(str(float(P) * (r * (1 + r) ** n) / ((1 + r) ** n - 1)))
        else:
            fixed_monthly_payment = P / Decimal(str(n))
    
    for year in range(1, 11):
        # Year 1 = current year (no growth), growth starts from Year 2
        if year == 1:
            projected_rent = annual_rent
        else:
            projected_rent = annual_rent * ((1 + rental_growth_rate) ** (year - 1))
        
        projected_vacancy_loss = projected_rent * vacancy_rate
        projected_gross_rent = projected_rent - projected_vacancy_loss

        projected_property_management_fees = projected_gross_rent * (property_obj.property_management_fees / 100)
        
        # Service charge and other costs increase by inflation, ground rent stays fixed
        if year == 1:
            projected_service_charge = property_obj.service_charge
            projected_other_annual_costs = property_obj.other_annual_costs
        else:
            projected_service_charge = property_obj.service_charge * ((1 + inflation_rate) ** (year - 1))
            projected_other_annual_costs = property_obj.other_annual_costs * ((1 + inflation_rate) ** (year - 1))
        
        projected_ground_rent = property_obj.ground_rent  # Always fixed
        projected_maintenance = projected_gross_rent * maintenance_rate

        projected_total_expenses = (projected_property_management_fees + projected_service_charge +
                                   projected_ground_rent + projected_other_annual_costs + projected_maintenance)

        # Calculate annual mortgage payments and breakdown
        annual_interest_payment = Decimal('0')
        annual_principal_payment = Decimal('0')
        annual_total_mortgage_payment = Decimal('0')
        
        if property_obj.has_mortgage and remaining_balance > 0:
            if property_obj.mortgage_type == 'interest_only':
                # Interest-only: same interest payment each year until loan term ends
                monthly_interest_rate = property_obj.mortgage_interest_rate / Decimal('100') / Decimal('12')
                annual_interest_payment = remaining_balance * monthly_interest_rate * 12
                annual_principal_payment = Decimal('0')
                annual_total_mortgage_payment = annual_interest_payment
                # Balance remains the same for interest-only loans
                
            elif property_obj.mortgage_type == 'principal_and_interest':
                # Calculate annual payments directly (like Excel model)
                annual_interest_rate = property_obj.mortgage_interest_rate / Decimal('100')
                years_remaining = max(0, property_obj.mortgage_years_remaining - (year - 1))
                
                if years_remaining > 0 and remaining_balance > 0:
                    # Annual interest on current balance
                    annual_interest_payment = remaining_balance * annual_interest_rate
                    
                    # Fixed annual total payment
                    annual_total_mortgage_payment = fixed_monthly_payment * 12
                    
                    # Annual principal = total payment - interest
                    annual_principal_payment = annual_total_mortgage_payment - annual_interest_payment
                    
                    # Update remaining balance for next year
                    remaining_balance = remaining_balance - annual_principal_payment
                else:
                    # Mortgage is paid off
                    annual_interest_payment = Decimal('0')
                    annual_principal_payment = Decimal('0')
                    annual_total_mortgage_payment = Decimal('0')
                    remaining_balance = Decimal('0')
        else:
            # No mortgage or no remaining balance
            annual_interest_payment = Decimal('0')
            annual_principal_payment = Decimal('0')
            annual_total_mortgage_payment = Decimal('0')

        # Calculate net cash flows
        net_operating_income = projected_gross_rent - projected_total_expenses
        net_cash_flow_before_tax = net_operating_income - annual_total_mortgage_payment
        
        # Taxable profit for company (interest is deductible, principal is not)
        company_taxable_profit = net_operating_income - annual_interest_payment
        corporate_tax = corp_tax_calculator.calculate_corporation_tax(company_taxable_profit)

        # Tax payable if owned individually (CORRECTED CALCULATION)
        # Apply inflation growth to personal income
        if year == 1:
            personal_income = property_obj.annual_income
        else:
            personal_income = property_obj.annual_income * ((1 + inflation_rate) ** (year - 1))
        
        rental_profit = net_operating_income  # Gross rental income - total operating expenses
        
        # Tax without property
        tax_result_without = tax_calculator.calculate_income_tax(personal_income)
        notional_income_tax_without_property = tax_result_without['tax_payable']
        
        # Tax with property (personal income + rental profit)
        total_income_with_property = personal_income + rental_profit
        tax_result_with = tax_calculator.calculate_income_tax(total_income_with_property)
        tax_with_property_before_relief = tax_result_with['tax_payable']
        
        # Apply 20% mortgage interest relief
        interest_rate_relief = annual_interest_payment * Decimal('0.20')
        tax_with_property_after_relief = max(0, tax_with_property_before_relief - interest_rate_relief)
        
        # Final tax payable = tax with property - tax without property
        tax_payable_on_shore_individual = tax_with_property_after_relief - notional_income_tax_without_property

        # Tax payable if owned by foreign individual (CORRECTED CALCULATION)
        # Apply inflation growth to personal income
        if year == 1:
            personal_income_offshore = property_obj.annual_income
        else:
            personal_income_offshore = property_obj.annual_income * ((1 + inflation_rate) ** (year - 1))
        
        rental_profit_offshore = net_operating_income  # Gross rental income - total operating expenses
        
        # Tax without property (offshore rates)
        notional_income_tax_without_property_offshore = offshore_tax_calculator.calculate_offshore_tax(personal_income_offshore)['tax_payable']
        
        # Tax with property (personal income + rental profit) - CORRECTED: using offshore rates for all income
        total_income_with_property_offshore = personal_income_offshore + rental_profit_offshore
        tax_with_property_before_relief_offshore = offshore_tax_calculator.calculate_offshore_tax(total_income_with_property_offshore)['tax_payable']
        
        # Apply 20% mortgage interest relief
        interest_rate_relief_offshore = annual_interest_payment * Decimal('0.20')
        tax_with_property_after_relief_offshore = max(0, tax_with_property_before_relief_offshore - interest_rate_relief_offshore)
        
        # Final tax payable = tax with property - tax without property
        tax_payable_offshore_individual = tax_with_property_after_relief_offshore - notional_income_tax_without_property_offshore

        # Determine applicable tax before carryforward adjustments
        if property_obj.ownership_status == 'company':
            gross_applicable_tax = corporate_tax
        elif property_obj.ownership_status == 'individual':
            if property_obj.uk_resident and property_obj.uk_taxfree_allowance:
                gross_applicable_tax = tax_payable_on_shore_individual
            else:
                gross_applicable_tax = tax_payable_offshore_individual
        else:
            # Fallback for any other ownership status
            gross_applicable_tax = Decimal('0')

        # Apply tax corkscrew logic
        if gross_applicable_tax < 0:
            # Tax loss - add to carryforward balance and set current tax to 0
            tax_loss_carryforward += abs(gross_applicable_tax)
            applicable_tax = Decimal('0')
            tax_loss_utilized = Decimal('0')
        elif gross_applicable_tax > 0 and tax_loss_carryforward > 0:
            # Positive tax - use carryforward to offset
            if tax_loss_carryforward >= gross_applicable_tax:
                # Sufficient carryforward to cover all tax
                tax_loss_utilized = gross_applicable_tax
                applicable_tax = Decimal('0')
                tax_loss_carryforward -= gross_applicable_tax
            else:
                # Partial offset - use all remaining carryforward
                tax_loss_utilized = tax_loss_carryforward
                applicable_tax = gross_applicable_tax - tax_loss_carryforward
                tax_loss_carryforward = Decimal('0')
        else:
            # Positive tax with no carryforward
            applicable_tax = gross_applicable_tax
            tax_loss_utilized = Decimal('0')

        # Calculate net cash flow after tax
        net_cash_flow_after_tax = net_cash_flow_before_tax - applicable_tax

        # Net income for tax purposes (excluding principal payments)
        net_income_for_tax = net_operating_income - annual_interest_payment
        
        cashflow_projection.append({
            'year': year,
            'gross_rent': projected_gross_rent,
            'total_expenses': projected_total_expenses,
            'net_operating_income': net_operating_income,
            'annual_interest_payment': annual_interest_payment,
            'annual_principal_payment': annual_principal_payment,
            'annual_total_mortgage_payment': annual_total_mortgage_payment,
            'net_cash_flow': net_cash_flow_before_tax,
            'net_income_for_tax': net_income_for_tax,
            'remaining_mortgage_balance': remaining_balance,
            'corporate_tax': corporate_tax,
            'tax_payable_on_shore_individual': tax_payable_on_shore_individual,
            'tax_payable_offshore_individual': tax_payable_offshore_individual,
            'gross_applicable_tax': gross_applicable_tax,
            'tax_loss_carryforward_beginning': tax_loss_carryforward + tax_loss_utilized - (abs(gross_applicable_tax) if gross_applicable_tax < 0 else 0),
            'tax_loss_generated': abs(gross_applicable_tax) if gross_applicable_tax < 0 else Decimal('0'),
            'tax_loss_utilized': tax_loss_utilized,
            'tax_loss_carryforward_ending': tax_loss_carryforward,
            'applicable_tax': applicable_tax,
            'net_cash_flow_after_tax': net_cash_flow_after_tax,
        })

    # Calculate NRAT using Year 1 Net Cash Flow After Tax from cashflow projection
    if len(cashflow_projection) > 0:
        year_1_net_return_after_tax = cashflow_projection[0]['net_cash_flow_after_tax']
        nrat_result = calculate_nrat(property_obj, year_1_net_return_after_tax)
        nrat_percentage = float(nrat_result['nrat'])
        print(f"=== NRAT CALCULATION COMPLETED ===")
        print(f"Year 1 Net Return After Tax: £{year_1_net_return_after_tax}")
        print(f"NRAT Result: {nrat_percentage:.2f}%")
        print(f"====================================")
    else:
        nrat_result = {'nrat': 0, 'sdlt_amount': 0, 'total_cash_deployed': 0}
        nrat_percentage = 0

    # CAPITAL GROWTH CALCULATIONS
    print("\n" + "="*60)
    print("="*60)
    
    # Constants for capital growth calculations
    agency_fees_rate = Decimal('0.015')  # 1.5% agency fees
    legal_fees_base = Decimal('1500')    # £1,500 legal fees (base year)
    
    # Apply 10 years of inflation to legal fees (costs incurred at sale)
    legal_fees_rate = legal_fees_base * ((1 + inflation_rate) ** 10)
    
    # Calculate EPC upgrade cost based on current EPC rating
    epc_rating = property_obj.epc_rating
    if epc_rating in ['A', 'B', 'C']:
        epc_upgrade_cost = Decimal('0')      # No upgrade needed for A, B, C ratings
    elif epc_rating == 'D':
        epc_upgrade_cost = Decimal('10000')  # £10,000 for D rating
    elif epc_rating == 'E':
        epc_upgrade_cost = Decimal('20000')  # £20,000 for E rating
    elif epc_rating == 'F':
        epc_upgrade_cost = Decimal('30000')  # £30,000 for F rating
    elif epc_rating == 'G':
        epc_upgrade_cost = Decimal('50000')  # £50,000 for G rating
    else:
        epc_upgrade_cost = Decimal('0')      # Default to £0 if EPC rating not set     

    # Use estimated_market_value as current_value for calculations
    current_value = estimated_market_value
    
    # Calculate cumulative principal payments for principal & interest mortgages
    total_principal_paid = Decimal('0')
    if property_obj.has_mortgage and property_obj.mortgage_type == 'principal_and_interest':
        total_principal_paid = sum(projection['annual_principal_payment'] for projection in cashflow_projection)
    
    # Calculate notional equity early for use in debug and calculations
    # For P&I mortgages, add principal payments made over cashflow period to increase equity
    notional_equity = current_value - Decimal(str(float(property_obj.outstanding_mortgage_balance or 0))) + total_principal_paid
    
    # Calculate total returns (10-year net cash flow + capital growth) - moved above for use in annual return calculations
    ten_year_total_cashflow = sum(projection['net_cash_flow_after_tax'] for projection in cashflow_projection)
    
    # FORECAST CAPITAL GROWTH (0% growth)
    print("--- 0% GROWTH SCENARIO ---")
    
    # Calculate Net Capital Growth for 0% growth scenario
    # With 0% growth, there's no capital appreciation, so net capital growth = negative selling costs
    future_value_no_growth = current_value  # No growth
    agency_fees_no_growth = future_value_no_growth * agency_fees_rate
    total_selling_costs_no_growth = agency_fees_no_growth + legal_fees_rate + epc_upgrade_cost
    net_capital_growth_no_growth = -total_selling_costs_no_growth  # Simply negative selling costs
    
    print(f"  Net Capital Growth Calculation (0% Growth):")
    print(f"    - Future Value: £{future_value_no_growth} (no growth)")
    print(f"    - Total Selling Costs: £{total_selling_costs_no_growth}")
    print(f"    - Net Capital Growth: -£{total_selling_costs_no_growth} (cost of selling with no appreciation)")
    
    # Calculate CGT for 0% growth scenario
    if net_capital_growth_no_growth <= 0:
        # No CGT on losses
        cgt_payable_no_growth = 0
        net_capital_growth_after_cgt_no_growth = net_capital_growth_no_growth
        print(f"    - CGT: £0 (no CGT on losses)")
    else:
        # Calculate CGT based on ownership
        if property_obj.ownership_status == 'company':
            cgt_payable_no_growth = corp_tax_calculator.calculate_corporation_tax(net_capital_growth_no_growth)
            print(f"    - CGT (Corporation Tax): £{cgt_payable_no_growth}")
        else:
            # Individual ownership - check CGT bands
            # Get year 10 cashflow income for CGT band calculation
            year_10_cashflow = cashflow_projection[9]['net_cash_flow_after_tax'] if len(cashflow_projection) >= 10 else 0
            total_gains_and_income = net_capital_growth_no_growth + year_10_cashflow
            
            if total_gains_and_income > 50270:
                cgt_rate = Decimal('0.24')  # 24% higher rate
                print(f"    - Total gains + Year 10 income: £{total_gains_and_income} > £50,270")
                print(f"    - CGT Rate: 24% (higher rate)")
            else:
                cgt_rate = Decimal('0.18')  # 18% basic rate
                print(f"    - Total gains + Year 10 income: £{total_gains_and_income} ≤ £50,270")
                print(f"    - CGT Rate: 18% (basic rate)")
            
            cgt_payable_no_growth = net_capital_growth_no_growth * cgt_rate
            print(f"    - CGT: £{cgt_payable_no_growth}")
        
        net_capital_growth_after_cgt_no_growth = net_capital_growth_no_growth - cgt_payable_no_growth
    
    print(f"    - Net Capital Growth (after CGT): £{net_capital_growth_after_cgt_no_growth}")
    
    # Create result dictionary for 0% growth
    cgt_result_no_growth = {
        'future_value': float(future_value_no_growth),
        'gross_gain': float(net_capital_growth_no_growth),
        'cgt_payable': float(cgt_payable_no_growth),
        'net_gain_after_cgt': float(net_capital_growth_after_cgt_no_growth),
        'selling_costs': float(total_selling_costs_no_growth)
    }
    
    no_growth_value = Decimal(str(cgt_result_no_growth['net_gain_after_cgt']))
    
    # For investment summary display - show net gain after CGT (same as capital growth analysis final values)
    no_growth_capital_growth_display = no_growth_value  # Net gain after CGT

    # Calculate no growth return rate
    if notional_equity and notional_equity != 0:
        no_growth_return_rate = float((no_growth_value / notional_equity) * 100)
        # Calculate annual capital growth return rate for capital growth table
        no_growth_annual_capital_return_rate = float((float(no_growth_value) / float(notional_equity)) / 10 * 100)
        # Calculate average annual return rate for conclusion table (total return including income + capital)
        no_growth_total_return = float(ten_year_total_cashflow + no_growth_value)
        no_growth_annual_return_rate = float((no_growth_total_return / float(notional_equity)) / 10 * 100)
        
        print(f"    - Capital return rate (10-year): {no_growth_return_rate:.2f}%")
        print(f"    - Annual capital return rate: {no_growth_annual_capital_return_rate:.2f}%")
        print(f"    - Total return (cashflow + capital): £{no_growth_total_return}")
        print(f"    - Annual total return rate: {no_growth_annual_return_rate:.2f}%")
    else:
        no_growth_return_rate = 0
        no_growth_annual_capital_return_rate = 0
        no_growth_annual_return_rate = 0
        print(f"    - Cannot calculate returns: Notional equity is zero")

    # FORECAST CAPITAL GROWTH (1.7%)
    print("\n--- 1.7% GROWTH SCENARIO ---")
    
    # Calculate Net Capital Growth for 1.7% growth scenario
    future_value_moderate_growth = current_value * ((Decimal('1.017')) ** 10)
    agency_fees_moderate_growth = future_value_moderate_growth * agency_fees_rate
    total_selling_costs_moderate_growth = agency_fees_moderate_growth + legal_fees_rate + epc_upgrade_cost
    net_capital_growth_moderate = future_value_moderate_growth - current_value - total_selling_costs_moderate_growth
    
    print(f"  Future Value (1.7% growth): £{future_value_moderate_growth}")
    print(f"  Net Capital Growth Calculation:")
    print(f"    - Future Value: £{future_value_moderate_growth}")
    print(f"    - Current Value: £{current_value}")
    print(f"    - Total Selling Costs: £{total_selling_costs_moderate_growth}")
    print(f"    - Net Capital Growth: £{net_capital_growth_moderate}")
    
    # Calculate CGT for 1.7% growth scenario
    if net_capital_growth_moderate <= 0:
        # No CGT on losses
        cgt_payable_moderate_growth = 0
        net_capital_growth_after_cgt_moderate = net_capital_growth_moderate
        print(f"    - CGT: £0 (no CGT on losses)")
    else:
        # Calculate CGT based on ownership
        if property_obj.ownership_status == 'company':
            cgt_payable_moderate_growth = corp_tax_calculator.calculate_corporation_tax(net_capital_growth_moderate)
            print(f"    - CGT (Corporation Tax): £{cgt_payable_moderate_growth}")
        else:
            # Individual ownership - check CGT bands
            # Get year 10 cashflow income for CGT band calculation
            year_10_cashflow = cashflow_projection[9]['net_cash_flow_after_tax'] if len(cashflow_projection) >= 10 else 0
            total_gains_and_income = net_capital_growth_moderate + year_10_cashflow
            
            if total_gains_and_income > 50270:
                cgt_rate = Decimal('0.24')  # 24% higher rate
                print(f"    - Total gains + Year 10 income: £{total_gains_and_income} > £50,270")
                print(f"    - CGT Rate: 24% (higher rate)")
            else:
                cgt_rate = Decimal('0.18')  # 18% basic rate
                print(f"    - Total gains + Year 10 income: £{total_gains_and_income} ≤ £50,270")
                print(f"    - CGT Rate: 18% (basic rate)")
            
            cgt_payable_moderate_growth = net_capital_growth_moderate * cgt_rate
            print(f"    - CGT: £{cgt_payable_moderate_growth}")
        
        net_capital_growth_after_cgt_moderate = net_capital_growth_moderate - cgt_payable_moderate_growth
    
    print(f"    - Net Capital Growth (after CGT): £{net_capital_growth_after_cgt_moderate}")

    # Create result dictionary for 1.7% growth
    cgt_result_moderate = {
        'future_value': float(future_value_moderate_growth),
        'gross_gain': float(net_capital_growth_moderate),
        'cgt_payable': float(cgt_payable_moderate_growth),
        'net_gain_after_cgt': float(net_capital_growth_after_cgt_moderate),
        'selling_costs': float(total_selling_costs_moderate_growth)
    }
    
    moderate_growth_value = Decimal(str(cgt_result_moderate['net_gain_after_cgt']))
    
    # For investment summary display - show net gain after CGT (same as capital growth analysis final values)
    moderate_growth_capital_growth_display = moderate_growth_value  # Net gain after CGT

    # Calculate 1.7% growth return rate
    if notional_equity and notional_equity != 0:
        moderate_growth_return_rate = float((moderate_growth_value / notional_equity) * 100)
        # Calculate annual capital growth return rate for capital growth table
        moderate_growth_annual_capital_return_rate = float((float(moderate_growth_value) / float(notional_equity)) / 10 * 100)
        # Calculate average annual return rate for conclusion table (total return including income + capital)
        moderate_growth_total_return = float(ten_year_total_cashflow + moderate_growth_value)
        moderate_growth_annual_return_rate = float((moderate_growth_total_return / float(notional_equity)) / 10 * 100)
        
        print(f"  Return Rate Calculations:")
        print(f"    - Net gain after CGT: £{moderate_growth_value}")
        print(f"    - Capital return rate (10-year): {moderate_growth_return_rate:.2f}%")
        print(f"    - Annual capital return rate: {moderate_growth_annual_capital_return_rate:.2f}%")
        print(f"    - Total return (cashflow + capital): £{moderate_growth_total_return}")
        print(f"    - Annual total return rate: {moderate_growth_annual_return_rate:.2f}%")
    else:
        moderate_growth_return_rate = 0
        moderate_growth_annual_capital_return_rate = 0
        moderate_growth_annual_return_rate = 0
        print(f"    - Cannot calculate returns: Notional equity is zero")

    # FORECAST CAPITAL GROWTH (3.4% annual)
    print("\n--- 3.4% GROWTH SCENARIO ---")
    
    # Calculate Net Capital Growth for 3.4% growth scenario
    future_value_average_growth = current_value * ((Decimal('1.034')) ** 10)
    agency_fees_average_growth = future_value_average_growth * agency_fees_rate
    total_selling_costs_average_growth = agency_fees_average_growth + legal_fees_rate + epc_upgrade_cost
    net_capital_growth_average = future_value_average_growth - current_value - total_selling_costs_average_growth
    
    print(f"  Future Value (3.4% growth): £{future_value_average_growth}")
    print(f"  Net Capital Growth Calculation:")
    print(f"    - Future Value: £{future_value_average_growth}")
    print(f"    - Current Value: £{current_value}")
    print(f"    - Total Selling Costs: £{total_selling_costs_average_growth}")
    print(f"    - Net Capital Growth: £{net_capital_growth_average}")
    
    # Calculate CGT for 3.4% growth scenario
    if net_capital_growth_average <= 0:
        # No CGT on losses
        cgt_payable_average_growth = 0
        net_capital_growth_after_cgt_average = net_capital_growth_average
        print(f"    - CGT: £0 (no CGT on losses)")
    else:
        # Calculate CGT based on ownership
        if property_obj.ownership_status == 'company':
            cgt_payable_average_growth = corp_tax_calculator.calculate_corporation_tax(net_capital_growth_average)
            print(f"    - CGT (Corporation Tax): £{cgt_payable_average_growth}")
        else:
            # Individual ownership - check CGT bands
            # Get year 10 cashflow income for CGT band calculation
            year_10_cashflow = cashflow_projection[9]['net_cash_flow_after_tax'] if len(cashflow_projection) >= 10 else 0
            total_gains_and_income = net_capital_growth_average + year_10_cashflow
            
            if total_gains_and_income > 50270:
                cgt_rate = Decimal('0.24')  # 24% higher rate
                print(f"    - Total gains + Year 10 income: £{total_gains_and_income} > £50,270")
                print(f"    - CGT Rate: 24% (higher rate)")
            else:
                cgt_rate = Decimal('0.18')  # 18% basic rate
                print(f"    - Total gains + Year 10 income: £{total_gains_and_income} ≤ £50,270")
                print(f"    - CGT Rate: 18% (basic rate)")
            
            cgt_payable_average_growth = net_capital_growth_average * cgt_rate
            print(f"    - CGT: £{cgt_payable_average_growth}")
        
        net_capital_growth_after_cgt_average = net_capital_growth_average - cgt_payable_average_growth
    
    print(f"    - Net Capital Growth (after CGT): £{net_capital_growth_after_cgt_average}")

    # Create result dictionary for 3.4% growth
    cgt_result_average = {
        'future_value': float(future_value_average_growth),
        'gross_gain': float(net_capital_growth_average),
        'cgt_payable': float(cgt_payable_average_growth),
        'net_gain_after_cgt': float(net_capital_growth_after_cgt_average),
        'selling_costs': float(total_selling_costs_average_growth)
    }
    
    average_growth_value = Decimal(str(cgt_result_average['net_gain_after_cgt']))
    
    # For investment summary display - show net gain after CGT (same as capital growth analysis final values)
    average_growth_capital_growth_display = average_growth_value  # Net gain after CGT

    # Calculate 3.4% growth return rate
    if notional_equity and notional_equity != 0:
        average_growth_return_rate = float((average_growth_value / notional_equity) * 100)
        # Calculate annual capital growth return rate for capital growth table
        average_growth_annual_capital_return_rate = float((float(average_growth_value) / float(notional_equity)) / 10 * 100)
        # Calculate average annual return rate for conclusion table (total return including income + capital)
        average_growth_total_return = float(ten_year_total_cashflow + average_growth_value)
        average_growth_annual_return_rate = float((average_growth_total_return / float(notional_equity)) / 10 * 100)
        
        print(f"  Return Rate Calculations:")
        print(f"    - Net gain after CGT: £{average_growth_value}")
        print(f"    - Capital return rate (10-year): {average_growth_return_rate:.2f}%")
        print(f"    - Annual capital return rate: {average_growth_annual_capital_return_rate:.2f}%")
        print(f"    - Total return (cashflow + capital): £{average_growth_total_return}")
        print(f"    - Annual total return rate: {average_growth_annual_return_rate:.2f}%")
    else:
        average_growth_return_rate = 0
        average_growth_annual_capital_return_rate = 0
        average_growth_annual_return_rate = 0
        print(f"    - Cannot calculate returns: Notional equity is zero")

    print("\n--- CAPITAL GROWTH SUMMARY ---")
    print("SCENARIO COMPARISON:")
    print(f"  0% Growth   - Net Gain: £{no_growth_value:,.2f} | Capital Return: {no_growth_annual_capital_return_rate:.2f}%/yr | Total Return: {no_growth_annual_return_rate:.2f}%/yr")
    print(f"  1.7% Growth - Net Gain: £{moderate_growth_value:,.2f} | Capital Return: {moderate_growth_annual_capital_return_rate:.2f}%/yr | Total Return: {moderate_growth_annual_return_rate:.2f}%/yr")
    print(f"  3.4% Growth - Net Gain: £{average_growth_value:,.2f} | Capital Return: {average_growth_annual_capital_return_rate:.2f}%/yr | Total Return: {average_growth_annual_return_rate:.2f}%/yr")
    print("="*60)
    
    # Add calculated fields to property object for template compatibility
    property_obj.address = property_obj.full_address  # Add address alias for template
    property_obj.no_growth_value = float(no_growth_value)
    property_obj.moderate_growth_value = float(moderate_growth_value)
    property_obj.average_growth_value = float(average_growth_value)
    property_obj.notional_equity = float(notional_equity)
    property_obj.no_growth_return_rate = no_growth_return_rate
    property_obj.moderate_growth_return_rate = moderate_growth_return_rate
    property_obj.average_growth_return_rate = average_growth_return_rate
    property_obj.no_growth_total_return = no_growth_total_return
    property_obj.moderate_growth_total_return = moderate_growth_total_return
    property_obj.average_growth_total_return = average_growth_total_return

    # Risk Analysis - Placeholder for future implementation
    Tenant_Dispute_Total = (monthly_mortgage_payment * 18) + 1500  # 18 months mortgage + legal fees
    Tenant_Dispute_monthly = Tenant_Dispute_Total / 18
    RRB_rent_recovery = property_obj.weekly_rent * 104  # 1 month rent as buffer

    # Calculate financial metrics
    annual_management_fees = (property_obj.annual_rent * property_obj.property_management_fees) / 100
    total_fixed_expenses = property_obj.service_charge + property_obj.ground_rent + property_obj.other_annual_costs
    total_annual_expenses = annual_management_fees + total_fixed_expenses
    net_annual_income = property_obj.annual_rent - total_annual_expenses
    
    # Calculate equity if property has mortgage
    equity_amount = 0
    equity_percentage = 100
    mortgage_percentage = 0
    
    if property_obj.has_mortgage and property_obj.estimated_market_value:
        equity_amount = property_obj.estimated_market_value - property_obj.outstanding_mortgage_balance
        mortgage_percentage = (property_obj.outstanding_mortgage_balance / property_obj.estimated_market_value) * 100
        equity_percentage = 100 - mortgage_percentage
    elif property_obj.estimated_market_value:
        equity_amount = property_obj.estimated_market_value

    context = {
        'property': property_obj,
        'page_title': f'{property_obj.property_name} Details',
        
        # HERO GRID FINANCIAL METRICS
        'capital_appreciation': capital_appreciation,
        'net_monthly_income': net_monthly_income,
        'gross_annual_yield': gross_annual_yield,
        'net_annual_yield': net_annual_yield,

        # Annual calculations
        'dscr': dscr,
        'opex_load': opex_load,

        'annual_management_fees': annual_management_fees,
        'total_fixed_expenses': total_fixed_expenses,
        'total_annual_expenses': total_annual_expenses,
        'net_annual_income': net_annual_income,
        
        # Equity calculations
        'equity_amount': equity_amount,
        'equity_percentage': equity_percentage,
        'mortgage_percentage': mortgage_percentage,
        
        # Monthly calculations
        'monthly_gross_income': monthly_gross_income,
        'monthly_mortgage_payment': monthly_mortgage_payment,
        'monthly_interest_payment': monthly_interest_payment,
        'monthly_principal_payment': monthly_principal_payment,
        'net_monthly_cash_flow': net_monthly_cash_flow,
        'total_monthly_expenses': total_monthly_expenses,
        'monthly_property_management_fees': monthly_property_management_fees,
        'monthly_maintenance': monthly_maintenance,
        'annual_vacancy_loss': annual_vacancy_loss,
        'annual_gross_rent': annual_gross_rent,
        
        # Cash flow projections
        'cashflow_projection': cashflow_projection,
        
        # Calculate 10-year total net income after tax
        'total_net_income_after_tax': sum(projection['net_cash_flow_after_tax'] for projection in cashflow_projection),
        
        # Capital Growth Analysis
        'no_growth_value': no_growth_value,
        'moderate_growth_value': moderate_growth_value,
        'average_growth_value': average_growth_value,
        
        # Capital Growth Display Values (actual growth before selling costs)
        'no_growth_capital_growth_display': no_growth_capital_growth_display,
        'moderate_growth_capital_growth_display': moderate_growth_capital_growth_display,
        'average_growth_capital_growth_display': average_growth_capital_growth_display,
        'no_growth_return_rate': no_growth_return_rate,
        'moderate_growth_return_rate': moderate_growth_return_rate,
        'average_growth_return_rate': average_growth_return_rate,
        'no_growth_total_return': no_growth_total_return,
        'moderate_growth_total_return': moderate_growth_total_return,
        'average_growth_total_return': average_growth_total_return,
        'no_growth_annual_return_rate': no_growth_annual_return_rate,
        'moderate_growth_annual_return_rate': moderate_growth_annual_return_rate,
        'average_growth_annual_return_rate': average_growth_annual_return_rate,
        'no_growth_annual_capital_return_rate': no_growth_annual_capital_return_rate,
        'moderate_growth_annual_capital_return_rate': moderate_growth_annual_capital_return_rate,
        'average_growth_annual_capital_return_rate': average_growth_annual_capital_return_rate,
        'notional_equity': notional_equity,
        
        # CGT Analysis Results
        'cgt_no_growth': cgt_result_no_growth,
        'cgt_moderate_growth': cgt_result_moderate,
        'cgt_average_growth': cgt_result_average,

        # Risk Analysis
        'Tenant_Dispute_Total': Tenant_Dispute_Total,
        'Tenant_Dispute_monthly': Tenant_Dispute_monthly,
        'RRB_rent_recovery': RRB_rent_recovery,

        'nrat_percentage': nrat_percentage,
    }
    return render(request, 'user_home/property_detail.html', context)

@login_required
def property_list(request):
    """View for listing all user's properties"""
    properties = Property.objects.filter(owner=request.user)
    
    context = {
        'properties': properties,
        'page_title': 'My Properties',
    }
    return render(request, 'user_home/property_list.html', context)

@login_required
def edit_property(request, slug):
    """View for editing property details"""
    property_obj = get_object_or_404(Property, slug=slug, owner=request.user)
    
    if request.method == 'POST':
        #print(f"DEBUG: Edit property POST data: {request.POST}")
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        #print(f"DEBUG: Form is valid: {form.is_valid()}")
        if not form.is_valid():
            #print(f"DEBUG: Form errors: {form.errors}")
            pass
        if form.is_valid():
            form.save()
            messages.success(request, f'Property "{property_obj.property_name}" has been updated successfully!')
            return redirect('user_home:property_detail', slug=property_obj.slug)
    else:
        form = PropertyForm(instance=property_obj)
    
    context = {
        'form': form,
        'property': property_obj,
        'page_title': f'Edit {property_obj.property_name}',
    }
    return render(request, 'user_home/edit_property.html', context)

@login_required
def profile_overview(request):
    """User profile overview page"""
    context = {
        'user': request.user,
        'profile': getattr(request.user, 'profile', None),
        'page_title': 'Profile Overview',
    }
    return render(request, 'user_home/profile_overview.html', context)

@login_required
def email_deal_analysis_pdf(request):
    """Send deal analysis report as PDF via email"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
    try:
        from django.core.mail import EmailMultiAlternatives
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        from datetime import datetime
        import io
        
        # Get the deal analysis data from session
        analysis_data = request.session.get('deal_analysis_context')
        if not analysis_data:
            return JsonResponse({'success': False, 'error': 'No analysis data found. Please run the analysis again.'}, status=400)
        
        user_email = request.user.email
        if not user_email:
            return JsonResponse({'success': False, 'error': 'No email address found for your account'}, status=400)
        
        # Parse request body for deal name
        try:
            data = json.loads(request.body)
            deal_name = data.get('deal_name', analysis_data['deal_data'].get('deal_name', 'Investment Deal'))
        except:
            deal_name = analysis_data['deal_data'].get('deal_name', 'Investment Deal')
        
        # Prepare PDF context
        pdf_context = analysis_data
        
        # Generate PDF using ReportLab
        pdf_file = io.BytesIO()
        doc = SimpleDocTemplate(pdf_file, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        
        # Container for PDF elements
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#1e40af'), spaceAfter=30, alignment=TA_CENTER)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor('#1e40af'), spaceAfter=12, spaceBefore=12)
        normal_style = styles['Normal']
        
        # Title
        elements.append(Paragraph("LEXIT", title_style))
        elements.append(Paragraph("Property Investment Analysis Report", ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, textColor=colors.HexColor('#3b82f6'), alignment=TA_CENTER, spaceAfter=10)))
        elements.append(Paragraph(f"<b>{deal_name}</b>", ParagraphStyle('DealName', parent=styles['Normal'], fontSize=14, alignment=TA_CENTER, spaceAfter=20)))
        elements.append(Spacer(1, 12))
        
        # Total Cash Required (Highlight Box)
        elements.append(Paragraph("Total Cash Required", heading_style))
        cash_data = [[f"£{analysis_data['metrics']['total_cash_deployed']:,.0f}"]]
        cash_table = Table(cash_data, colWidths=[6*inch])
        cash_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1e40af')),
        ]))
        elements.append(cash_table)
        elements.append(Spacer(1, 12))
        
        # Cash Breakdown
        breakdown_data = [
            ['Deposit', 'SDLT/Land Tax', 'Acquisition Costs'],
            [f"£{analysis_data['deal_data']['deposit_paid']:,.0f}", 
             f"£{analysis_data['metrics']['sdlt_amount']:,.0f}",
             f"£{analysis_data['metrics']['acquisition_costs']:,.0f}"]
        ]
        breakdown_table = Table(breakdown_data, colWidths=[2*inch, 2*inch, 2*inch])
        breakdown_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(breakdown_table)
        elements.append(Spacer(1, 20))
        
        # Property Details
        elements.append(Paragraph("Property Details", heading_style))
        property_data = [
            ['Property Type:', analysis_data['deal_data']['property_type'].title()],
            ['Bedrooms:', str(analysis_data['deal_data']['number_bedrooms'])],
            ['Bathrooms:', str(analysis_data['deal_data']['number_bathrooms'])],
            ['Purchase Price:', f"£{analysis_data['deal_data']['purchase_price']:,.0f}"],
            ['Current Market Value:', f"£{analysis_data['deal_data']['current_market_value']:,.0f}"],
            ['Ownership:', 'Limited Company' if analysis_data['deal_data']['ownership_status'] == 'company' else 'Individual'],
        ]
        property_table = Table(property_data, colWidths=[2.5*inch, 3.5*inch])
        property_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(property_table)
        elements.append(Spacer(1, 20))
        
        # Key Financial Metrics
        elements.append(Paragraph("Key Financial Metrics", heading_style))
        nrat = analysis_data['metrics']['nrat']
        nrat_rating = 'Excellent' if nrat >= 8 else 'Good' if nrat >= 5 else 'Poor'
        nrat_color = colors.green if nrat >= 8 else colors.orange if nrat >= 5 else colors.red
        
        metrics_data = [
            ['NRAT', f"{nrat:.1f}% ({nrat_rating})", 'Monthly Income', f"£{analysis_data['metrics']['monthly_net_income']:,.0f}"],
            ['Gross Yield', f"{analysis_data['metrics']['gross_annual_yield']:.2f}%", 'Net Yield', f"{analysis_data['metrics']['net_annual_yield']:.2f}%"],
            ['ROI', f"{analysis_data['metrics']['roi']:.2f}%", 'DSCR', f"{analysis_data['metrics']['dscr']:.2f}"],
        ]
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
        # Page Break
        elements.append(PageBreak())
        
        # 10-Year Cashflow Summary (first 5 years)
        elements.append(Paragraph("10-Year Cashflow Projection", heading_style))
        cashflow_data = [['Year', 'Gross Rent', 'Expenses', 'Mortgage', 'Tax', 'Net Cashflow']]
        for year_data in analysis_data['cashflow_projection']:
            cashflow_data.append([
                str(year_data['year']),
                f"£{year_data['gross_rent']:,.0f}",
                f"£{year_data['total_expenses']:,.0f}",
                f"£{year_data['annual_total_mortgage_payment']:,.0f}",
                f"£{year_data['applicable_tax']:,.0f}",
                f"£{year_data['net_cash_flow_after_tax']:,.0f}",
            ])
        
        cashflow_table = Table(cashflow_data, colWidths=[0.6*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch, 1.1*inch])
        cashflow_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(cashflow_table)
        elements.append(Spacer(1, 12))
        
        # 10-Year Total
        total_data = [[f"10-Year Total: £{analysis_data['ten_year_total']:,.0f}"]]
        total_table = Table(total_data, colWidths=[6*inch])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(total_table)
        elements.append(Spacer(1, 20))
        
        # Capital Growth Scenarios
        elements.append(Paragraph("Capital Growth Scenarios (10 Years)", heading_style))
        growth_data = [
            ['Scenario', 'Growth Rate', 'Future Value', 'Net Gain', 'Annual Return'],
            ['No Growth', '0.0%', 
             f"£{analysis_data['capital_growth']['no_growth_future_value']:,.0f}",
             f"£{analysis_data['capital_growth']['no_growth_net_gain']:,.0f}",
             f"{analysis_data['capital_growth']['no_growth_total_return']:.2f}%"],
            ['Moderate', '1.7%',
             f"£{analysis_data['capital_growth']['moderate_growth_future_value']:,.0f}",
             f"£{analysis_data['capital_growth']['moderate_growth_net_gain']:,.0f}",
             f"{analysis_data['capital_growth']['moderate_growth_total_return']:.2f}%"],
            ['Average', '3.4%',
             f"£{analysis_data['capital_growth']['average_growth_future_value']:,.0f}",
             f"£{analysis_data['capital_growth']['average_growth_net_gain']:,.0f}",
             f"{analysis_data['capital_growth']['average_growth_total_return']:.2f}%"],
        ]
        growth_table = Table(growth_data, colWidths=[1.2*inch, 1.1*inch, 1.3*inch, 1.3*inch, 1.2*inch])
        growth_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(growth_table)
        elements.append(Spacer(1, 20))
        
        # Footer
        elements.append(Spacer(1, 30))
        elements.append(Paragraph(f"Report generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", 
                                 ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
        elements.append(Paragraph("© LEXIT - Property Investment Analysis. This report is for informational purposes only.", 
                                 ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)))
        
        # Build PDF
        doc.build(elements)
        pdf_file.seek(0)
        
        # Email subject and message
        subject = f'LEXIT - Deal Analysis Report: {deal_name}'
        
        # Create email body (HTML)
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">LEXIT</h1>
                        <p style="color: #e0e7ff; margin: 10px 0 0 0;">Property Investment Analysis</p>
                    </div>
                    
                    <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #1e40af; margin-top: 0;">Deal Analysis Report</h2>
                        
                        <p>Dear {request.user.first_name or request.user.username},</p>
                        
                        <p>Your deal analysis report for <strong>{deal_name}</strong> has been generated and is attached to this email as a PDF.</p>
                        
                        <div style="background: white; padding: 20px; border-left: 4px solid #1e40af; margin: 20px 0;">
                            <p style="margin: 0;"><strong>Report Highlights:</strong></p>
                            <ul style="margin: 10px 0;">
                                <li>Net Return After Tax (NRAT): <strong>{analysis_data['metrics']['nrat']:.1f}%</strong></li>
                                <li>Monthly Net Income: <strong>£{analysis_data['metrics']['monthly_net_income']:,.0f}</strong></li>
                                <li>10-Year Total Return: <strong>£{analysis_data['ten_year_total']:,.0f}</strong></li>
                            </ul>
                        </div>
                        
                        <p>The attached PDF contains:</p>
                        <ul style="margin: 10px 0;">
                            <li>Complete property and financial details</li>
                            <li>10-year cashflow projection</li>
                            <li>Capital growth scenarios</li>
                            <li>Risk analysis</li>
                            <li>Investment recommendations</li>
                        </ul>
                        
                        <p>You can also view your analysis online in your LEXIT dashboard:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'}/dashboard/" 
                               style="background: #1e40af; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                View Dashboard
                            </a>
                        </div>
                        
                        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 14px;">
                            This is an automated message from LEXIT. If you have any questions, please contact our support team.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        text_message = f"""
        LEXIT - Deal Analysis Report
        
        Dear {request.user.first_name or request.user.username},
        
        Your deal analysis report for {deal_name} has been generated and is attached to this email as a PDF.
        
        Report Highlights:
        - Net Return After Tax (NRAT): {analysis_data['metrics']['nrat']:.1f}%
        - Monthly Net Income: £{analysis_data['metrics']['monthly_net_income']:,.0f}
        - 10-Year Total Return: £{analysis_data['ten_year_total']:,.0f}
        
        The attached PDF contains complete property details, 10-year cashflow projection, capital growth scenarios, risk analysis, and investment recommendations.
        
        You can also view your analysis online in your LEXIT dashboard.
        
        Best regards,
        The LEXIT Team
        """
        
        # Create email with both plain text and HTML versions
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@lexit.com',
            to=[user_email],
        )
        
        # Attach HTML version
        email.attach_alternative(html_message, "text/html")
        
        # Attach PDF
        email.attach(
            f'LEXIT_Deal_Analysis_{deal_name.replace(" ", "_")}.pdf',
            pdf_file.getvalue(),
            'application/pdf'
        )
        
        # Send email
        email.send(fail_silently=False)
        
        return JsonResponse({
            'success': True,
            'message': f'Report sent to {user_email} with PDF attachment'
        })
        
    except Exception as e:
        print(f"Error sending email with PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Failed to send email: {str(e)}'
        }, status=500)
        
        # Get the deal analysis data from session
        analysis_data = request.session.get('deal_analysis_context')
        if not analysis_data:
            return JsonResponse({'success': False, 'error': 'No analysis data found. Please run the analysis again.'}, status=400)
        
        user_email = request.user.email
        if not user_email:
            return JsonResponse({'success': False, 'error': 'No email address found for your account'}, status=400)
        
        # Parse request body for deal name
        try:
            data = json.loads(request.body)
            deal_name = data.get('deal_name', analysis_data['deal_data'].get('deal_name', 'Investment Deal'))
        except:
            deal_name = analysis_data['deal_data'].get('deal_name', 'Investment Deal')
        
        # Prepare context for PDF template
        pdf_context = {
            'deal_data': analysis_data['deal_data'],
            'monthly_gross_income': analysis_data['metrics']['monthly_gross_income'],
            'total_monthly_expenses': analysis_data['metrics']['total_monthly_expenses'],
            'monthly_mortgage_payment': analysis_data['metrics']['monthly_mortgage_payment'],
            'monthly_net_income': analysis_data['metrics']['monthly_net_income'],
            'annual_net_income': analysis_data['metrics']['annual_net_income'],
            'total_cash_invested': analysis_data['metrics']['total_cash_invested'],
            'roi': analysis_data['metrics']['roi'],
            'gross_annual_yield': analysis_data['metrics']['gross_annual_yield'],
            'net_annual_yield': analysis_data['metrics']['net_annual_yield'],
            'dscr': analysis_data['metrics']['dscr'],
            'opex_load': analysis_data['metrics']['opex_load'],
            'nrat': analysis_data['metrics']['nrat'],
            'sdlt_amount': analysis_data['metrics']['sdlt_amount'],
            'total_cash_deployed': analysis_data['metrics']['total_cash_deployed'],
            'acquisition_costs': analysis_data['metrics']['acquisition_costs'],
            'notional_equity': analysis_data['metrics']['notional_equity'],
            'cashflow_projection': analysis_data['cashflow_projection'],
            'ten_year_total': analysis_data['ten_year_total'],
            'no_growth_future_value': analysis_data['capital_growth']['no_growth_future_value'],
            'moderate_growth_future_value': analysis_data['capital_growth']['moderate_growth_future_value'],
            'average_growth_future_value': analysis_data['capital_growth']['average_growth_future_value'],
            'no_growth_net_gain': analysis_data['capital_growth']['no_growth_net_gain'],
            'moderate_growth_net_gain': analysis_data['capital_growth']['moderate_growth_net_gain'],
            'average_growth_net_gain': analysis_data['capital_growth']['average_growth_net_gain'],
            'no_growth_capital_return': analysis_data['capital_growth']['no_growth_capital_return'],
            'moderate_growth_capital_return': analysis_data['capital_growth']['moderate_growth_capital_return'],
            'average_growth_capital_return': analysis_data['capital_growth']['average_growth_capital_return'],
            'no_growth_total_return': analysis_data['capital_growth']['no_growth_total_return'],
            'moderate_growth_total_return': analysis_data['capital_growth']['moderate_growth_total_return'],
            'average_growth_total_return': analysis_data['capital_growth']['average_growth_total_return'],
            'tenant_dispute_total': analysis_data['risk_analysis']['tenant_dispute_total'],
            'tenant_dispute_monthly': analysis_data['risk_analysis']['tenant_dispute_monthly'],
            'rrb_rent_recovery': analysis_data['risk_analysis']['rrb_rent_recovery'],
            'report_date': datetime.now(),
        }
        
        # Render PDF HTML template
        html_string = render_to_string('user_home/deal_analysis_pdf.html', pdf_context)
        
        # Generate PDF using xhtml2pdf
        pdf_file = io.BytesIO()
        pisa_status = pisa.CreatePDF(html_string, dest=pdf_file)
        
        if pisa_status.err:
            return JsonResponse({
                'success': False,
                'error': 'PDF generation failed'
            }, status=500)
        
        pdf_file.seek(0)
        
        # Email subject and message
        subject = f'LEXIT - Deal Analysis Report: {deal_name}'
        
        # Create email body (HTML)
        html_message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                        <h1 style="color: white; margin: 0; font-size: 28px;">LEXIT</h1>
                        <p style="color: #e0e7ff; margin: 10px 0 0 0;">Property Investment Analysis</p>
                    </div>
                    
                    <div style="background: #f8fafc; padding: 30px; border-radius: 0 0 10px 10px;">
                        <h2 style="color: #1e40af; margin-top: 0;">Deal Analysis Report</h2>
                        
                        <p>Dear {request.user.first_name or request.user.username},</p>
                        
                        <p>Your deal analysis report for <strong>{deal_name}</strong> has been generated and is attached to this email as a PDF.</p>
                        
                        <div style="background: white; padding: 20px; border-left: 4px solid #1e40af; margin: 20px 0;">
                            <p style="margin: 0;"><strong>Report Highlights:</strong></p>
                            <ul style="margin: 10px 0;">
                                <li>Net Return After Tax (NRAT): <strong>{pdf_context['nrat']:.1f}%</strong></li>
                                <li>Monthly Net Income: <strong>£{pdf_context['monthly_net_income']:,.0f}</strong></li>
                                <li>10-Year Total Return: <strong>£{pdf_context['ten_year_total']:,.0f}</strong></li>
                            </ul>
                        </div>
                        
                        <p>The attached PDF contains:</p>
                        <ul style="margin: 10px 0;">
                            <li>Complete property and financial details</li>
                            <li>10-year cashflow projection</li>
                            <li>Capital growth scenarios</li>
                            <li>Risk analysis</li>
                            <li>Investment recommendations</li>
                        </ul>
                        
                        <p>You can also view your analysis online in your LEXIT dashboard:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://127.0.0.1:8000'}/dashboard/" 
                               style="background: #1e40af; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                                View Dashboard
                            </a>
                        </div>
                        
                        <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 14px;">
                            This is an automated message from LEXIT. If you have any questions, please contact our support team.
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Plain text version
        text_message = f"""
        LEXIT - Deal Analysis Report
        
        Dear {request.user.first_name or request.user.username},
        
        Your deal analysis report for {deal_name} has been generated and is attached to this email as a PDF.
        
        Report Highlights:
        - Net Return After Tax (NRAT): {pdf_context['nrat']:.1f}%
        - Monthly Net Income: £{pdf_context['monthly_net_income']:,.0f}
        - 10-Year Total Return: £{pdf_context['ten_year_total']:,.0f}
        
        The attached PDF contains complete property details, 10-year cashflow projection, capital growth scenarios, risk analysis, and investment recommendations.
        
        You can also view your analysis online in your LEXIT dashboard.
        
        Best regards,
        The LEXIT Team
        """
        
        # Create email with both plain text and HTML versions
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@lexit.com',
            to=[user_email],
        )
        
        # Attach HTML version
        email.attach_alternative(html_message, "text/html")
        
        # Attach PDF
        email.attach(
            f'LEXIT_Deal_Analysis_{deal_name.replace(" ", "_")}.pdf',
            pdf_file.getvalue(),
            'application/pdf'
        )
        
        # Send email
        email.send(fail_silently=False)
        
        return JsonResponse({
            'success': True,
            'message': f'Report sent to {user_email} with PDF attachment'
        })
        
    except Exception as e:
        print(f"Error sending email with PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Failed to send email: {str(e)}'
        }, status=500)
        return JsonResponse({
            'success': False,
            'error': f'Failed to send email: {str(e)}'
        }, status=500)