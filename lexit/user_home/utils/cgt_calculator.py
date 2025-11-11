"""
Capital Gains Tax Calculator for Property Investments

This module provides functions to calculate capital gains tax based on different ownership
structures and taxpayer categories.

Scenarios:
1. Company Ownership: Capital gains taxed as income at corporation tax rates
2. Individual Ownership: Capital gains taxed at CGT rates (18% basic rate, 24% higher rate)
"""

from decimal import Decimal


def calculate_cgt_rate_individual(annual_taxable_income, is_basic_rate_taxpayer=None):
    """
    Determine the CGT rate for individuals based on their tax bracket.
    
    Args:
        annual_taxable_income (Decimal): Total annual taxable income
        is_basic_rate_taxpayer (bool, optional): Override to specify tax bracket
    
    Returns:
        Decimal: CGT rate (0.18 for basic rate, 0.24 for higher rate)
    """
    # UK tax thresholds for 2024/25 (can be updated annually)
    BASIC_RATE_THRESHOLD = Decimal('50270')  # £50,270
    
    if is_basic_rate_taxpayer is not None:
        # Use explicit override if provided
        return Decimal('0.18') if is_basic_rate_taxpayer else Decimal('0.24')
    
    # Determine rate based on income
    if annual_taxable_income <= BASIC_RATE_THRESHOLD:
        return Decimal('0.18')  # Basic rate CGT
    else:
        return Decimal('0.24')  # Higher rate CGT


def calculate_corporation_tax_rate(profit):
    """
    Calculate corporation tax rate based on profit levels.
    
    Args:
        profit (Decimal): Annual profit
    
    Returns:
        Decimal: Corporation tax rate
    """
    # UK Corporation Tax rates for 2024/25
    SMALL_PROFITS_THRESHOLD = Decimal('50000')  # £50,000
    MAIN_RATE_THRESHOLD = Decimal('250000')     # £250,000
    
    if profit <= SMALL_PROFITS_THRESHOLD:
        return Decimal('0.19')  # Small profits rate
    elif profit <= MAIN_RATE_THRESHOLD:
        # Marginal relief applies between £50k and £250k
        return Decimal('0.25')  # Simplified - actual calculation more complex
    else:
        return Decimal('0.25')  # Main rate


def calculate_capital_gains_tax(
    sale_price,
    purchase_price,
    selling_costs=None,
    acquisition_costs=None,
    improvement_costs=None,
    ownership_type='individual',
    annual_taxable_income=None,
    is_basic_rate_taxpayer=None,
    annual_exempt_amount=None
):
    """
    Calculate capital gains tax for property disposal.
    
    Args:
        sale_price (Decimal): Gross sale price
        purchase_price (Decimal): Original purchase price
        selling_costs (Decimal, optional): Estate agent fees, legal costs, etc.
        acquisition_costs (Decimal, optional): Purchase costs (stamp duty, legal fees)
        improvement_costs (Decimal, optional): Costs of improvements to property
        ownership_type (str): 'company' or 'individual'
        annual_taxable_income (Decimal, optional): For determining CGT rate
        is_basic_rate_taxpayer (bool, optional): Override for tax bracket
        annual_exempt_amount (Decimal, optional): CGT annual exempt amount
    
    Returns:
        dict: Detailed breakdown of CGT calculation
    """
    # Convert inputs to Decimal for precision
    sale_price = Decimal(str(sale_price))
    purchase_price = Decimal(str(purchase_price))
    selling_costs = Decimal(str(selling_costs or 0))
    acquisition_costs = Decimal(str(acquisition_costs or 0))
    improvement_costs = Decimal(str(improvement_costs or 0))
    
    # Calculate total allowable costs
    total_costs = purchase_price + selling_costs + acquisition_costs + improvement_costs
    
    # Calculate gross capital gain
    gross_capital_gain = sale_price - total_costs
    
    # Initialize result dictionary
    result = {
        'sale_price': float(sale_price),
        'purchase_price': float(purchase_price),
        'selling_costs': float(selling_costs),
        'acquisition_costs': float(acquisition_costs),
        'improvement_costs': float(improvement_costs),
        'total_costs': float(total_costs),
        'gross_capital_gain': float(gross_capital_gain),
        'ownership_type': ownership_type,
        'cgt_rate': 0,
        'taxable_gain': 0,
        'cgt_liability': 0,
        'net_proceeds': 0
    }
    
    # If no gain or loss, no CGT liability
    if gross_capital_gain <= 0:
        result['net_proceeds'] = float(sale_price - selling_costs)
        return result
    
    if ownership_type == 'company':
        # Company ownership: Gains taxed as income at corporation tax rates
        corp_tax_rate = calculate_corporation_tax_rate(gross_capital_gain)
        
        result.update({
            'cgt_rate': float(corp_tax_rate),
            'taxable_gain': float(gross_capital_gain),
            'cgt_liability': float(gross_capital_gain * corp_tax_rate),
            'tax_type': 'Corporation Tax on Capital Gains'
        })
        
    else:
        # Individual ownership: CGT rates apply
        # Annual exempt amount for CGT (2024/25)
        if annual_exempt_amount is None:
            annual_exempt_amount = Decimal('3000')  # £3,000 for 2024/25
        else:
            annual_exempt_amount = Decimal(str(annual_exempt_amount))
        
        # Apply annual exempt amount
        taxable_gain = max(Decimal('0'), gross_capital_gain - annual_exempt_amount)
        
        # Determine CGT rate
        if annual_taxable_income is not None:
            annual_taxable_income = Decimal(str(annual_taxable_income))
        
        cgt_rate = calculate_cgt_rate_individual(
            annual_taxable_income or Decimal('0'),
            is_basic_rate_taxpayer
        )
        
        # Calculate CGT liability
        cgt_liability = taxable_gain * cgt_rate
        
        result.update({
            'annual_exempt_amount': float(annual_exempt_amount),
            'cgt_rate': float(cgt_rate),
            'taxable_gain': float(taxable_gain),
            'cgt_liability': float(cgt_liability),
            'tax_type': f'Capital Gains Tax ({float(cgt_rate * 100):.0f}% rate)',
            'is_basic_rate': cgt_rate == Decimal('0.18')
        })
    
    # Calculate net proceeds
    net_proceeds = sale_price - selling_costs - result['cgt_liability']
    result['net_proceeds'] = float(net_proceeds)
    
    return result


