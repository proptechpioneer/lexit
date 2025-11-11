from decimal import Decimal

class CorporationTaxCalculator:
    def __init__(self):
        # UK Corporation Tax rates for 2024/25
        self.small_profits_rate = Decimal('0.19')  # 19% for profits up to £250k
        self.main_rate = Decimal('0.25')  # 25% for profits over £250k
        self.small_profits_threshold = Decimal('250000')
        self.marginal_relief_threshold = Decimal('50000')
    
    def calculate_corporation_tax(self, profits):
        """Calculate UK Corporation Tax with marginal relief"""
        # Convert to Decimal if needed
        if not isinstance(profits, Decimal):
            profits = Decimal(str(profits))
            
        if profits <= self.marginal_relief_threshold:
            return profits * self.small_profits_rate
        elif profits <= self.small_profits_threshold:
            # Apply marginal relief
            main_rate_tax = profits * self.main_rate
            marginal_relief = (self.small_profits_threshold - profits) * Decimal('0.015')
            return main_rate_tax - marginal_relief
        else:
            return profits * self.main_rate

# Change this line to match your views.py import
corp_tax_calculator = CorporationTaxCalculator()