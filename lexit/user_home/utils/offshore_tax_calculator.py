from decimal import Decimal

class OffshoreTaxCalculator:
    def __init__(self):
        # Offshore tax rates and thresholds
        self.basic_rate_limit = Decimal('37000')
        self.higher_rate_limit = Decimal('150000')
        self.basic_rate = Decimal('0.20')
        self.higher_rate = Decimal('0.40')
        self.additional_rate = Decimal('0.45')
    
    def calculate_offshore_tax(self, income):
        """
        Calculate offshore tax based on specified rates
        
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
            
            # Calculate tax in bands
            tax_payable = Decimal('0')
            breakdown = []
            
            # Basic rate band (20%) - £0 to £37,000
            basic_taxable = min(income, self.basic_rate_limit)
            if basic_taxable > 0:
                basic_tax = basic_taxable * self.basic_rate
                tax_payable += basic_tax
                breakdown.append({
                    'band': f"Basic rate (£0 - £{self.basic_rate_limit:,})",
                    'taxable_amount': basic_taxable,
                    'rate': f"{self.basic_rate * 100:.0f}%",
                    'tax': basic_tax
                })
            
            # Higher rate band (40%) - £37,001 to £150,000
            higher_taxable = max(Decimal('0'), min(income - self.basic_rate_limit, 
                                      (self.higher_rate_limit - self.basic_rate_limit)))
            if higher_taxable > 0:
                higher_tax = higher_taxable * self.higher_rate
                tax_payable += higher_tax
                breakdown.append({
                    'band': f"Higher rate (£{self.basic_rate_limit + 1:,} - £{self.higher_rate_limit:,})",
                    'taxable_amount': higher_taxable,
                    'rate': f"{self.higher_rate * 100:.0f}%",
                    'tax': higher_tax
                })
            
            # Additional rate band (45%) - £150,001+
            additional_taxable = max(Decimal('0'), income - self.higher_rate_limit)
            if additional_taxable > 0:
                additional_tax = additional_taxable * self.additional_rate
                tax_payable += additional_tax
                breakdown.append({
                    'band': f"Additional rate (£{self.higher_rate_limit + 1:,}+)",
                    'taxable_amount': additional_taxable,
                    'rate': f"{self.additional_rate * 100:.0f}%",
                    'tax': additional_tax
                })
            
            # Calculate effective rate
            effective_rate = (tax_payable / income * 100) if income > 0 else Decimal('0')
            
            return {
                'income': income,
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

# Simple function for offshore tax calculation
def calculate_offshore_tax(income):
    """
    Simple function to calculate offshore tax
    
    Tax bands:
    - £0 - £37,000: 20%
    - £37,001 - £150,000: 40%
    - £150,001+: 45%
    """
    # Convert to Decimal if needed
    if not isinstance(income, Decimal):
        income = Decimal(str(income))
        
    if income <= 0:
        return Decimal('0')
    
    tax_payable = Decimal('0')
    
    # Basic rate (20%) - up to £37,000
    basic_taxable = min(income, Decimal('37000'))
    tax_payable += basic_taxable * Decimal('0.20')
    
    # Higher rate (40%) - £37,001 to £150,000
    if income > Decimal('37000'):
        higher_taxable = min(income - Decimal('37000'), Decimal('150000') - Decimal('37000'))
        tax_payable += higher_taxable * Decimal('0.40')
    
    # Additional rate (45%) - over £150,000
    if income > Decimal('150000'):
        additional_taxable = income - Decimal('150000')
        tax_payable += additional_taxable * Decimal('0.45')
    
    return tax_payable

# Create a global instance
offshore_tax_calculator = OffshoreTaxCalculator()