def calculate_property_disposal_scenarios(
    current_value,
    purchase_price,
    ownership_type='individual',
    annual_taxable_income=None,
    selling_costs_rate=Decimal('0.015'),  # 1.5% default
    legal_fees=Decimal('1500'),           # £1,500 default
    epc_upgrade_cost=Decimal('5000')      # £5,000 default
):
    """
    Calculate CGT scenarios for property disposal with standard assumptions.
    
    Args:
        current_value (Decimal): Current estimated market value
        purchase_price (Decimal): Original purchase price
        ownership_type (str): 'company' or 'individual'
        annual_taxable_income (Decimal, optional): For determining CGT rate
        selling_costs_rate (Decimal): Estate agent fees as percentage
        legal_fees (Decimal): Fixed legal costs
        epc_upgrade_cost (Decimal): EPC upgrade costs
    
    Returns:
        dict: CGT calculation with standard selling costs
    """
    current_value = Decimal(str(current_value))
    purchase_price = Decimal(str(purchase_price))
    
    # Calculate total selling costs
    agency_fees = current_value * selling_costs_rate
    total_selling_costs = agency_fees + legal_fees + epc_upgrade_cost
    
    # Calculate CGT
    cgt_result = calculate_capital_gains_tax(
        sale_price=current_value,
        purchase_price=purchase_price,
        selling_costs=total_selling_costs,
        ownership_type=ownership_type,
        annual_taxable_income=annual_taxable_income
    )
    
    # Add breakdown of selling costs
    cgt_result['selling_costs_breakdown'] = {
        'agency_fees': float(agency_fees),
        'legal_fees': float(legal_fees),
        'epc_upgrade_cost': float(epc_upgrade_cost),
        'agency_fees_rate': float(selling_costs_rate * 100)
    }
    
    return cgt_result


