from datetime import datetime
from decimal import Decimal

class SDLTCalculator:
    def __init__(self):
        # BTL (Buy-to-Let) surcharge rates by period and buyer type
        self.btl_surcharge_rates = [
            {
                'from': '1900-01-01',
                'to': '2016-03-31',
                'uk_individual': 0.00,
                'non_uk_individual': 0.00,
                'uk_company': 0.00
            },
            {
                'from': '2016-04-01',
                'to': '2020-07-07',
                'uk_individual': 0.03,
                'non_uk_individual': 0.03,
                'uk_company': 0.03
            },
            {
                'from': '2020-07-08',
                'to': '2021-06-30',
                'uk_individual': 0.03,
                'non_uk_individual': 0.03,
                'uk_company': 0.03
            },
            {
                'from': '2021-07-01',
                'to': '2021-09-30',
                'uk_individual': 0.03,
                'non_uk_individual': 0.03,
                'uk_company': 0.03
            },
            {
                'from': '2021-10-01',
                'to': '2022-09-22',
                'uk_individual': 0.03,
                'non_uk_individual': 0.05,
                'uk_company': 0.03
            },
            {
                'from': '2022-09-23',
                'to': '2025-03-31',
                'uk_individual': 0.03,
                'non_uk_individual': 0.05,
                'uk_company': 0.03
            },
            {
                'from': '2025-04-01',
                'to': '2050-12-31',
                'uk_individual': 0.05,
                'non_uk_individual': 0.07,
                'uk_company': 0.05
            }
        ]
        
        self.historic_rates = [
            {
                'from': '1900-01-01',
                'to': '1958-07-31',
                'tier': 'Tier 0',
                'thresholds': [{'limit': float('inf'), 'rate': 0}]
            },
            {
                'from': '1958-08-01',
                'to': '1963-07-31',
                'tier': 'Tier 1',
                'thresholds': [
                    {'limit': 3500, 'rate': 0},
                    {'limit': 4500, 'rate': 0.005},
                    {'limit': 5250, 'rate': 0.01},
                    {'limit': 6000, 'rate': 0.015},
                    {'limit': float('inf'), 'rate': 0.02}
                ]
            },
            {
                'from': '1963-08-01',
                'to': '1967-07-31',
                'tier': 'Tier 2',
                'thresholds': [
                    {'limit': 4500, 'rate': 0},
                    {'limit': 6000, 'rate': 0.005},
                    {'limit': float('inf'), 'rate': 0.01}
                ]
            },
            {
                'from': '1967-08-01',
                'to': '1972-07-31',
                'tier': 'Tier 3',
                'thresholds': [
                    {'limit': 5500, 'rate': 0},
                    {'limit': 7000, 'rate': 0.005},
                    {'limit': float('inf'), 'rate': 0.01}
                ]
            },
            {
                'from': '1972-08-01',
                'to': '1974-04-30',
                'tier': 'Tier 4',
                'thresholds': [
                    {'limit': 10000, 'rate': 0},
                    {'limit': 15000, 'rate': 0.005},
                    {'limit': float('inf'), 'rate': 0.01}
                ]
            },
            {
                'from': '1974-05-01',
                'to': '1980-04-05',
                'tier': 'Tier 5',
                'thresholds': [
                    {'limit': 15000, 'rate': 0},
                    {'limit': 20000, 'rate': 0.005},
                    {'limit': 25000, 'rate': 0.01},
                    {'limit': 30000, 'rate': 0.015},
                    {'limit': float('inf'), 'rate': 0.02}
                ]
            },
            {
                'from': '1980-04-06',
                'to': '1982-03-21',
                'tier': 'Tier 6',
                'thresholds': [
                    {'limit': 20000, 'rate': 0},
                    {'limit': 25000, 'rate': 0.005},
                    {'limit': 30000, 'rate': 0.01},
                    {'limit': 35000, 'rate': 0.015},
                    {'limit': float('inf'), 'rate': 0.02}
                ]
            },
            {
                'from': '1982-03-22',
                'to': '1984-03-12',
                'tier': 'Tier 7',
                'thresholds': [
                    {'limit': 25000, 'rate': 0},
                    {'limit': 30000, 'rate': 0.005},
                    {'limit': 35000, 'rate': 0.01},
                    {'limit': 40000, 'rate': 0.015},
                    {'limit': float('inf'), 'rate': 0.02}
                ]
            },
            {
                'from': '1984-03-13',
                'to': '1991-12-19',
                'tier': 'Tier 8',
                'thresholds': [
                    {'limit': 30000, 'rate': 0},
                    {'limit': float('inf'), 'rate': 0.01}
                ]
            },
            {
                'from': '1991-12-20',
                'to': '1992-08-19',
                'tier': 'Tier 9',
                'thresholds': [
                    {'limit': 250000, 'rate': 0},
                    {'limit': float('inf'), 'rate': 0.01}
                ]
            },
            {
                'from': '1992-08-20',
                'to': '1993-03-15',
                'tier': 'Tier 10',
                'thresholds': [
                    {'limit': 30000, 'rate': 0},
                    {'limit': float('inf'), 'rate': 0.01}
                ]
            },
            {
                'from': '1993-03-16',
                'to': '1997-07-07',
                'tier': 'Tier 11',
                'thresholds': [
                    {'limit': 60000, 'rate': 0},
                    {'limit': float('inf'), 'rate': 0.01}
                ]
            },
            {
                'from': '1997-07-08',
                'to': '1998-03-23',
                'tier': 'Tier 12',
                'thresholds': [
                    {'limit': 60000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.015},
                    {'limit': float('inf'), 'rate': 0.02}
                ]
            },
            {
                'from': '1998-03-24',
                'to': '1999-03-15',
                'tier': 'Tier 13',
                'thresholds': [
                    {'limit': 60000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.02},
                    {'limit': float('inf'), 'rate': 0.03}
                ]
            },
            {
                'from': '1999-03-16',
                'to': '2000-03-27',
                'tier': 'Tier 14',
                'thresholds': [
                    {'limit': 60000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.025},
                    {'limit': float('inf'), 'rate': 0.035}
                ]
            },
            {
                'from': '2000-03-28',
                'to': '2005-03-16',
                'tier': 'Tier 15',
                'thresholds': [
                    {'limit': 60000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.03},
                    {'limit': float('inf'), 'rate': 0.04}
                ]
            },
            {
                'from': '2005-03-17',
                'to': '2006-03-22',
                'tier': 'Tier 16',
                'thresholds': [
                    {'limit': 120000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.03},
                    {'limit': float('inf'), 'rate': 0.04}
                ]
            },
            {
                'from': '2006-03-23',
                'to': '2008-09-02',
                'tier': 'Tier 17',
                'thresholds': [
                    {'limit': 125000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.03},
                    {'limit': float('inf'), 'rate': 0.04}
                ]
            },
            {
                'from': '2008-09-03',
                'to': '2009-12-31',
                'tier': 'Tier 18',
                'thresholds': [
                    {'limit': 175000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.03},
                    {'limit': float('inf'), 'rate': 0.04}
                ]
            },
            {
                'from': '2010-01-01',
                'to': '2011-04-05',
                'tier': 'Tier 19',
                'thresholds': [
                    {'limit': 125000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.03},
                    {'limit': float('inf'), 'rate': 0.04}
                ]
            },
            {
                'from': '2011-04-06',
                'to': '2012-03-21',
                'tier': 'Tier 20',
                'thresholds': [
                    {'limit': 125000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.03},
                    {'limit': 1000000, 'rate': 0.04},
                    {'limit': float('inf'), 'rate': 0.05}
                ]
            },
            {
                'from': '2012-03-22',
                'to': '2014-12-02',
                'tier': 'Tier 21',
                'thresholds': [
                    {'limit': 125000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.01},
                    {'limit': 500000, 'rate': 0.03},
                    {'limit': 1000000, 'rate': 0.04},
                    {'limit': 2000000, 'rate': 0.05},
                    {'limit': float('inf'), 'rate': 0.07}
                ]
            },
            {
                'from': '2014-12-03',
                'to': '2020-07-07',
                'tier': 'Tier 22',
                'thresholds': [
                    {'limit': 125000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.02},
                    {'limit': 925000, 'rate': 0.05},
                    {'limit': 1500000, 'rate': 0.10},
                    {'limit': float('inf'), 'rate': 0.12}
                ]
            },
            {
                'from': '2020-07-08',
                'to': '2021-06-30',
                'tier': 'Tier 23',
                'thresholds': [
                    {'limit': 500000, 'rate': 0},
                    {'limit': 925000, 'rate': 0.05},
                    {'limit': 1500000, 'rate': 0.10},
                    {'limit': float('inf'), 'rate': 0.12}
                ]
            },
            {
                'from': '2021-07-01',
                'to': '2021-09-30',
                'tier': 'Tier 24',
                'thresholds': [
                    {'limit': 250000, 'rate': 0},
                    {'limit': 925000, 'rate': 0.05},
                    {'limit': 1500000, 'rate': 0.10},
                    {'limit': float('inf'), 'rate': 0.12}
                ]
            },
            {
                'from': '2021-10-01',
                'to': '2022-09-22',
                'tier': 'Tier 25',
                'thresholds': [
                    {'limit': 125000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.02},
                    {'limit': 925000, 'rate': 0.05},
                    {'limit': 1500000, 'rate': 0.10},
                    {'limit': float('inf'), 'rate': 0.12}
                ]
            },
            {
                'from': '2022-09-23',
                'to': '2025-03-31',
                'tier': 'Tier 26',
                'thresholds': [
                    {'limit': 250000, 'rate': 0},
                    {'limit': 925000, 'rate': 0.05},
                    {'limit': 1500000, 'rate': 0.10},
                    {'limit': float('inf'), 'rate': 0.12}
                ]
            },
            {
                'from': '2025-04-01',
                'to': '2050-03-31',
                'tier': 'Tier 27',
                'thresholds': [
                    {'limit': 125000, 'rate': 0},
                    {'limit': 250000, 'rate': 0.02},
                    {'limit': 925000, 'rate': 0.05},
                    {'limit': 1500000, 'rate': 0.10},
                    {'limit': float('inf'), 'rate': 0.12}
                ]
            }
        ]
        
        # Additional property (BTL) surcharge rates - tiered system for individuals
        # These are the full rates (base + 5% surcharge)
        self.btl_tiered_individual = [
            {
                'from': '2016-04-01',
                'to': '2050-12-31',
                'thresholds': [
                    {'limit': 125000, 'rate': 0.05},      # 5% on first £125k
                    {'limit': 250000, 'rate': 0.07},      # 7% on £125k-£250k
                    {'limit': 925000, 'rate': 0.10},      # 10% on £250k-£925k
                    {'limit': 1500000, 'rate': 0.15},     # 15% on £925k-£1.5m
                    {'limit': float('inf'), 'rate': 0.17} # 17% above £1.5m
                ]
            }
        ]
        
        # Company BTL rates (UK resident company)
        # For purchases ≤ £500k: banded rates with 5% surcharge
        # For purchases > £500k: flat 17%
        self.btl_tiered_company_uk = [
            {
                'from': '2016-04-01',
                'to': '2050-12-31',
                'thresholds': [
                    {'limit': 125000, 'rate': 0.05},      # 5% on first £125k
                    {'limit': 250000, 'rate': 0.07},      # 7% on £125k-£250k
                    {'limit': 925000, 'rate': 0.10},      # 10% on £250k-£925k
                    {'limit': 1500000, 'rate': 0.15},     # 15% on £925k-£1.5m
                    {'limit': float('inf'), 'rate': 0.17} # 17% above £1.5m
                ],
                'flat_rate_threshold': 500000,
                'flat_rate': 0.17
            }
        ]
        
        # Non-resident company BTL rates
        # For purchases ≤ £500k: banded rates with 5% surcharge + 2% non-resident surcharge
        # For purchases > £500k: flat 19%
        self.btl_tiered_company_non_uk = [
            {
                'from': '2016-04-01',
                'to': '2050-12-31',
                'thresholds': [
                    {'limit': 125000, 'rate': 0.07},      # 7% on first £125k (5% + 2%)
                    {'limit': 250000, 'rate': 0.09},      # 9% on £125k-£250k (7% + 2%)
                    {'limit': 925000, 'rate': 0.12},      # 12% on £250k-£925k (10% + 2%)
                    {'limit': 1500000, 'rate': 0.17},     # 17% on £925k-£1.5m (15% + 2%)
                    {'limit': float('inf'), 'rate': 0.19} # 19% above £1.5m (17% + 2%)
                ],
                'flat_rate_threshold': 500000,
                'flat_rate': 0.19
            }
        ]
    
    def find_applicable_rate_tier(self, purchase_date):
        """Find the applicable rate tier for a given date"""
        for rate_tier in self.historic_rates:
            from_date = datetime.strptime(rate_tier['from'], '%Y-%m-%d').date()
            to_date = datetime.strptime(rate_tier['to'], '%Y-%m-%d').date()
            
            if from_date <= purchase_date <= to_date:
                return rate_tier
        return None
    
    def find_btl_tiered_structure(self, purchase_date, buyer_type):
        """Find the applicable BTL tiered structure for a given date and buyer type"""
        # Determine which rate structure to use based on buyer type
        if buyer_type == 'uk_company':
            rate_structures = self.btl_tiered_company_uk
        elif buyer_type == 'non_uk_company':
            rate_structures = self.btl_tiered_company_non_uk
        else:  # uk_individual or non_uk_individual
            rate_structures = self.btl_tiered_individual
        
        for structure in rate_structures:
            from_date = datetime.strptime(structure['from'], '%Y-%m-%d').date()
            to_date = datetime.strptime(structure['to'], '%Y-%m-%d').date()
            
            if from_date <= purchase_date <= to_date:
                return structure
        return None
    
    def find_btl_surcharge_rate(self, purchase_date, buyer_type):
        """Find the applicable BTL surcharge rate for a given date and buyer type"""
        for surcharge_period in self.btl_surcharge_rates:
            from_date = datetime.strptime(surcharge_period['from'], '%Y-%m-%d').date()
            to_date = datetime.strptime(surcharge_period['to'], '%Y-%m-%d').date()
            
            if from_date <= purchase_date <= to_date:
                return surcharge_period.get(buyer_type, 0.00)
        return 0.00
    
    def calculate_sdlt(self, purchase_date, purchase_price, ownership_type='individual', buyer_type=None, is_btl=False):
        """
        Calculate SDLT with BTL surcharges based on buyer type
        
        Args:
            purchase_date: Date of purchase
            purchase_price: Purchase price of property
            ownership_type: 'individual' or 'company' (legacy support)
            buyer_type: 'uk_individual', 'non_uk_individual', 'uk_company', or 'non_uk_company'
            is_btl: Whether this is a Buy-to-Let property
        """
        try:
            # Validation
            if not purchase_date or not purchase_price:
                raise ValueError('Purchase date and price are required')
            
            if purchase_price <= 0:
                raise ValueError('Purchase price must be greater than 0')
            
            # Handle legacy ownership_type parameter and map to new buyer_type system
            if buyer_type is None:
                if ownership_type == 'individual':
                    buyer_type = 'uk_individual'  # Default to UK individual for legacy support
                elif ownership_type == 'company':
                    buyer_type = 'uk_company'  # Default to UK company for legacy support
                else:
                    raise ValueError('Invalid ownership type')
            
            # Validate buyer_type
            valid_buyer_types = ['uk_individual', 'non_uk_individual', 'uk_company', 'non_uk_company']
            if buyer_type not in valid_buyer_types:
                raise ValueError(f'Buyer type must be one of: {", ".join(valid_buyer_types)}')
            
            # Convert string date to date object if needed
            if isinstance(purchase_date, str):
                purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
            
            # Find applicable rate tier
            applicable_rate_tier = self.find_applicable_rate_tier(purchase_date)
            
            if not applicable_rate_tier:
                raise ValueError('No applicable stamp duty rates found for the given date')
            
            # Get BTL structure if applicable
            btl_structure = None
            if is_btl:
                btl_structure = self.find_btl_tiered_structure(purchase_date, buyer_type)
            
            # Calculate SDLT using tiered system
            sdlt = 0
            breakdown = []
            previous_limit = 0
            is_flat_rate = False
            
            # For BTL, check if flat rate applies (companies over £500k)
            if is_btl and btl_structure:
                # Check if flat rate applies (companies with purchase price > threshold)
                flat_rate_threshold = btl_structure.get('flat_rate_threshold')
                flat_rate = btl_structure.get('flat_rate')
                
                if (buyer_type in ['uk_company', 'non_uk_company'] and 
                    flat_rate_threshold and flat_rate and 
                    purchase_price > flat_rate_threshold):
                    # Apply flat rate on entire purchase price
                    is_flat_rate = True
                    rate = Decimal(str(flat_rate))
                    sdlt = purchase_price * rate
                    
                    breakdown.append({
                        'band': f'Entire purchase (flat rate for company > £{flat_rate_threshold:,})',
                        'taxable_amount': purchase_price,
                        'rate': f"{rate * 100:.1f}%",
                        'tax': sdlt
                    })
                else:
                    # Use BTL tiered rates
                    for threshold in btl_structure['thresholds']:
                        taxable_amount = min(purchase_price, threshold['limit']) - previous_limit
                        
                        if taxable_amount <= 0:
                            break
                        
                        rate = Decimal(str(threshold['rate']))
                        tax_on_band = taxable_amount * rate
                        sdlt += tax_on_band
                        
                        # Build description for this band
                        band_description = f"£{previous_limit:,} - £{threshold['limit']:,}" if threshold['limit'] != float('inf') else f"£{previous_limit:,} - ∞"
                        
                        breakdown.append({
                            'band': band_description,
                            'taxable_amount': taxable_amount,
                            'rate': f"{rate * 100:.1f}%",
                            'tax': tax_on_band
                        })
                        
                        previous_limit = threshold['limit']
                        
                        if purchase_price <= threshold['limit']:
                            break
            else:
                # Standard rates for non-BTL properties
                for threshold in applicable_rate_tier['thresholds']:
                    taxable_amount = min(purchase_price, threshold['limit']) - previous_limit
                    
                    if taxable_amount <= 0:
                        break
                    
                    rate = Decimal(str(threshold['rate']))
                    tax_on_band = taxable_amount * rate
                    sdlt += tax_on_band
                    
                    # Build description for this band
                    band_description = f"£{previous_limit:,} - £{threshold['limit']:,}" if threshold['limit'] != float('inf') else f"£{previous_limit:,} - ∞"
                    
                    breakdown.append({
                        'band': band_description,
                        'taxable_amount': taxable_amount,
                        'rate': f"{rate * 100:.1f}%",
                        'tax': tax_on_band
                    })
                    
                    previous_limit = threshold['limit']
                    
                    if purchase_price <= threshold['limit']:
                        break
            
            
            return {
                'sdlt': round(sdlt, 2),
                'rate_tier': applicable_rate_tier['tier'],
                'buyer_type': buyer_type,
                'is_btl': is_btl,
                'is_flat_rate': is_flat_rate,
                'breakdown': breakdown,
                'effective_rate': f"{(sdlt / purchase_price) * 100:.3f}%"
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'sdlt': 0
            }

# Create a global instance
sdlt_calculator = SDLTCalculator()