from datetime import datetime
from decimal import Decimal

class IncomeTaxCalculator:
    def __init__(self):
        # Current UK tax rates and thresholds for 2024/25 tax year
        self.personal_allowance = Decimal('12570')
        self.personal_allowance_threshold = Decimal('100000')
        self.basic_rate_limit = Decimal('37700')
        self.higher_rate_limit = Decimal('125140')
        self.basic_rate = Decimal('0.20')
        self.higher_rate = Decimal('0.40')
        self.additional_rate = Decimal('0.45')
    
    def calculate_income_tax(self, income):
        """
        Calculate UK income tax based on current rates
        
        Args:
            income (float): Annual income amount
            
        Returns:
            dict: Dictionary containing tax calculation details
        """
        try:
            # Validation
            if income is None or income < 0:
                raise ValueError('Income must be a positive number')
            
            # Convert to Decimal if needed
            if not isinstance(income, Decimal):
                income = Decimal(str(income))
            
            # Calculate personal allowance (tapers after £100k)
            personal_allowance = self.personal_allowance
            if income > self.personal_allowance_threshold:
                reduction = (income - self.personal_allowance_threshold) // 2
                personal_allowance = max(Decimal('0'), self.personal_allowance - reduction)
            
            # Calculate taxable income
            taxable_income = max(Decimal('0'), income - personal_allowance)
            
            # Calculate tax in bands
            tax_payable = Decimal('0')
            breakdown = []
            
            # Basic rate band (20%)
            basic_taxable = min(taxable_income, self.basic_rate_limit)
            if basic_taxable > 0:
                basic_tax = basic_taxable * self.basic_rate
                tax_payable += basic_tax
                breakdown.append({
                    'band': f"Basic rate (£0 - £{self.basic_rate_limit:,})",
                    'taxable_amount': basic_taxable,
                    'rate': f"{self.basic_rate * 100:.0f}%",
                    'tax': basic_tax
                })
            
            # Higher rate band (40%)
            higher_taxable = max(Decimal('0'), min(taxable_income - self.basic_rate_limit, 
                                      (self.higher_rate_limit - self.basic_rate_limit)))
            if higher_taxable > 0:
                higher_tax = higher_taxable * self.higher_rate
                tax_payable += higher_tax
                breakdown.append({
                    'band': f"Higher rate (£{self.basic_rate_limit:,} - £{self.higher_rate_limit:,})",
                    'taxable_amount': higher_taxable,
                    'rate': f"{self.higher_rate * 100:.0f}%",
                    'tax': higher_tax
                })
            
            # Additional rate band (45%)
            additional_taxable = max(Decimal('0'), taxable_income - self.higher_rate_limit)
            if additional_taxable > 0:
                additional_tax = additional_taxable * self.additional_rate
                tax_payable += additional_tax
                breakdown.append({
                    'band': f"Additional rate (£{self.higher_rate_limit:,}+)",
                    'taxable_amount': additional_taxable,
                    'rate': f"{self.additional_rate * 100:.0f}%",
                    'tax': additional_tax
                })
            
            # Calculate effective rate
            effective_rate = (tax_payable / income * 100) if income > 0 else Decimal('0')
            
            return {
                'income': income,
                'personal_allowance': personal_allowance,
                'taxable_income': taxable_income,
                'tax_payable': round(tax_payable, 2),
                'net_income': round(income - tax_payable, 2),
                'effective_rate': f"{effective_rate:.2f}%",
                'breakdown': breakdown
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'tax_payable': Decimal('0')
            }

# Simple function that exactly matches your JavaScript function
def calculate_income_tax(income):
    """
    Simple function to calculate income tax - matches your JS function structure
    """
    # Convert to Decimal if needed
    if not isinstance(income, Decimal):
        income = Decimal(str(income))
        
    personal_allowance_threshold = Decimal('100000')
    personal_allowance = Decimal('12570')
    
    if income > personal_allowance_threshold:
        personal_allowance = max(Decimal('0'), Decimal('12570') - ((income - personal_allowance_threshold) // 2))
    
    taxable_income = max(Decimal('0'), income - personal_allowance)
    tax_payable = Decimal('0')
    
    basic_rate_limit = Decimal('37700')
    higher_rate_limit = Decimal('125140')
    
    # Basic rate (20%)
    basic_taxable = min(taxable_income, basic_rate_limit)
    tax_payable += basic_taxable * Decimal('0.20')
    
    # Higher rate (40%)
    higher_taxable = max(Decimal('0'), min(taxable_income - basic_rate_limit, 
                               (higher_rate_limit - basic_rate_limit)))
    tax_payable += higher_taxable * Decimal('0.40')
    
    # Additional rate (45%)
    additional_taxable = max(Decimal('0'), taxable_income - higher_rate_limit)
    tax_payable += additional_taxable * Decimal('0.45')
    
    return tax_payable

# Create a global instance
income_tax_calculator = IncomeTaxCalculator()

# https://taxfix.com/en-uk/calculator/corporation-tax-calculator/

# How to calculate corporation tax with marginal relief
# https://www.qualitycompanyformations.co.uk/blog/corporation-tax-new-rates-and-marginal-relief/