def calculate_future_cgt_scenarios(
    current_value,
    purchase_price,
    growth_rates=[0, 0.017, 0.034],  # 0%, 1.7%, 3.4%
    years=10,
    ownership_type='individual',
    annual_taxable_income=None,
    **kwargs
):
    """
    Calculate CGT for multiple future growth scenarios.
    
    Args:
        current_value (Decimal): Current estimated market value
        purchase_price (Decimal): Original purchase price
        growth_rates (list): Annual growth rates to model
        years (int): Number of years to project
        ownership_type (str): 'company' or 'individual'
        annual_taxable_income (Decimal, optional): For determining CGT rate
        **kwargs: Additional parameters for calculate_property_disposal_scenarios
    
    Returns:
        dict: CGT calculations for each growth scenario
    """
    current_value = Decimal(str(current_value))
    scenarios = {}
    
    for growth_rate in growth_rates:
        growth_rate = Decimal(str(growth_rate))
        
        # Calculate future value
        future_value = current_value * ((Decimal('1') + growth_rate) ** years)
        
        # Calculate CGT for this scenario
        cgt_result = calculate_property_disposal_scenarios(
            current_value=future_value,
            purchase_price=purchase_price,
            ownership_type=ownership_type,
            annual_taxable_income=annual_taxable_income,
            **kwargs
        )
        
        # Add scenario-specific information
        cgt_result.update({
            'growth_rate': float(growth_rate),
            'years': years,
            'future_value': float(future_value),
            'capital_appreciation': float(future_value - current_value)
        })
        
        # Create scenario label
        scenario_label = f"{float(growth_rate * 100):.1f}%_growth"
        scenarios[scenario_label] = cgt_result
    
    return scenarios


def calculate_property_cgt(sale_price, purchase_price, ownership_type='individual', annual_income=None, selling_costs_rate=0.025):
    """
    Simple function to calculate CGT for property disposal - designed for use in views.py
    Similar to how corp_tax_calculator and other tax calculators are used.
    
    Args:
        sale_price (float): Property sale price
        purchase_price (float): Original purchase price
        ownership_type (str): 'company' or 'individual'
        annual_income (float, optional): Annual income to determine CGT rate
        selling_costs_rate (float): Selling costs as percentage of sale price
    
    Returns:
        dict: Simple CGT calculation result
    """
    sale_price = Decimal(str(sale_price))
    purchase_price = Decimal(str(purchase_price))
    selling_costs = sale_price * Decimal(str(selling_costs_rate))
    
    result = calculate_capital_gains_tax(
        sale_price=sale_price,
        purchase_price=purchase_price,
        selling_costs=selling_costs,
        ownership_type=ownership_type,
        annual_taxable_income=Decimal(str(annual_income)) if annual_income else None
    )
    
    return {
        'cgt_liability': result['cgt_liability'],
        'net_proceeds': result['net_proceeds'],
        'cgt_rate': result['cgt_rate'],
        'gross_gain': result['gross_capital_gain'],
        'taxable_gain': result['taxable_gain'],
        'selling_costs': result['selling_costs']
    }


def calculate_property_cgt_with_growth(current_value, purchase_price, growth_rate, years=10, ownership_type='individual', annual_income=None):
    """
    Calculate CGT with property growth over time - for use in growth projections.
    
    Args:
        current_value (float): Current property value
        purchase_price (float): Original purchase price
        growth_rate (float): Annual growth rate (e.g., 0.034 for 3.4%)
        years (int): Number of years to project
        ownership_type (str): 'company' or 'individual'
        annual_income (float, optional): Annual income to determine CGT rate
    
    Returns:
        dict: CGT calculation for future value
    """
    current_value = Decimal(str(current_value))
    purchase_price = Decimal(str(purchase_price))
    growth_rate = Decimal(str(growth_rate))
    
    # Calculate future value
    future_value = current_value * ((Decimal('1') + growth_rate) ** years)
    
    # Standard selling costs
    agency_fees = future_value * Decimal('0.015')  # 1.5%
    legal_fees = Decimal('1500')
    epc_costs = Decimal('5000')
    total_selling_costs = agency_fees + legal_fees + epc_costs
    
    result = calculate_capital_gains_tax(
        sale_price=future_value,
        purchase_price=purchase_price,
        selling_costs=total_selling_costs,
        ownership_type=ownership_type,
        annual_taxable_income=Decimal(str(annual_income)) if annual_income else None
    )
    
    return {
        'future_value': float(future_value),
        'cgt_liability': result['cgt_liability'],
        'net_proceeds': result['net_proceeds'],
        'cgt_rate': result['cgt_rate'],
        'gross_gain': result['gross_capital_gain'],
        'net_gain_after_cgt': float(future_value - total_selling_costs - Decimal(str(result['cgt_liability'])) - current_value),
        'selling_costs': float(total_selling_costs)
    }
